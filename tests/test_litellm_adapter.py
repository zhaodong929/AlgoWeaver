from types import SimpleNamespace

import litellm
import pytest

from algo_weaver.config import Settings
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


def test_complete_json_uses_provider_neutral_settings(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_completion(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content='{"name":"demo"}'))]
        )

    monkeypatch.setattr(litellm, "completion", fake_completion)
    model = LiteLLMChatModel(
        Settings(
            llm_mode="litellm",
            llm_model="openai/test-model",
            llm_api_key="test-key",
            llm_api_base="http://localhost:9999/v1",
            llm_temperature=0.0,
            llm_timeout_seconds=12.0,
        )
    )

    assert model.complete_json(system_prompt="system", user_prompt="user") == '{"name":"demo"}'
    assert captured["model"] == "openai/test-model"
    assert captured["temperature"] == 0.0
    assert captured["timeout"] == 12.0
    assert captured["api_base"] == "http://localhost:9999/v1"
