"""Optional Qdrant adapter using the existing provenance chunk contract."""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from typing import Any

from algo_weaver.config import Settings
from algo_weaver.schemas.retrieval import EvidenceChunk, RetrievalHit


class QdrantVectorRetriever:
    """Store externally supplied vectors and return provenance-preserving hits."""

    def __init__(
        self,
        dimension: int,
        *,
        collection_name: str = "algo_weaver_chunks",
        client: Any | None = None,
        url: str | None = None,
        api_key: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        if dimension < 1:
            raise ValueError("dimension must be positive")
        try:
            from qdrant_client import QdrantClient, models
        except ModuleNotFoundError as exc:  # pragma: no cover - optional extra boundary
            raise RuntimeError("Qdrant retrieval requires the optional 'retrieval' extra") from exc

        self.dimension = dimension
        self.collection_name = collection_name
        self._models = models
        if client is not None and (url is not None or api_key is not None):
            raise ValueError("client cannot be combined with url or api_key")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        if client is not None:
            self.client = client
        elif url is not None:
            self.client = QdrantClient(
                url=url,
                api_key=api_key,
                timeout=max(1, int(timeout)),
            )
        else:
            self.client = QdrantClient(":memory:")
        if not self.client.collection_exists(collection_name):
            self.client.create_collection(
                collection_name,
                vectors_config=models.VectorParams(
                    size=dimension,
                    distance=models.Distance.COSINE,
                ),
            )

    def upsert(self, chunks: Sequence[EvidenceChunk], vectors: Sequence[Sequence[float]]) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("chunks and vectors must have the same length")
        points = []
        for chunk, vector in zip(chunks, vectors, strict=True):
            if len(vector) != self.dimension:
                raise ValueError("vector dimension does not match the collection")
            points.append(
                self._models.PointStruct(
                    id=_point_id(chunk.chunk_id),
                    vector=list(vector),
                    payload={"chunk": chunk.model_dump(mode="json")},
                )
            )
        if points:
            self.client.upsert(self.collection_name, points=points)

    def search(self, vector: Sequence[float], *, top_k: int = 5) -> list[RetrievalHit]:
        if len(vector) != self.dimension:
            raise ValueError("vector dimension does not match the collection")
        if top_k < 1:
            raise ValueError("top_k must be positive")
        points = self.client.query_points(
            self.collection_name,
            query=list(vector),
            limit=top_k,
            with_payload=True,
        ).points
        hits: list[RetrievalHit] = []
        for rank, point in enumerate(points, start=1):
            payload = point.payload or {}
            chunk = EvidenceChunk.model_validate(payload["chunk"])
            hits.append(
                RetrievalHit(
                    rank=rank,
                    score=max(0.0, float(point.score or 0.0)),
                    chunk=chunk,
                )
            )
        return hits


def create_qdrant_retriever(settings: Settings, dimension: int) -> QdrantVectorRetriever:
    """Create a Qdrant adapter from application settings.

    ``memory`` is the default for tests and offline demos. ``server`` connects
    to a persistent Qdrant service such as the repository's Docker Compose
    service and keeps the same provenance contract.
    """

    if settings.qdrant_mode == "memory":
        return QdrantVectorRetriever(
            dimension,
            collection_name=settings.qdrant_collection_name,
        )
    if settings.qdrant_mode == "server":
        return QdrantVectorRetriever(
            dimension,
            collection_name=settings.qdrant_collection_name,
            url=settings.qdrant_url,
            api_key=(
                settings.qdrant_api_key.get_secret_value()
                if settings.qdrant_api_key is not None
                else None
            ),
            timeout=settings.qdrant_timeout_seconds,
        )
    raise ValueError(f"Unsupported Qdrant mode: {settings.qdrant_mode}")


def _point_id(chunk_id: str) -> int:
    return int(hashlib.sha256(chunk_id.encode("utf-8")).hexdigest()[:15], 16)
