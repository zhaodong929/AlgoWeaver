"""LiteLLM adapter for OpenAI, DeepSeek, Qwen, Ollama, and compatible APIs."""

from __future__ import annotations

import json
import re
from typing import Any

from algo_weaver.config import Settings


class LiteLLMChatModel:
    """Provider-neutral adapter using LiteLLM's unified completion interface.

    Set llm_model using LiteLLM's provider/model format, for example:
    ``openai/<model>``, ``deepseek/<model>``, ``dashscope/<model>``, or
    ``ollama/<model>``. For OpenAI-compatible endpoints, use ``openai/<model>``
    together with ``ALGOWEAVER_LLM_API_BASE``.
    """

    def __init__(self, settings: Settings) -> None:
        if not settings.llm_model:
            raise ValueError("ALGOWEAVER_LLM_MODEL is required when LLM_MODE=litellm")
        self.settings = settings

    def complete_json(self, *, system_prompt: str, user_prompt: str) -> str:
        try:
            from litellm import completion
        except ImportError as exc:  # pragma: no cover - dependency is in core extras
            raise RuntimeError("LiteLLM is not installed. Run: uv sync") from exc

        kwargs: dict[str, Any] = {
            "model": self.settings.llm_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.settings.llm_temperature,
            "timeout": self.settings.llm_timeout_seconds,
        }
        if self.settings.llm_api_key:
            kwargs["api_key"] = self.settings.llm_api_key.get_secret_value()
        if self.settings.llm_api_base:
            kwargs["api_base"] = self.settings.llm_api_base

        response = completion(**kwargs)
        content = response.choices[0].message.content
        if isinstance(content, list):
            text_parts = [
                item.get("text", "")
                for item in content
                if isinstance(item, dict) and item.get("type") == "text"
            ]
            content = "\n".join(text_parts)
        if not isinstance(content, str) or not content.strip():
            raise ValueError("The model returned an empty or non-text response")
        return self._extract_json(content)

    @staticmethod
    def _extract_json(content: str) -> str:
        """Accept raw JSON or JSON wrapped in a Markdown code fence."""
        text = content.strip()
        fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.S | re.I)
        if fenced:
            text = fenced.group(1).strip()
        if text.startswith("{") and text.endswith("}"):
            json.loads(text)
            return text
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            candidate = text[start : end + 1]
            json.loads(candidate)
            return candidate
        raise ValueError("Model response does not contain a valid JSON object")
