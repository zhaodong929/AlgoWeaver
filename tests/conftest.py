import pytest

from algo_weaver.llm.mock import MockChatModel
from algo_weaver.services.capability_extractor import CapabilityExtractor


@pytest.fixture
def extractor() -> CapabilityExtractor:
    return CapabilityExtractor(MockChatModel())
