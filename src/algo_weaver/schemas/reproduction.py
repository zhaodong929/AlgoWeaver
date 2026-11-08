"""Schemas for planned algorithm reproduction artifacts."""

from __future__ import annotations

from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

PlanStatus = Literal["ready", "blocked"]
GenerationMode = Literal["template", "mock", "llm"]
ArtifactKind = Literal["python_source", "pytest_test"]


class ReproductionStep(BaseModel):
    """One auditable step in a reproduction plan."""

    model_config = ConfigDict(extra="forbid")

    step_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    evidence_chunk_ids: list[str] = Field(default_factory=list)
    acceptance_checks: list[str] = Field(default_factory=list)


class ReproductionPlan(BaseModel):
    """Structured plan used before any code artifact is written."""

    model_config = ConfigDict(extra="forbid")

    plan_id: str = Field(default_factory=lambda: f"plan_{uuid4().hex[:12]}")
    capability_id: str = Field(min_length=1)
    capability_name: str = Field(min_length=1)
    required_entrypoint: str | None = Field(default=None)
    algorithm_family: str = Field(min_length=1)
    objective: str = Field(min_length=1)
    required_inputs: list[str] = Field(default_factory=list)
    expected_outputs: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    steps: list[ReproductionStep] = Field(min_length=1)
    evidence_source_ids: list[str] = Field(default_factory=list)
    evidence_chunk_ids: list[str] = Field(default_factory=list)
    acceptance_checks: list[str] = Field(default_factory=list)
    generation_mode: GenerationMode = "template"
    status: PlanStatus
    blocking_reasons: list[str] = Field(default_factory=list)


class GeneratedArtifact(BaseModel):
    """A generated file that is still unverified until an execution workflow passes."""

    model_config = ConfigDict(extra="forbid")

    artifact_id: str = Field(default_factory=lambda: f"artifact_{uuid4().hex[:12]}")
    path: str = Field(min_length=1)
    kind: ArtifactKind
    content: str = Field(min_length=1)
    content_sha256: str = Field(min_length=64, max_length=64)
    generation_mode: GenerationMode = "template"
    verification_status: Literal["unverified"] = "unverified"


class ReproductionBundle(BaseModel):
    """Plan plus files ready for a later isolated validation step."""

    model_config = ConfigDict(extra="forbid")

    plan: ReproductionPlan
    artifacts: list[GeneratedArtifact] = Field(min_length=1)


class GeneratedCodeDraft(BaseModel):
    """Structured code returned by a model before static validation."""

    model_config = ConfigDict(extra="forbid")

    algorithm_source: str = Field(min_length=1)
    test_source: str = Field(min_length=1)
    dependencies: list[str] = Field(default_factory=list)
