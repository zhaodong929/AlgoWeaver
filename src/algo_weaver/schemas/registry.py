"""Schemas for persisted, versioned capability records."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CapabilityVersion(BaseModel):
    """One immutable registry version of an algorithm capability."""

    model_config = ConfigDict(extra="forbid")

    capability_id: str = Field(min_length=1)
    version: int = Field(ge=1)
    status: str = Field(min_length=1)
    name: str = Field(min_length=1)
    created_at: datetime
    capability: dict
