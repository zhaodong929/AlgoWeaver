"""Pydantic contracts for deterministic candidate algorithm comparisons."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from algo_weaver.schemas.capability import CapabilityStatus
from algo_weaver.schemas.metrics import MetricReport
from algo_weaver.schemas.validation import ValidationReport


class ForecastCandidateResult(BaseModel):
    """One candidate's predictions, metrics and auditable validation result."""

    model_config = ConfigDict(extra="forbid")

    candidate_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    algorithm_family: str = Field(min_length=1)
    predictions: list[float] = Field(min_length=1)
    metric_report: MetricReport
    validation_report: ValidationReport

    @model_validator(mode="after")
    def keep_validation_status_consistent(self) -> ForecastCandidateResult:
        if self.validation_report.target_id != self.candidate_id:
            raise ValueError("candidate validation report target does not match candidate_id")
        return self


class InventoryForecastComparisonReport(BaseModel):
    """Comparison artifact for inventory demand forecasting candidates.

    ``status`` uses the same lifecycle values as capability cards. A passing
    comparison leaves a draft capability eligible for a separate runtime gate,
    preserves ``needs_review`` cards, and only keeps an already verified card
    verified after comparison.
    """

    model_config = ConfigDict(extra="forbid")

    report_id: str = Field(default_factory=lambda: f"cmp_{uuid4().hex[:12]}")
    task: Literal["inventory_demand"] = "inventory_demand"
    window: int = Field(ge=1)
    actual: list[float] = Field(min_length=2)
    evaluation_target: list[float] = Field(min_length=1)
    candidates: list[ForecastCandidateResult] = Field(min_length=1)
    selected_candidate_id: str | None = None
    selection_metric: Literal["mae", "rmse"] = "mae"
    validation_report: ValidationReport
    overall_status: Literal["passed", "failed", "partial"]
    status: CapabilityStatus
    capability_id: str | None = None
    registry_version: int | None = Field(default=None, ge=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_consistent_status(self) -> InventoryForecastComparisonReport:
        if self.validation_report.target_id != self.report_id:
            raise ValueError("comparison validation report target does not match report_id")
        if self.validation_report.overall_status != self.overall_status:
            raise ValueError("comparison status must match validation report status")
        if self.status == "verified" and self.overall_status != "passed":
            raise ValueError("verified comparison requires a passing validation report")
        if self.selected_candidate_id is not None and self.selected_candidate_id not in {
            candidate.candidate_id for candidate in self.candidates
        }:
            raise ValueError("selected_candidate_id must reference a candidate")
        return self


# Short aliases keep the domain-specific name available without making callers
# depend on an implementation-specific report class name.
AlgorithmComparisonReport = InventoryForecastComparisonReport
CandidateResult = ForecastCandidateResult
