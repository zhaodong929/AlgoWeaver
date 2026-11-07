"""Provider-neutral text embedding adapters.

The local mock is deterministic and intended for tests.  The DashScope
adapter is an explicit HTTP boundary; lexical retrieval remains the default
retrieval path when no dense provider is selected.
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Sequence
from typing import Protocol

from algo_weaver.config import Settings
from algo_weaver.services._dashscope import post_json


class EmbeddingProvider(Protocol):
    """Minimal interface consumed by a dense retrieval implementation."""

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        """Return one vector for each input text, in input order."""
        ...


class MockEmbeddingProvider:
    """Deterministic hash embeddings for offline tests and local development."""

    def __init__(self, *, dimensions: int = 8) -> None:
        if dimensions < 1:
            raise ValueError("dimensions must be positive")
        self.dimensions = dimensions

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in _validate_texts(texts)]

    def embed_query(self, text: str) -> list[float]:
        """Convenience method for query vectors."""
        return self.embed([text])[0]

    def _embed_one(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        raw = [
            (digest[index % len(digest)] / 127.5) - 1.0
            for index in range(self.dimensions)
        ]
        norm = math.sqrt(sum(value * value for value in raw))
        return [value / norm for value in raw] if norm else [0.0] * self.dimensions


class DashScopeEmbeddingProvider:
    """Embedding adapter for DashScope's text-embedding endpoint.

    No request is made until :meth:`embed` is called.  A missing key fails at
    this boundary rather than silently falling back to a mock result.
    """

    endpoint_suffix = "/services/embeddings/text-embedding/text-embedding"

    def __init__(self, settings: Settings) -> None:
        self.model = settings.embedding_model
        self.api_base = settings.embedding_api_base.rstrip("/")
        self.api_key = settings.embedding_api_key
        self.timeout = settings.embedding_timeout_seconds

    @property
    def endpoint(self) -> str:
        return f"{self.api_base}{self.endpoint_suffix}"

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        values = _validate_texts(texts)
        if not values:
            return []
        if self.api_key is None:
            raise ValueError("ALGOWEAVER_EMBEDDING_API_KEY is required for DashScope embeddings")

        response = post_json(
            url=self.endpoint,
            api_key=self.api_key.get_secret_value(),
            payload={"model": self.model, "input": {"texts": values}},
            timeout=self.timeout,
        )
        output = response.get("output")
        embeddings = output.get("embeddings") if isinstance(output, dict) else None
        if not isinstance(embeddings, list) or len(embeddings) != len(values):
            raise ValueError("DashScope embedding response has an unexpected shape")

        ordered: list[list[float] | None] = [None] * len(values)
        for item in embeddings:
            if not isinstance(item, dict):
                raise ValueError("DashScope embedding response contains an invalid item")
            # Older DashScope responses call this ``text_index``; the current
            # API documents the shorter ``index`` field.
            index = item.get("text_index", item.get("index"))
            vector = item.get("embedding")
            if not isinstance(index, int) or not 0 <= index < len(values):
                raise ValueError("DashScope embedding response contains an invalid text index")
            if not isinstance(vector, list) or not vector or not all(
                isinstance(value, (int, float)) and math.isfinite(value) for value in vector
            ):
                raise ValueError("DashScope embedding response contains an invalid vector")
            if ordered[index] is not None:
                raise ValueError("DashScope embedding response contains a duplicate text index")
            ordered[index] = [float(value) for value in vector]

        if any(vector is None for vector in ordered):
            raise ValueError("DashScope embedding response is missing a text index")
        result = [vector for vector in ordered if vector is not None]
        dimensions = len(result[0])
        if any(len(vector) != dimensions for vector in result):
            raise ValueError("DashScope embedding vectors have inconsistent dimensions")
        return result


def create_embedding_provider(settings: Settings) -> EmbeddingProvider:
    """Construct the explicitly configured embedding provider."""

    if settings.embedding_mode == "mock":
        return MockEmbeddingProvider()
    if settings.embedding_mode == "dashscope":
        return DashScopeEmbeddingProvider(settings)
    raise ValueError(f"Unsupported embedding mode: {settings.embedding_mode}")


def _validate_texts(texts: Sequence[str]) -> list[str]:
    values = list(texts)
    if any(not isinstance(text, str) or not text.strip() for text in values):
        raise ValueError("texts must contain non-empty strings")
    return values
