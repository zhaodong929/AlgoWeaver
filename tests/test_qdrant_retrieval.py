import pytest

pytest.importorskip("qdrant_client")

from algo_weaver.schemas.ingestion import IngestedSource
from algo_weaver.services.qdrant_retrieval import QdrantVectorRetriever
from algo_weaver.services.retrieval import SourceChunker


def test_qdrant_memory_adapter_preserves_chunk_provenance() -> None:
    source = IngestedSource(
        source_id="vector-doc",
        path="vector.md",
        source_type="document",
        source_format="markdown",
        content="first chunk\nsecond chunk",
        content_sha256="a" * 64,
    )
    chunks = SourceChunker().chunk(source, max_chars=12, overlap_lines=0)
    retriever = QdrantVectorRetriever(dimension=2)
    retriever.upsert(chunks, [[1.0, 0.0], [0.0, 1.0]])

    hits = retriever.search([0.9, 0.1], top_k=1)

    assert len(hits) == 1
    assert hits[0].chunk.source_id == "vector-doc"
    assert hits[0].chunk.location == "vector.md:L1-L1"
    assert hits[0].score > 0
