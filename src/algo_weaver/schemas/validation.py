"""Schemas for deterministic validation reports."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

CheckStatus = Literal["passed", "failed", "skipped"]
ReportStatus = Literal["passed", "failed", "partial"]
ValidationTarget = Literal["capability", "python_source"]


class ValidationCheck(BaseModel):
    """One deterministic validation observation."""

    model_config = ConfigDict(extra="forbid")

    check_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    status: CheckStatus
    message: str = Field(min_length=1)
    details: dict[str, str | int | float | bool] = Field(default_factory=dict)


class ValidationReport(BaseModel):
    """Auditable validation result for a capability or source file."""

    model_config = ConfigDict(extra="forbid")

    report_id: str = Field(default_factory=lambda: f"val_{uuid4().hex[:12]}")
    target_type: ValidationTarget
    target_id: str = Field(min_length=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    checks: list[ValidationCheck] = Field(min_length=1)
    overall_status: ReportStatus

    @property
    def passed_count(self) -> int:
        return sum(check.status == "passed" for check in self.checks)

    @property
    def failed_count(self) -> int:
        return sum(check.status == "failed" for check in self.checks)

    @property
    def skipped_count(self) -> int:
        return sum(check.status == "skipped" for check in self.checks)
