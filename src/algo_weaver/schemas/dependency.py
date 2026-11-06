"""Dependency analysis results for generated Python artifacts."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DependencyReport(BaseModel):
    """Static import inventory; it never installs or imports the target code."""

    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(min_length=1)
    imports: list[str] = Field(default_factory=list)
    standard_library: list[str] = Field(default_factory=list)
    third_party: list[str] = Field(default_factory=list)
    relative_imports: list[str] = Field(default_factory=list)
    dynamic_imports: list[str] = Field(default_factory=list)
    parse_error: str | None = None
