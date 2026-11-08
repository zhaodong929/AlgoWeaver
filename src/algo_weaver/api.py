"""Optional FastAPI surface for the CLI-first AlgoWeaver services."""

from __future__ import annotations

import hashlib
import json
import secrets
import time
from collections import defaultdict, deque
from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Lock
from typing import Literal

from pydantic import BaseModel, Field

from algo_weaver.agents.reproduction_graph import build_reproduction_graph
from algo_weaver.config import Settings, get_settings
from algo_weaver.llm.factory import create_chat_model
from algo_weaver.schemas.capability import AlgorithmCapability, SourceType
from algo_weaver.schemas.execution import ExecutionPolicy, ExecutionResult
from algo_weaver.schemas.ingestion import IngestedSource, SourceFormat
from algo_weaver.schemas.reproduction import ReproductionBundle
from algo_weaver.services.capability_extractor import CapabilityExtractor
from algo_weaver.services.code_generation import (
    ArtifactGenerator,
    LLMCodeGenerator,
    MockCodeGenerator,
)
from algo_weaver.services.dependency import PythonDependencyAnalyzer
from algo_weaver.services.embedding import create_embedding_provider
from algo_weaver.services.llm_repair import LLMRepairer
from algo_weaver.services.metrics import RegressionMetricEvaluator
from algo_weaver.services.qdrant_retrieval import create_qdrant_retriever
from algo_weaver.services.registry import CapabilityRegistry
from algo_weaver.services.reranker import create_reranker_provider
from algo_weaver.services.sandbox import DockerSandboxRunner, WslDockerSandboxRunner
from algo_weaver.services.template_repair import TemplateRepairer

ExecutionRunnerFactory = Callable[[str, Path], ExecutionResult]
MetricRunnerFactory = Callable[[str, Path, list[str]], ExecutionResult]


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


class AdditionalSourceRequest(BaseModel):
    source_text: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    source_type: SourceType = "document"
    source_format: SourceFormat = "markdown"
    source_location: str | None = None


class ReproduceRequest(ExtractRequest):
    source_format: SourceFormat = "markdown"
    execute: bool = False
    backend: Literal["docker", "wsl"] = "docker"
    repair: bool = False
    max_repair_attempts: int = Field(default=2, ge=0, le=5)
    persist: bool = False
    additional_sources: list[AdditionalSourceRequest] = Field(default_factory=list)
    generation_mode: Literal["template", "mock", "llm"] = "template"
    repair_mode: Literal["template", "llm"] = "template"
    metrics: SandboxMetricsRequest | None = None
    reuse_query: str | None = Field(default=None, min_length=1)
    auto_reuse: bool = False


class MetricsRequest(BaseModel):
    task: str = Field(default="regression", min_length=1)
    actual: list[float] = Field(min_length=1)
    predicted: list[float] = Field(min_length=1)
    max_mae: float | None = Field(default=None, ge=0)
    max_rmse: float | None = Field(default=None, ge=0)


class SandboxMetricsRequest(BaseModel):
    """Safe inventory metric configuration for a generated moving-average artifact."""

    task: Literal["inventory_demand"] = "inventory_demand"
    actual: list[float] = Field(min_length=1)
    window: int = Field(default=3, ge=1)
    max_mae: float | None = Field(default=None, ge=0)
    max_rmse: float | None = Field(default=None, ge=0)


