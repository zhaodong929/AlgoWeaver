"""Optional FastAPI surface for the CLI-first AlgoWeaver services."""

from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, Field

from algo_weaver.config import Settings, get_settings
from algo_weaver.llm.factory import create_chat_model
from algo_weaver.schemas.capability import SourceType
from algo_weaver.schemas.ingestion import IngestedSource, SourceFormat
from algo_weaver.services.capability_extractor import CapabilityExtractor
from algo_weaver.services.dependency import PythonDependencyAnalyzer
from algo_weaver.services.reproduction import TemplateArtifactWriter
from algo_weaver.services.retrieval import LocalLexicalRetriever, SourceChunker
from algo_weaver.services.validation import ValidationService


class ExtractRequest(BaseModel):
    source_text: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    source_type: SourceType = "document"
    source_location: str | None = None
    mode: Literal["mock", "litellm"] = "mock"


class ReproduceRequest(ExtractRequest):
    source_format: SourceFormat = "markdown"


def create_app(settings: Settings | None = None):
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
            chunks = SourceChunker().chunk(source)
            hits = LocalLexicalRetriever(chunks).search(capability.name, top_k=5)
            from algo_weaver.services.reproduction import ReproductionPlanner

            plan = ReproductionPlanner().build_plan(capability, hits)
            if plan.status != "ready":
                raise HTTPException(status_code=422, detail=plan.blocking_reasons)
            bundle = TemplateArtifactWriter().generate(plan)
            validator = ValidationService()
            reports = [validator.validate_capability(capability)]
            dependency_reports = []
            for artifact in bundle.artifacts:
                if artifact.kind == "python_source":
                    dependency_reports.append(
                        PythonDependencyAnalyzer().analyze(artifact.content, source_id=artifact.path)
                    )
                    reports.append(validator.validate_python_source(artifact.content, source_id=artifact.path))
            return {
                "capability": capability.model_dump(mode="json"),
                "hits": [hit.model_dump(mode="json") for hit in hits],
                "plan": plan.model_dump(mode="json"),
                "bundle": bundle.model_dump(mode="json"),
                "reports": [report.model_dump(mode="json") for report in reports],
                "dependency_reports": [report.model_dump(mode="json") for report in dependency_reports],
            }
        except HTTPException:
            raise
        except (ValueError, TypeError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return app


app = None
