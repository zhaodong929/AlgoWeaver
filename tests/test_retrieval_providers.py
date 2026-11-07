import json

import pytest

from algo_weaver.config import Settings
from algo_weaver.schemas.retrieval import RerankResult
from algo_weaver.services.embedding import (
    DashScopeEmbeddingProvider,
    MockEmbeddingProvider,
    create_embedding_provider,
)
from algo_weaver.services.reranker import (
    DashScopeRerankerProvider,
    MockRerankerProvider,
    create_reranker_provider,
)


class _Response:
    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload

    def __enter__(self) -> "_Response":
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def test_settings_expose_explicit_retrieval_provider_modes(monkeypatch) -> None:
    monkeypatch.setenv("ALGOWEAVER_EMBEDDING_MODE", "dashscope")
    monkeypatch.setenv("ALGOWEAVER_EMBEDDING_MODEL", "text-embedding-v4-test")
    monkeypatch.setenv("ALGOWEAVER_RERANKER_MODE", "dashscope")
    monkeypatch.setenv("ALGOWEAVER_RERANKER_MODEL", "qwen3-rerank-test")

    settings = Settings(_env_file=None)

    assert settings.embedding_mode == "dashscope"
    assert settings.embedding_model == "text-embedding-v4-test"
    assert settings.reranker_mode == "dashscope"
    assert settings.reranker_model == "qwen3-rerank-test"


def test_mock_embedding_is_deterministic_and_keeps_batch_order() -> None:
    provider = MockEmbeddingProvider(dimensions=4)

    first = provider.embed(["alpha", "beta"])
    second = provider.embed(["alpha", "beta"])

    assert first == second
    assert len(first) == 2
    assert all(len(vector) == 4 for vector in first)
    assert provider.embed_query("alpha") == first[0]


def test_mock_reranker_returns_original_indexes_and_top_k() -> None:
    results = MockRerankerProvider().rerank(
        "moving average",
        ["unrelated", "moving average validation", "moving"],
        top_k=2,
    )

    assert [result.index for result in results] == [1, 2]
    assert results[0].score > results[1].score
    assert all(isinstance(result, RerankResult) for result in results)


def test_dashscope_embedding_boundary_sends_batch_and_orders_response(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_urlopen(request, *, timeout):
        captured["url"] = request.full_url
        captured["headers"] = request.headers
        captured["payload"] = json.loads(request.data)
        captured["timeout"] = timeout
        return _Response(
            {
                "output": {
                    "embeddings": [
                        {"index": 1, "embedding": [0.2, 0.3]},
                        {"index": 0, "embedding": [0.4, 0.5]},
                    ]
                }
            }
        )

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    provider = DashScopeEmbeddingProvider(
        Settings(
            _env_file=None,
            embedding_mode="dashscope",
            embedding_model="text-embedding-v4-test",
            embedding_api_key="test-key",
            embedding_api_base="https://example.test/api/v1",
            embedding_timeout_seconds=13.0,
        )
    )

    assert provider.embed(["first", "second"]) == [[0.4, 0.5], [0.2, 0.3]]
    assert captured["url"] == (
        "https://example.test/api/v1/services/embeddings/text-embedding/text-embedding"
    )
    assert captured["payload"] == {
        "model": "text-embedding-v4-test",
        "input": {"texts": ["first", "second"]},
    }
    assert captured["timeout"] == 13.0


def test_dashscope_reranker_boundary_maps_scores_to_documents(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_post_json(*, url, api_key, payload, timeout):
        captured.update(url=url, api_key=api_key, payload=payload, timeout=timeout)
        return {"output": {"results": [{"index": 1, "relevance_score": 0.9}]}}

    monkeypatch.setattr("algo_weaver.services.reranker.post_json", fake_post_json)
    provider = DashScopeRerankerProvider(
        Settings(
            _env_file=None,
            reranker_mode="dashscope",
            reranker_model="qwen3-rerank-test",
            reranker_api_key="test-key",
            reranker_api_base="https://example.test/api/v1",
            reranker_timeout_seconds=9.0,
        )
    )

    results = provider.rerank("query", ["first", "second"], top_k=1)

    assert results == [RerankResult(index=1, score=0.9, text="second")]
    assert captured["url"] == "https://example.test/compatible-api/v1/reranks"
    assert captured["api_key"] == "test-key"
    assert captured["payload"] == {
        "model": "qwen3-rerank-test",
        "query": "query",
        "documents": ["first", "second"],
        "top_n": 1,
        "return_documents": False,
    }


def test_dashscope_provider_requires_a_key_without_network(monkeypatch) -> None:
    def fail_urlopen(*args, **kwargs):
        raise AssertionError("network should not be called")

    monkeypatch.setattr("urllib.request.urlopen", fail_urlopen)
    provider = DashScopeEmbeddingProvider(Settings(_env_file=None, embedding_mode="dashscope"))

    with pytest.raises(ValueError, match="EMBEDDING_API_KEY"):
        provider.embed(["text"])


def test_provider_factories_keep_mock_as_the_default() -> None:
    settings = Settings(_env_file=None)
    assert isinstance(create_embedding_provider(settings), MockEmbeddingProvider)
    assert isinstance(create_reranker_provider(settings), MockRerankerProvider)