def create_app(
    settings: Settings | None = None,
    execution_runner: ExecutionRunnerFactory | None = None,
    metric_runner: MetricRunnerFactory | None = None,
):
    """Create the optional API app; importing this module does not require FastAPI."""
    try:
        from fastapi import FastAPI, HTTPException
    except ModuleNotFoundError as exc:  # pragma: no cover - depends on optional extra
        raise RuntimeError("FastAPI is required for the API extra") from exc

    active_settings = settings or get_settings()
    app = FastAPI(title=active_settings.app_name, version="0.1.0")
    if active_settings.api_auth_mode == "api_key" and active_settings.api_key is None:
        raise RuntimeError("ALGOWEAVER_API_KEY is required when ALGOWEAVER_API_AUTH_MODE=api_key")

    # Dependency-free limiter for one process. Multi-replica deployments should
    # put a shared limiter at the reverse proxy (for example Redis-backed).
    request_timestamps: dict[str, deque[float]] = defaultdict(deque)
    limiter_lock = Lock()

    @app.middleware("http")
    async def access_boundary(request, call_next):
        if request.url.path == "/health" or request.method == "OPTIONS":
            return await call_next(request)

        if active_settings.api_auth_mode == "api_key":
            supplied = request.headers.get("x-api-key", "")
            authorization = request.headers.get("authorization", "")
            if not supplied and authorization.lower().startswith("bearer "):
                supplied = authorization[7:].strip()
            configured = active_settings.api_key.get_secret_value() if active_settings.api_key else ""
            if not supplied or not secrets.compare_digest(supplied, configured):
                from fastapi.responses import JSONResponse

                return JSONResponse(
                    {"detail": "valid API key required"},
                    status_code=401,
                    headers={"WWW-Authenticate": "Bearer"},
                )

        if active_settings.rate_limit_requests > 0:
            client = request.client.host if request.client else "unknown"
            now = time.monotonic()
            cutoff = now - active_settings.rate_limit_window_seconds
            with limiter_lock:
                timestamps = request_timestamps[client]
                while timestamps and timestamps[0] <= cutoff:
                    timestamps.popleft()
                if len(timestamps) >= active_settings.rate_limit_requests:
                    retry_after = max(
                        1,
                        int(timestamps[0] + active_settings.rate_limit_window_seconds - now),
                    )
                    from fastapi.responses import JSONResponse

                    return JSONResponse(
                        {"detail": "rate limit exceeded"},
                        status_code=429,
                        headers={"Retry-After": str(retry_after)},
                    )
                timestamps.append(now)
        return await call_next(request)

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

    @app.post("/metrics")
    def metrics(request: MetricsRequest) -> dict:
        try:
            report = RegressionMetricEvaluator().evaluate(
                request.actual,
                request.predicted,
                task=request.task,
                max_mae=request.max_mae,
                max_rmse=request.max_rmse,
            )
            return report.model_dump(mode="json")
        except (ValueError, TypeError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/reproduce")
    def reproduce(request: ReproduceRequest) -> dict:
        try:
            if request.generation_mode == "llm" and request.mode != "litellm":
                raise HTTPException(
                    status_code=400,
                    detail="generation_mode='llm' requires mode='litellm'",
                )
            if request.repair_mode == "llm" and not request.repair:
                raise HTTPException(
                    status_code=400,
                    detail="repair_mode='llm' requires repair=true",
                )
            if request.repair_mode == "llm" and request.mode != "litellm":
                raise HTTPException(
                    status_code=400,
                    detail="repair_mode='llm' requires mode='litellm'",
                )
            if request.metrics is not None and not request.execute:
                raise HTTPException(
                    status_code=400,
                    detail="metrics requires execute=true",
                )
            if request.metrics is not None and request.metrics.window > len(request.metrics.actual):
                raise HTTPException(
                    status_code=400,
                    detail="metrics.window cannot exceed the number of actual samples",
                )
            if request.reuse_query is not None and request.auto_reuse:
                raise HTTPException(
                    status_code=400,
                    detail="use either reuse_query or auto_reuse, not both",
                )
            model_settings = active_settings.model_copy(update={"llm_mode": request.mode})
            reused_record = None
            if request.reuse_query is not None:
                matches = CapabilityRegistry(active_settings.registry_path).search_reusable(
                    request.reuse_query,
                    limit=1,
                )
                if not matches:
                    raise HTTPException(
                        status_code=404,
                        detail=f"no verified capability matched: {request.reuse_query}",
                    )
                reused_record = matches[0]
                capability = AlgorithmCapability.model_validate(reused_record.capability)
            else:
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
                if request.auto_reuse:
                    matches = CapabilityRegistry(active_settings.registry_path).search_reusable(
                        capability.name,
                        limit=1,
                    )
                    if matches:
                        reused_record = matches[0]
                        capability = AlgorithmCapability.model_validate(reused_record.capability)
            source = IngestedSource(
                source_id=request.source_id,
                path=request.source_location or request.source_id,
                source_type=request.source_type,
                source_format=request.source_format,
                content=request.source_text,
                content_sha256=hashlib.sha256(request.source_text.encode("utf-8")).hexdigest(),
            )
            additional_sources = [
                IngestedSource(
                    source_id=item.source_id,
                    path=item.source_location or item.source_id,
                    source_type=item.source_type,
                    source_format=item.source_format,
                    content=item.source_text,
                    content_sha256=hashlib.sha256(
                        item.source_text.encode("utf-8")
                    ).hexdigest(),
                )
                for item in request.additional_sources
            ]
            state = {
                "source": source.model_dump(mode="json"),
                "sources": [
                    source.model_dump(mode="json"),
                    *(item.model_dump(mode="json") for item in additional_sources),
                ],
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

            def run_metric_in_sandbox(workspace: Path, command: list[str]) -> ExecutionResult:
                if metric_runner is not None:
                    return metric_runner(request.backend, workspace, command)
                if execution_runner is not None:
                    raise ValueError(
                        "metric_runner is required when an execution_runner is injected"
                    )
                runner = (
                    WslDockerSandboxRunner()
                    if request.backend == "wsl"
                    else DockerSandboxRunner()
                )
                return runner.run(workspace, command, policy=ExecutionPolicy())

            repair_callback = None
            if request.repair:
                repair_callback = (
                    LLMRepairer(
                        create_chat_model(model_settings, model=model_settings.code_llm_model)
                    ).repair
                    if request.repair_mode == "llm"
                    else _template_repair_callback
                )
            generator: ArtifactGenerator | None = None
            if request.generation_mode == "mock":
                generator = MockCodeGenerator()
            elif request.generation_mode == "llm":
                generator = LLMCodeGenerator(
                    create_chat_model(model_settings, model=model_settings.code_llm_model)
                )
            embedding_provider = (
                create_embedding_provider(active_settings)
                if active_settings.embedding_mode != "mock"
                else None
            )
            reranker_provider = (
                create_reranker_provider(active_settings)
                if active_settings.reranker_mode != "mock"
                else None
            )
            metric_execution: ExecutionResult | None = None
            metric_report: dict | None = None
            if request.execute:
                with TemporaryDirectory(prefix="algo-weaver-api-") as workspace:
                    result = build_reproduction_graph(
                        workspace=workspace,
                        runner=run_in_sandbox,
                        repair=repair_callback,
                        max_repair_attempts=request.max_repair_attempts,
                        generator=generator,
                        embedding_provider=embedding_provider,
                        reranker_provider=reranker_provider,
                        qdrant_factory=(
                            (lambda dimension: create_qdrant_retriever(active_settings, dimension))
                            if active_settings.qdrant_mode == "server"
                            else None
                        ),
                    ).invoke(state)
                    if request.metrics is not None and result.get("execution", {}).get("status") == "passed":
                        workspace_path = Path(workspace)
                        (workspace_path / "metric_input.json").write_text(
                            json.dumps(
                                {
                                    "actual": request.metrics.actual,
                                    "window": request.metrics.window,
                                }
                            ),
                            encoding="utf-8",
                        )
                        metric_command = [
                            "python",
                            "-c",
                            (
                                "import json; "
                                "from algorithm import moving_average; "
                                "payload=json.load(open('/workspace/metric_input.json', encoding='utf-8')); "
                                "print(json.dumps(moving_average(payload['actual'], payload['window'])))"
                            ),
                        ]
                        metric_execution = run_metric_in_sandbox(workspace_path, metric_command)
                        if metric_execution.status == "passed":
                            try:
                                predicted = json.loads(metric_execution.stdout.strip())
                            except (json.JSONDecodeError, TypeError) as exc:
                                raise HTTPException(
                                    status_code=422,
                                    detail=f"metric sandbox returned invalid JSON: {exc}",
                                ) from exc
                            metric_report = RegressionMetricEvaluator().evaluate(
                                request.metrics.actual[request.metrics.window - 1 :],
                                predicted,
                                task=request.metrics.task,
                                max_mae=request.metrics.max_mae,
                                max_rmse=request.metrics.max_rmse,
                            ).model_dump(mode="json")
            else:
                result = build_reproduction_graph(
                    generator=generator,
                    embedding_provider=embedding_provider,
                    reranker_provider=reranker_provider,
                    qdrant_factory=(
                        (lambda dimension: create_qdrant_retriever(active_settings, dimension))
                        if active_settings.qdrant_mode == "server"
                        else None
                    ),
                ).invoke(state)

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
                "sources": [item.model_dump(mode="json") for item in [source, *additional_sources]],
                "hits": result.get("hits", []),
                "plan": result["plan"],
                "bundle": bundle,
                "reports": result.get("reports", []),
                "dependency_reports": dependency_reports,
            }
            if reused_record is not None:
                response["reused_record"] = reused_record.model_dump(mode="json")
            if request.persist:
                registry = CapabilityRegistry(active_settings.registry_path)
                saved = registry.save(capability)
                registry_record = saved
                metric_gate_passed = request.metrics is None or (
                    metric_report is not None and metric_report["overall_status"] == "passed"
                )
                if request.execute and result.get("reports"):
                    runtime_report = result["reports"][-1]
                    if runtime_report["target_type"] == "capability" and runtime_report[
                        "overall_status"
                    ] == "passed" and metric_gate_passed:
                        from algo_weaver.schemas.validation import ValidationReport

                        registry_record = registry.promote_verified(
                            capability.capability_id,
                            ValidationReport.model_validate(runtime_report),
                        )
                response["registry_record"] = registry_record.model_dump(mode="json")
            if request.execute:
                response["execution"] = result["execution"]
                if "repair_result" in result:
                    response["repair_result"] = result["repair_result"]
                if metric_execution is not None:
                    response["metric_execution"] = metric_execution.model_dump(mode="json")
                if metric_report is not None:
                    response["metric_report"] = metric_report
            return response
        except HTTPException:
            raise
        except (ValueError, TypeError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return app


app = None
