"""Schemas for deterministic algorithm metric reports."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class MetricResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    value: float = Field(ge=0)
    threshold: float | None = Field(default=None, ge=0)
    passed: bool | None = None


class MetricReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task: str = Field(min_length=1)
    sample_count: int = Field(ge=1)
    metrics: list[MetricResult] = Field(min_length=1)
    overall_status: str = Field(min_length=1)
