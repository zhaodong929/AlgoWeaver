"""Canonical schemas for extracted algorithm capabilities."""

from __future__ import annotations

from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SourceType = Literal["document", "code", "experiment", "expert_note", "test_report", "unknown"]
CapabilityStatus = Literal["draft", "needs_review", "verified"]


class AlgorithmParameter(BaseModel):
    """A parameter required or supported by an algorithm."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, description="Parameter name")
    description: str = Field(default="", description="What the parameter controls")
    data_type: str = Field(default="unknown", description="Expected parameter type")
    default: str | int | float | bool | None = None
    constraints: list[str] = Field(default_factory=list)


class EvidenceRef(BaseModel):
    """A pointer back to the source material used during extraction."""

    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(min_length=1)
    source_type: SourceType = "unknown"
    location: str | None = None
    line_start: int | None = Field(default=None, ge=1)
    line_end: int | None = Field(default=None, ge=1)
    content_sha256: str | None = Field(default=None, min_length=64, max_length=64)
    excerpt: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_line_range(self) -> EvidenceRef:
        if (self.line_start is None) != (self.line_end is None):
            raise ValueError("line_start and line_end must be provided together")
        if self.line_start is not None and self.line_end is not None:
            if self.line_end < self.line_start:
                raise ValueError("line_end must be greater than or equal to line_start")
        return self


class AlgorithmDraft(BaseModel):
    """LLM-facing extraction result, before source provenance is attached."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    problem_definition: str = Field(default="")
    algorithm_family: str = Field(default="unknown")
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    preprocessing: list[str] = Field(default_factory=list)
    algorithm_steps: list[str] = Field(default_factory=list)
    parameters: list[AlgorithmParameter] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    metrics: list[str] = Field(default_factory=list)
    failure_cases: list[str] = Field(default_factory=list)
    implementation_notes: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)


class AlgorithmCapability(BaseModel):
    """Persistable algorithm capability with provenance and review status."""

    model_config = ConfigDict(extra="forbid")

    capability_id: str = Field(default_factory=lambda: f"cap_{uuid4().hex[:12]}")
    schema_version: str = "1.0"
    name: str = Field(min_length=1)
    problem_definition: str = ""
    algorithm_family: str = "unknown"
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    preprocessing: list[str] = Field(default_factory=list)
    algorithm_steps: list[str] = Field(default_factory=list)
    parameters: list[AlgorithmParameter] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    metrics: list[str] = Field(default_factory=list)
    failure_cases: list[str] = Field(default_factory=list)
    implementation_notes: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    evidence: list[EvidenceRef] = Field(default_factory=list)
    status: CapabilityStatus = "draft"

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Algorithm name cannot be blank")
        return value
