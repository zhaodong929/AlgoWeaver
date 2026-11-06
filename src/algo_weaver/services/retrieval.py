"""Dependency-free lexical chunking and retrieval baseline."""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from collections.abc import Iterable, Mapping

from algo_weaver.schemas.ingestion import IngestedSource
from algo_weaver.schemas.retrieval import EvidenceChunk, RetrievalHit

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


def _tokenize(text: str) -> list[str]:
    return [match.group(0).lower() for match in _TOKEN_PATTERN.finditer(text)]
