"""
Pytest fixtures and mocks for FsExplorer tests.

Provides mock implementations of the LLM client for unit testing
without making actual API calls.
"""

from fs_explorer.llm.base import ChatMessage, LLMUsage
from fs_explorer.models import StopAction, Action


class MockLLMClient:
    """Mock LLM backend that always returns a stop action."""

    def __init__(self, provider_name: str = "google", model_name: str = "mock-model") -> None:
        self._provider_name = provider_name
        self._model_name = model_name

    @property
    def provider_name(self) -> str:
        return self._provider_name

    @property
    def model_name(self) -> str:
        return self._model_name

    async def generate_action_json(
        self,
        *,
        messages: list[ChatMessage],
        system_instruction: str,
    ) -> tuple[str, LLMUsage]:
        del messages, system_instruction
        payload = Action(
            action=StopAction(final_result="this is a final result"),
            reason="I am done",
        ).model_dump_json()
        return payload, LLMUsage(prompt_tokens=100, completion_tokens=50)
