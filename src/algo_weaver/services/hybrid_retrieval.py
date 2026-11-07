"""Hybrid lexical and semantic retrieval over provenance-preserving chunks."""

from __future__ import annotations

from collections.abc import Sequence

from algo_weaver.schemas.retrieval import EvidenceChunk, RetrievalHit
from algo_weaver.services.embedding import EmbeddingProvider
from algo_weaver.services.qdrant_retrieval import QdrantVectorRetriever
from algo_weaver.services.reranker import RerankerProvider
from algo_weaver.services.retrieval import LocalLexicalRetriever


class HybridRetriever:
    """Fuse lexical and embedding retrieval, then optionally rerank candidates."""

    def __init__(
        self,
        chunks: Sequence[EvidenceChunk],
        embedding_provider: EmbeddingProvider,
        *,
        reranker_provider: RerankerProvider | None = None,
        lexical_weight: float = 0.7,
    ) -> None:
        if not 0 <= lexical_weight <= 1:
            raise ValueError("lexical_weight must be between 0 and 1")
        self.chunks = list(chunks)
        self.embedding_provider = embedding_provider
        self.reranker_provider = reranker_provider
        self.lexical_weight = lexical_weight

    def search(self, query: str, *, top_k: int = 5) -> list[RetrievalHit]:
        if not query.strip():
            raise ValueError("query cannot be empty")
        if top_k < 1:
            raise ValueError("top_k must be positive")
        if not self.chunks:
            return []

        candidate_k = max(top_k * 4, top_k)
        lexical_hits = LocalLexicalRetriever(self.chunks).search(query, top_k=candidate_k)
        document_vectors = self.embedding_provider.embed([chunk.text for chunk in self.chunks])
        query_vector = self.embedding_provider.embed([query])
        if len(query_vector) != 1:
            raise ValueError("embedding provider must return one query vector")
        if len(document_vectors) != len(self.chunks):
            raise ValueError("embedding provider returned an unexpected document count")

        vector_retriever = QdrantVectorRetriever(len(query_vector[0]))
        vector_retriever.upsert(self.chunks, document_vectors)
        dense_hits = vector_retriever.search(query_vector[0], top_k=candidate_k)

        lexical_by_id = {hit.chunk.chunk_id: hit for hit in lexical_hits}
        dense_by_id = {hit.chunk.chunk_id: hit for hit in dense_hits}
        candidate_ids = set(lexical_by_id) | set(dense_by_id)
        fused: list[RetrievalHit] = []
        for chunk_id in candidate_ids:
            lexical_hit = lexical_by_id.get(chunk_id)
            dense_hit = dense_by_id.get(chunk_id)
            base = lexical_hit or dense_hit
            if base is None:
                continue
            lexical_score = lexical_hit.score if lexical_hit is not None else 0.0
            dense_score = dense_hit.score if dense_hit is not None else 0.0
            fused.append(
                base.model_copy(
                    update={
                        "score": self.lexical_weight * lexical_score
                        + (1 - self.lexical_weight) * dense_score,
                        "matched_terms": lexical_hit.matched_terms if lexical_hit else [],
                    }
                )
            )
        fused.sort(key=lambda hit: (-hit.score, hit.chunk.chunk_id))
        fused = [hit.model_copy(update={"rank": rank}) for rank, hit in enumerate(fused, start=1)]

        if self.reranker_provider is not None and fused:
            reranked = self.reranker_provider.rerank(
                query,
                [hit.chunk.text for hit in fused[:candidate_k]],
                top_k=min(candidate_k, len(fused)),
            )
            reranked_hits = [
                fused[item.index].model_copy(update={"score": item.score})
                for item in reranked
                if 0 <= item.index < len(fused)
            ]
            fused = reranked_hits

        return [hit.model_copy(update={"rank": rank}) for rank, hit in enumerate(fused[:top_k], start=1)]
