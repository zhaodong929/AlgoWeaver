"""Provider-neutral chat model interface."""

from typing import Protocol


class ChatModel(Protocol):
    """Minimal interface required by extraction services."""

    def complete_json(self, *, system_prompt: str, user_prompt: str) -> str:
        """Return a JSON object as text."""
        ...
