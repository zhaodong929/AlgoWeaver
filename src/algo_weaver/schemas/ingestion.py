"""Schemas for source ingestion and provenance."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

IngestionStatus = Literal["ingested", "unsupported", "failed"]
SourceFormat = Literal[
    "text",
    "markdown",
    "python",
    "csv",
    "json",
    "yaml",
    "pdf",
    "docx",
    "pptx",
    "xlsx",
    "unknown",
]


class IngestedSource(BaseModel):
    """Normalized source content with enough provenance for later extraction."""

    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(min_length=1)
    path: str = Field(min_length=1)
    source_type: str = Field(min_length=1)
    source_format: SourceFormat
    media_type: str = "text/plain"
    content: str = ""
    content_sha256: str = Field(min_length=64, max_length=64)
    metadata: dict[str, str | int | bool] = Field(default_factory=dict)
    status: IngestionStatus = "ingested"
    error: str | None = None


class IngestionBatch(BaseModel):
    """Results for a multi-source ingestion request."""

    model_config = ConfigDict(extra="forbid")

    sources: list[IngestedSource] = Field(min_length=1)

    @property
    def ingested_count(self) -> int:
        return sum(source.status == "ingested" for source in self.sources)

    @property
    def unsupported_count(self) -> int:
        return sum(source.status == "unsupported" for source in self.sources)

    @property
    def failed_count(self) -> int:
        return sum(source.status == "failed" for source in self.sources)
