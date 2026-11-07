"""Dependency-free lexical chunking and retrieval baseline."""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence

from algo_weaver.schemas.ingestion import IngestedSource
from algo_weaver.schemas.retrieval import (
    EvidenceChunk,
    RetrievalCase,
    RetrievalCaseResult,
    RetrievalEvaluation,
    RetrievalHit,
)

_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]")


class SourceChunker:
    """Split normalized source text into line-addressable evidence windows."""

    def chunk(
        self,
        source: IngestedSource,
        *,
        max_chars: int = 1200,
        overlap_lines: int = 1,
    ) -> list[EvidenceChunk]:
        if max_chars < 1:
            raise ValueError("max_chars must be positive")
        if overlap_lines < 0:
            raise ValueError("overlap_lines cannot be negative")
        if not source.content.strip():
            return []

        lines = source.content.splitlines()
        chunks: list[EvidenceChunk] = []
        start = 0
        while start < len(lines):
            end = start
            size = 0
            while end < len(lines):
                candidate_size = len(lines[end]) + (1 if end > start else 0)
                if end > start and size + candidate_size > max_chars:
                    break
                size += candidate_size
                end += 1
            text = "\n".join(lines[start:end]).strip()
            if text:
                line_start = start + 1
                line_end = end
                digest = hashlib.sha256(
                    f"{source.source_id}:{line_start}:{line_end}:{text}".encode()
                ).hexdigest()[:16]
                chunks.append(
                    EvidenceChunk(
                        chunk_id=f"chunk_{digest}",
                        source_id=source.source_id,
                        source_type=source.source_type,
                        source_format=source.source_format,
                        path=source.path,
                        text=text,
                        line_start=line_start,
                        line_end=line_end,
                        metadata={**source.metadata},
                    )
                )
            if end >= len(lines):
                break
            start = max(start + 1, end - overlap_lines)
        return chunks


class LocalLexicalRetriever:
    """Rank evidence chunks by deterministic token overlap."""

    def __init__(self, chunks: Iterable[EvidenceChunk] = ()) -> None:
        self._chunks: dict[str, EvidenceChunk] = {}
        self.add(chunks)

    def add(self, chunks: Iterable[EvidenceChunk]) -> None:
        for chunk in chunks:
            self._chunks[chunk.chunk_id] = chunk

    def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        source_type: str | None = None,
        metadata_filter: Mapping[str, str | int | bool] | None = None,
    ) -> list[RetrievalHit]:
        if not query.strip():
            raise ValueError("query cannot be empty")
        if top_k < 1:
            raise ValueError("top_k must be positive")

        query_terms = set(_tokenize(query))
        if not query_terms:
            return []
        candidates: list[tuple[float, list[str], EvidenceChunk]] = []
        for chunk in self._chunks.values():
            if source_type is not None and chunk.source_type != source_type:
                continue
            if metadata_filter and any(
                chunk.metadata.get(key) != value for key, value in metadata_filter.items()
            ):
                continue
            counts = Counter(_tokenize(chunk.text))
            matched = sorted(query_terms.intersection(counts))
            if not matched:
                continue
            score = sum(counts[token] for token in matched) / len(query_terms)
            candidates.append((score, matched, chunk))

        candidates.sort(key=lambda item: (-item[0], item[2].chunk_id))
        return [
            RetrievalHit(rank=index, score=score, matched_terms=matched, chunk=chunk)
            for index, (score, matched, chunk) in enumerate(candidates[:top_k], start=1)
        ]


class RetrievalEvaluator:
    """Evaluate a retriever with deterministic Recall@k, MRR and provenance coverage."""

    def evaluate(
        self,
        retriever: LocalLexicalRetriever,
        cases: Sequence[RetrievalCase],
    ) -> RetrievalEvaluation:
        if not cases:
            raise ValueError("cases cannot be empty")
        results: list[RetrievalCaseResult] = []
        for case in cases:
            hits = retriever.search(case.query, top_k=case.top_k)
            retrieved_ids = [hit.chunk.chunk_id for hit in hits]
            relevant = set(case.relevant_chunk_ids)
            found = relevant.intersection(retrieved_ids)
            recall = len(found) / len(relevant)
            reciprocal_rank = next(
                (1 / index for index, chunk_id in enumerate(retrieved_ids, start=1) if chunk_id in relevant),
                0.0,
            )
            evidence_coverage = (
                sum(bool(hit.chunk.source_id and hit.chunk.path and hit.chunk.location) for hit in hits)
                / len(hits)
                if hits
                else 0.0
            )
            results.append(
                RetrievalCaseResult(
                    query=case.query,
                    retrieved_chunk_ids=retrieved_ids,
                    recall_at_k=recall,
                    reciprocal_rank=reciprocal_rank,
                    evidence_coverage=evidence_coverage,
                )
            )
        return RetrievalEvaluation(
            cases=results,
            mean_recall_at_k=sum(item.recall_at_k for item in results) / len(results),
            mean_reciprocal_rank=sum(item.reciprocal_rank for item in results) / len(results),
            mean_evidence_coverage=sum(item.evidence_coverage for item in results) / len(results),
        )


def combine_lexical_and_dense_scores(
    hits: Iterable[RetrievalHit],
    dense_scores: Mapping[str, float],
    *,
    lexical_weight: float = 0.7,
) -> list[RetrievalHit]:
    """Fuse externally supplied scores without claiming an embedding implementation."""
    if not 0 <= lexical_weight <= 1:
        raise ValueError("lexical_weight must be between 0 and 1")
    combined: list[RetrievalHit] = []
    for hit in hits:
        dense_score = min(1.0, max(0.0, dense_scores.get(hit.chunk.chunk_id, 0.0)))
        score = lexical_weight * hit.score + (1 - lexical_weight) * dense_score
        combined.append(hit.model_copy(update={"score": score}))
    combined.sort(key=lambda hit: (-hit.score, hit.chunk.chunk_id))
    return [hit.model_copy(update={"rank": rank}) for rank, hit in enumerate(combined, start=1)]


def _tokenize(text: str) -> list[str]:
    return [match.group(0).lower() for match in _TOKEN_PATTERN.finditer(text)]
