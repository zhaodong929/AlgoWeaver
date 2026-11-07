from algo_weaver.schemas.retrieval import EvidenceChunk
from algo_weaver.services.embedding import MockEmbeddingProvider
from algo_weaver.services.hybrid_retrieval import HybridRetriever
from algo_weaver.services.reranker import MockRerankerProvider


def _chunks() -> list[EvidenceChunk]:
    return [
        EvidenceChunk(
            chunk_id="chunk-1",
            source_id="doc",
            source_type="document",
            source_format="markdown",
            path="algorithm.md",
            text="moving average inventory demand forecast",
            line_start=1,
            line_end=1,
        ),
        EvidenceChunk(
            chunk_id="chunk-2",
            source_id="doc",
            source_type="document",
            source_format="markdown",
            path="algorithm.md",
            text="image classification model",
            line_start=2,
            line_end=2,
        ),
    ]


def test_hybrid_retriever_returns_provenance_hits() -> None:
    hits = HybridRetriever(
        _chunks(),
        MockEmbeddingProvider(dimensions=8),
    ).search("inventory forecast", top_k=1)

    assert len(hits) == 1
    assert hits[0].rank == 1
    assert hits[0].chunk.path == "algorithm.md"


def test_hybrid_retriever_applies_optional_reranker() -> None:
    hits = HybridRetriever(
        _chunks(),
        MockEmbeddingProvider(dimensions=8),
        reranker_provider=MockRerankerProvider(),
    ).search("inventory forecast", top_k=2)

    assert [hit.rank for hit in hits] == [1, 2]
    assert hits[0].score >= hits[1].score
