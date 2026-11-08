"""Schemas for durable repair observations and failure experience."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

FailureOutcome = Literal["failed", "repaired", "abandoned"]


class RepairFailureRecord(BaseModel):
    """One bounded repair observation that can be reused as experience."""

    model_config = ConfigDict(extra="forbid")

    failure_id: str = Field(default_factory=lambda: f"failure_{uuid4().hex[:12]}")
    run_id: str = Field(min_length=1)
    capability_id: str = Field(min_length=1)
    attempt: int = Field(ge=1)
    observation: str = Field(min_length=1)
    patch_hash: str | None = None
    outcome: FailureOutcome
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
