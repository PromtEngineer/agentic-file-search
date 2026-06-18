"""Shared types for LLM provider adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ChatMessage:
    """Provider-neutral chat message."""

    role: str
    content: str


@dataclass(frozen=True)
class LLMUsage:
    """Token usage from a single LLM call."""

    prompt_tokens: int = 0
    completion_tokens: int = 0


class LLMClient(Protocol):
    """Interface implemented by all LLM backends."""

    @property
    def provider_name(self) -> str:
        """Human-readable provider id, e.g. google or siliconflow."""

    @property
    def model_name(self) -> str:
        """Model id sent to the provider API."""

    async def generate_action_json(
        self,
        *,
        messages: list[ChatMessage],
        system_instruction: str,
    ) -> tuple[str, LLMUsage]:
        """Return structured action JSON and token usage."""
