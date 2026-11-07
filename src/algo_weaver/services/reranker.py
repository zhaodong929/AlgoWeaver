"""Provider-neutral document reranking adapters."""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Protocol

from algo_weaver.config import Settings
from algo_weaver.schemas.retrieval import RerankResult
from algo_weaver.services._dashscope import post_json

_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]")


class RerankerProvider(Protocol):
    """Minimal interface for reranking an existing candidate set."""

    def rerank(
        self,
        query: str,
        documents: Sequence[str],
        *,
        top_k: int | None = None,
    ) -> list[RerankResult]:
        """Return scores tied to original document indexes."""
        ...


class MockRerankerProvider:
    """Deterministic lexical overlap reranker for offline tests.

    This is intentionally modest: it keeps the system usable without a
    semantic service and makes the lexical fallback explicit and testable.
    """

    def rerank(
        self,
        query: str,
        documents: Sequence[str],
        *,
        top_k: int | None = None,
    ) -> list[RerankResult]:
        query_terms = set(_tokenize(_validate_query(query)))
        values = _validate_documents(documents)
        if not values:
            return []
        if top_k is not None and top_k < 1:
            raise ValueError("top_k must be positive")
        scored = [
            RerankResult(
                index=index,
                score=(
                    len(query_terms.intersection(_tokenize(document))) / len(query_terms)
                    if query_terms
                    else 0.0
                ),
                text=document,
            )
            for index, document in enumerate(values)
        ]
        scored.sort(key=lambda item: (-item.score, item.index))
        return scored[:top_k] if top_k is not None else scored


class DashScopeRerankerProvider:
    """Reranker adapter for DashScope's OpenAI-compatible endpoint."""

    endpoint_suffix = "/compatible-api/v1/reranks"

    def __init__(self, settings: Settings) -> None:
        self.model = settings.reranker_model
        self.api_base = settings.reranker_api_base.rstrip("/")
        self.api_key = settings.reranker_api_key
        self.timeout = settings.reranker_timeout_seconds

    @property
    def endpoint(self) -> str:
        base = self.api_base
        if base.endswith("/api/v1"):
            base = base[: -len("/api/v1")]
        return f"{base}{self.endpoint_suffix}"

    def rerank(
        self,
        query: str,
        documents: Sequence[str],
        *,
        top_k: int | None = None,
    ) -> list[RerankResult]:
        query_value = _validate_query(query)
        values = _validate_documents(documents)
        if not values:
            return []
        if top_k is not None and top_k < 1:
            raise ValueError("top_k must be positive")
        if self.api_key is None:
            raise ValueError("ALGOWEAVER_RERANKER_API_KEY is required for DashScope reranking")

        response = post_json(
            url=self.endpoint,
            api_key=self.api_key.get_secret_value(),
            payload={
                "model": self.model,
                "query": query_value,
                "documents": values,
                "top_n": top_k if top_k is not None else len(values),
                "return_documents": False,
            },
            timeout=self.timeout,
        )
        output = response.get("output")
        raw_results = output.get("results") if isinstance(output, dict) else response.get("results")
        if not isinstance(raw_results, list):
            raise ValueError("DashScope reranker response has an unexpected shape")

        results: list[RerankResult] = []
        seen: set[int] = set()
        for item in raw_results:
            if not isinstance(item, dict):
                raise ValueError("DashScope reranker response contains an invalid item")
            index = item.get("index")
            score = item.get("relevance_score", item.get("score"))
            if (
                not isinstance(index, int)
                or not 0 <= index < len(values)
                or index in seen
                or not isinstance(score, (int, float))
            ):
                raise ValueError("DashScope reranker response contains an invalid result")
            seen.add(index)
            results.append(RerankResult(index=index, score=float(score), text=values[index]))

        return results[:top_k] if top_k is not None else results


def create_reranker_provider(settings: Settings) -> RerankerProvider:
    """Construct the explicitly configured reranker provider."""

    if settings.reranker_mode == "mock":
        return MockRerankerProvider()
    if settings.reranker_mode == "dashscope":
        return DashScopeRerankerProvider(settings)
    raise ValueError(f"Unsupported reranker mode: {settings.reranker_mode}")


def _validate_query(query: str) -> str:
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query cannot be empty")
    return query


def _validate_documents(documents: Sequence[str]) -> list[str]:
    values = list(documents)
    if any(not isinstance(document, str) or not document.strip() for document in values):
        raise ValueError("documents must contain non-empty strings")
    return values


def _tokenize(text: str) -> list[str]:
    return [match.group(0).lower() for match in _TOKEN_PATTERN.finditer(text)]
