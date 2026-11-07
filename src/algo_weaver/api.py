"""Optional FastAPI surface for the CLI-first AlgoWeaver services."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal

from pydantic import BaseModel, Field

from algo_weaver.agents.reproduction_graph import build_reproduction_graph
from algo_weaver.config import Settings, get_settings
from algo_weaver.llm.factory import create_chat_model
from algo_weaver.schemas.capability import SourceType
from algo_weaver.schemas.execution import ExecutionPolicy, ExecutionResult
from algo_weaver.schemas.ingestion import IngestedSource, SourceFormat
from algo_weaver.schemas.reproduction import ReproductionBundle
from algo_weaver.services.capability_extractor import CapabilityExtractor
from algo_weaver.services.dependency import PythonDependencyAnalyzer
from algo_weaver.services.sandbox import DockerSandboxRunner, WslDockerSandboxRunner
from algo_weaver.services.template_repair import TemplateRepairer

ExecutionRunnerFactory = Callable[[str, Path], ExecutionResult]


def _template_repair_callback(
    bundle: ReproductionBundle,
    workspace: Path,
    observation: ExecutionResult,
) -> bool:
    return TemplateRepairer().repair(bundle, workspace, observation)


class ExtractRequest(BaseModel):
    source_text: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    source_type: SourceType = "document"
    source_location: str | None = None
    mode: Literal["mock", "litellm"] = "mock"


class ReproduceRequest(ExtractRequest):
    source_format: SourceFormat = "markdown"
    execute: bool = False
    backend: Literal["docker", "wsl"] = "docker"
    repair: bool = False
    max_repair_attempts: int = Field(default=2, ge=0, le=5)


def create_app(
    settings: Settings | None = None,
    execution_runner: ExecutionRunnerFactory | None = None,
):
    """Create the optional API app; importing this module does not require FastAPI."""
    try:
        from fastapi import FastAPI, HTTPException
    except ModuleNotFoundError as exc:  # pragma: no cover - depends on optional extra
        raise RuntimeError("FastAPI is required for the API extra") from exc

    active_settings = settings or get_settings()
    app = FastAPI(title=active_settings.app_name, version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "llm_mode": active_settings.llm_mode}

    @app.post("/extract")
    def extract(request: ExtractRequest) -> dict:
        try:
            model_settings = active_settings.model_copy(update={"llm_mode": request.mode})
            extractor = CapabilityExtractor(
                create_chat_model(model_settings),
                max_input_chars=active_settings.max_input_chars,
            )
            capability = extractor.extract(
                source_text=request.source_text,
                source_id=request.source_id,
                source_type=request.source_type,
                source_location=request.source_location,
            )
            return capability.model_dump(mode="json")
        except (ValueError, TypeError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/reproduce")
    def reproduce(request: ReproduceRequest) -> dict:
        try:
            model_settings = active_settings.model_copy(update={"llm_mode": request.mode})
            extractor = CapabilityExtractor(
                create_chat_model(model_settings),
                max_input_chars=active_settings.max_input_chars,
            )
            capability = extractor.extract(
                source_text=request.source_text,
                source_id=request.source_id,
                source_type=request.source_type,
                source_location=request.source_location,
            )
            source = IngestedSource(
                source_id=request.source_id,
                path=request.source_location or request.source_id,
                source_type=request.source_type,
                source_format=request.source_format,
                content=request.source_text,
                content_sha256=hashlib.sha256(request.source_text.encode("utf-8")).hexdigest(),
            )
            state = {
                "source": source.model_dump(mode="json"),
                "capability": capability.model_dump(mode="json"),
            }

            def run_in_sandbox(workspace: Path) -> ExecutionResult:
                if execution_runner is not None:
                    return execution_runner(request.backend, workspace)
                runner = (
                    WslDockerSandboxRunner()
                    if request.backend == "wsl"
                    else DockerSandboxRunner()
                )
                return runner.run(
                    workspace,
                    ["python", "-m", "unittest", "discover", "-v"],
                    policy=ExecutionPolicy(),
                )

            repair_callback = _template_repair_callback if request.repair else None
            if request.execute:
                with TemporaryDirectory(prefix="algo-weaver-api-") as workspace:
                    result = build_reproduction_graph(
                        workspace=workspace,
                        runner=run_in_sandbox,
                        repair=repair_callback,
                        max_repair_attempts=request.max_repair_attempts,
                    ).invoke(state)
            else:
                result = build_reproduction_graph().invoke(state)

            if "error" in result:
                raise HTTPException(status_code=422, detail=result["error"])

            bundle = result["bundle"]
            dependency_reports = [
                PythonDependencyAnalyzer().analyze(
                    artifact["content"], source_id=artifact["path"]
                ).model_dump(mode="json")
                for artifact in bundle["artifacts"]
                if artifact["kind"] == "python_source"
            ]
            response = {
                "capability": capability.model_dump(mode="json"),
                "hits": result.get("hits", []),
                "plan": result["plan"],
                "bundle": bundle,
                "reports": result.get("reports", []),
                "dependency_reports": dependency_reports,
            }
            if request.execute:
                response["execution"] = result["execution"]
                if "repair_result" in result:
                    response["repair_result"] = result["repair_result"]
            return response
        except HTTPException:
            raise
        except (ValueError, TypeError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return app


app = None
