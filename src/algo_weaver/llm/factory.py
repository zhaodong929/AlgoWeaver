"""Construct the configured chat model."""

from algo_weaver.config import Settings
from algo_weaver.llm.base import ChatModel
from algo_weaver.llm.mock import MockChatModel


def create_chat_model(settings: Settings, *, model: str | None = None) -> ChatModel:
    if model:
        settings = settings.model_copy(update={"llm_model": model})
    if settings.llm_mode == "mock":
        return MockChatModel()
    if settings.llm_mode == "litellm":
        from algo_weaver.llm.litellm_adapter import LiteLLMChatModel

        return LiteLLMChatModel(settings)
    raise ValueError(f"Unsupported LLM mode: {settings.llm_mode}")
