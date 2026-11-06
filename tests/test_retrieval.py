import pytest

from algo_weaver.schemas.ingestion import IngestedSource
from algo_weaver.services.retrieval import LocalLexicalRetriever, SourceChunker


def _source(source_id: str, content: str, source_type: str = "document") -> IngestedSource:
    return IngestedSource(
        source_id=source_id,
        path=f"{source_id}.md",
        source_type=source_type,
        source_format="markdown",
        content=content,
        content_sha256="a" * 64,
    )


def test_chunker_preserves_line_locations_and_metadata() -> None:
    chunks = SourceChunker().chunk(
        _source("doc-001", "moving average\nwindow parameter\nvalidation metric"),
        max_chars=20,
        overlap_lines=0,
    )

    assert len(chunks) == 3
    assert chunks[0].location == "doc-001.md:L1-L1"
    assert chunks[1].line_start == 2
    assert chunks[0].source_id == "doc-001"


def test_retriever_ranks_term_overlap_and_returns_provenance() -> None:
    chunker = SourceChunker()
    chunks = [
        *chunker.chunk(_source("doc-001", "moving average window validation")),
        *chunker.chunk(_source("code-001", "moving average implementation", "code")),
    ]

    hits = LocalLexicalRetriever(chunks).search("moving average validation", top_k=2)

    assert len(hits) == 2
    assert hits[0].chunk.source_id == "doc-001"
    assert hits[0].score > hits[1].score
    assert hits[0].chunk.location == "doc-001.md:L1-L1"
    assert "validation" in hits[0].matched_terms


def test_retriever_supports_source_and_metadata_filters() -> None:
    source = _source("doc-001", "Qdrant retrieval", "document")
    source.metadata["stage"] = "research"
    chunks = SourceChunker().chunk(source)
    retriever = LocalLexicalRetriever(chunks)

    assert retriever.search("retrieval", source_type="code") == []
    hits = retriever.search("retrieval", metadata_filter={"stage": "research"})
    assert hits[0].chunk.source_id == "doc-001"


def test_retriever_rejects_empty_query_and_bad_limits() -> None:
    retriever = LocalLexicalRetriever()
    with pytest.raises(ValueError, match="query cannot be empty"):
        retriever.search(" ")
    with pytest.raises(ValueError, match="top_k must be positive"):
        retriever.search("algorithm", top_k=0)
