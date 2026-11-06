"""Execution policy and result schemas for isolated code runs."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ExecutionStatus = Literal["passed", "failed", "timeout", "blocked"]


class ExecutionPolicy(BaseModel):
    """Resource and isolation limits applied to a Docker execution."""

    model_config = ConfigDict(extra="forbid")

    image: str = Field(default="python:3.12-slim", min_length=1)
    timeout_seconds: float = Field(default=30.0, gt=0, le=600)
    memory_mb: int = Field(default=512, ge=64, le=16_384)
    cpu_limit: float = Field(default=1.0, gt=0, le=8)
    pids_limit: int = Field(default=128, ge=1, le=4096)
    network_enabled: bool = False
    read_only_workspace: bool = True
    max_output_chars: int = Field(default=20_000, ge=1, le=1_000_000)


class ExecutionResult(BaseModel):
    """Auditable result returned by a sandbox runner."""

    model_config = ConfigDict(extra="forbid")

    status: ExecutionStatus
    command: list[str] = Field(min_length=1)
    image: str = Field(min_length=1)
    exit_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    duration_seconds: float = Field(ge=0)
    error: str | None = None
