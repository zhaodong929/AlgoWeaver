import pytest

from algo_weaver.llm.mock import MockChatModel
from algo_weaver.services.capability_extractor import CapabilityExtractor


@pytest.fixture
def extractor() -> CapabilityExtractor:
    return CapabilityExtractor(MockChatModel())


@pytest.fixture(autouse=True)
def isolate_provider_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the offline suite deterministic when live user-level env is configured."""

    monkeypatch.setenv("ALGOWEAVER_LLM_MODE", "mock")
    monkeypatch.setenv("ALGOWEAVER_EMBEDDING_MODE", "mock")
    monkeypatch.setenv("ALGOWEAVER_RERANKER_MODE", "mock")
