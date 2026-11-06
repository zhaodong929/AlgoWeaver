"""Schemas for provenance-preserving local retrieval."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class EvidenceChunk(BaseModel):
    """A searchable text/code window tied to a source location."""

    model_config = ConfigDict(extra="forbid")

    chunk_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    source_type: str = Field(min_length=1)
    source_format: str = Field(min_length=1)
    path: str = Field(min_length=1)
    text: str = Field(min_length=1)
    line_start: int = Field(ge=1)
    line_end: int = Field(ge=1)
    metadata: dict[str, str | int | bool] = Field(default_factory=dict)

    @property
    def location(self) -> str:
        """Human-readable source location for citations and UI display."""
        return f"{self.path}:L{self.line_start}-L{self.line_end}"


class RetrievalHit(BaseModel):
    """One ranked retrieval result with the complete evidence chunk attached."""

    model_config = ConfigDict(extra="forbid")

    rank: int = Field(ge=1)
    score: float = Field(ge=0)
    matched_terms: list[str] = Field(default_factory=list)
    chunk: EvidenceChunk
