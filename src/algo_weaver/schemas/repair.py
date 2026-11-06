"""Schemas for bounded, externally observed repair loops."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

RepairAttemptStatus = Literal["applied", "failed", "skipped"]
RepairFinalStatus = Literal["passed", "failed", "exhausted", "blocked"]


class RepairAttempt(BaseModel):
    """One repair decision and its resulting execution observation."""

    model_config = ConfigDict(extra="forbid")

    attempt: int = Field(ge=1)
    status: RepairAttemptStatus
    observation: str = Field(min_length=1)


class RepairLoopResult(BaseModel):
    """Bounded repair outcome with all external observations retained."""

    model_config = ConfigDict(extra="forbid")

    final_status: RepairFinalStatus
    attempts: list[RepairAttempt] = Field(default_factory=list)
    max_attempts: int = Field(ge=0)
