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


class RerankResult(BaseModel):
    """One reranker score tied to the original candidate document index."""

    model_config = ConfigDict(extra="forbid")

    index: int = Field(ge=0)
    score: float
    text: str = Field(min_length=1)


class RetrievalCase(BaseModel):
    """One deterministic retrieval evaluation query."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1)
    relevant_chunk_ids: list[str] = Field(min_length=1)
    top_k: int = Field(default=5, ge=1)


class RetrievalCaseResult(BaseModel):
    """Metrics and provenance coverage for one evaluation query."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1)
    retrieved_chunk_ids: list[str] = Field(default_factory=list)
    recall_at_k: float = Field(ge=0, le=1)
    reciprocal_rank: float = Field(ge=0, le=1)
    evidence_coverage: float = Field(ge=0, le=1)


class RetrievalEvaluation(BaseModel):
    """Aggregate deterministic retrieval metrics."""

    model_config = ConfigDict(extra="forbid")

    cases: list[RetrievalCaseResult] = Field(min_length=1)
    mean_recall_at_k: float = Field(ge=0, le=1)
    mean_reciprocal_rank: float = Field(ge=0, le=1)
    mean_evidence_coverage: float = Field(ge=0, le=1)
    score_fusion_used: bool = False
