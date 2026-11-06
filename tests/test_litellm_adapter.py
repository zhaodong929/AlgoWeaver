import pytest

from algo_weaver.llm.litellm_adapter import LiteLLMChatModel


def test_extract_json_from_markdown_fence() -> None:
    result = LiteLLMChatModel._extract_json('```json\n{"name": "demo"}\n```')
    assert result == '{"name": "demo"}'


def test_extract_json_from_surrounding_text() -> None:
    result = LiteLLMChatModel._extract_json('Result:\n{"name": "demo"}\nDone.')
    assert result == '{"name": "demo"}'


def test_reject_non_json_response() -> None:
    with pytest.raises(ValueError, match="valid JSON"):
        LiteLLMChatModel._extract_json("I cannot produce JSON")
