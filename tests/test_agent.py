"""Tests for the FsExplorerAgent class."""

import pytest
import os

from unittest.mock import patch

from fs_explorer.agent import (
    FsExplorerAgent,
    SYSTEM_PROMPT,
    TokenUsage,
    _build_system_prompt,
    set_search_flags,
    get_search_flags,
    clear_index_context,
)
from fs_explorer.models import Action, StopAction
from .conftest import MockLLMClient


class TestAgentInitialization:
    """Tests for agent initialization."""

    @patch.dict(os.environ, {"GOOGLE_API_KEY": "test-api-key", "FS_EXPLORER_LLM_PROVIDER": "google"})
    def test_agent_init_with_env_key(self) -> None:
        """Test agent initialization with API key from environment."""
        agent = FsExplorerAgent()
        assert agent.llm_client.provider_name == "google"
        assert len(agent._chat_history) == 0
        assert isinstance(agent.token_usage, TokenUsage)

    @patch.dict(os.environ, {"FS_EXPLORER_LLM_PROVIDER": "google"})
    def test_agent_init_with_explicit_key(self) -> None:
        """Test agent initialization with explicit API key."""
        agent = FsExplorerAgent(api_key="explicit-test-key")
        assert agent.llm_client.provider_name == "google"

    @patch.dict(
        os.environ,
        {
            "FS_EXPLORER_LLM_PROVIDER": "siliconflow",
            "SILICONFLOW_API_KEY": "sf-test-key",
        },
        clear=False,
    )
    def test_agent_init_with_siliconflow(self) -> None:
        """Test siliconflow provider selection from environment."""
        agent = FsExplorerAgent()
        assert agent.llm_client.provider_name == "siliconflow"

    def test_agent_init_without_key_raises(self) -> None:
        """Test that initialization without API key raises ValueError."""
        env = os.environ.copy()
        for key in (
            "GOOGLE_API_KEY",
            "SILICONFLOW_API_KEY",
            "OPENAI_API_KEY",
            "FS_EXPLORER_LLM_PROVIDER",
        ):
            env.pop(key, None)

        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(ValueError, match="No API key found"):
                FsExplorerAgent()

    def test_agent_init_with_injected_client(self) -> None:
        """Test initialization with an injected mock client."""
        client = MockLLMClient(provider_name="mock")
        agent = FsExplorerAgent(llm_client=client)
        assert agent.llm_client is client


class TestAgentConfiguration:
    """Tests for agent task configuration."""

    def test_configure_task_adds_to_history(self) -> None:
        """Test that configure_task adds message to chat history."""
        agent = FsExplorerAgent(llm_client=MockLLMClient())
        agent.configure_task("this is a task")

        assert len(agent._chat_history) == 1
        assert agent._chat_history[0].role == "user"
        assert agent._chat_history[0].content == "this is a task"

    def test_multiple_configure_task_calls(self) -> None:
        """Test that multiple configure_task calls accumulate."""
        agent = FsExplorerAgent(llm_client=MockLLMClient())
        agent.configure_task("task 1")
        agent.configure_task("task 2")

        assert len(agent._chat_history) == 2
        assert agent._chat_history[0].content == "task 1"
        assert agent._chat_history[1].content == "task 2"


class TestAgentActions:
    """Tests for agent action handling."""

    @pytest.mark.asyncio
    async def test_take_action_returns_action(self) -> None:
        """Test that take_action returns an action from the model."""
        agent = FsExplorerAgent(llm_client=MockLLMClient())
        agent.configure_task("this is a task")

        result = await agent.take_action()

        assert result is not None
        action, action_type = result
        assert isinstance(action, Action)
        assert isinstance(action.action, StopAction)
        assert action.action.final_result == "this is a final result"
        assert action.reason == "I am done"
        assert action_type == "stop"

    def test_reset_clears_history(self) -> None:
        """Test that reset clears chat history and token usage."""
        agent = FsExplorerAgent(llm_client=MockLLMClient())
        agent.configure_task("task 1")
        agent.token_usage.api_calls = 5

        agent.reset()

        assert len(agent._chat_history) == 0
        assert agent.token_usage.api_calls == 0


class TestTokenUsage:
    """Tests for TokenUsage tracking."""

    def test_add_api_call(self) -> None:
        """Test adding API call metrics."""
        usage = TokenUsage()
        usage.add_api_call(100, 50, provider_name="google", model_name="gemini")

        assert usage.prompt_tokens == 100
        assert usage.completion_tokens == 50
        assert usage.total_tokens == 150
        assert usage.api_calls == 1
        assert usage.provider_name == "google"

    def test_add_tool_result_parse_file(self) -> None:
        """Test tracking parse_file tool usage."""
        usage = TokenUsage()
        usage.add_tool_result("document content here", "parse_file")

        assert usage.documents_parsed == 1
        assert usage.tool_result_chars == len("document content here")

    def test_add_tool_result_scan_folder(self) -> None:
        """Test tracking scan_folder tool usage."""
        usage = TokenUsage()
        result = "│ [1/3] doc1.pdf\n│ [2/3] doc2.pdf\n│ [3/3] doc3.pdf"
        usage.add_tool_result(result, "scan_folder")

        assert usage.documents_scanned == 3

    def test_summary_format(self) -> None:
        """Test that summary produces formatted output."""
        usage = TokenUsage(provider_name="google", model_name="gemini")
        usage.add_api_call(1000, 500)

        summary = usage.summary()

        assert "TOKEN USAGE SUMMARY" in summary
        assert "1,000" in summary
        assert "API Calls:" in summary
        assert "Est. Cost" in summary


class TestSystemPrompt:
    """Tests for system prompt configuration."""

    def test_system_prompt_contains_tools(self) -> None:
        """Test that system prompt documents all tools."""
        assert "scan_folder" in SYSTEM_PROMPT
        assert "preview_file" in SYSTEM_PROMPT
        assert "parse_file" in SYSTEM_PROMPT
        assert "read" in SYSTEM_PROMPT
        assert "grep" in SYSTEM_PROMPT
        assert "glob" in SYSTEM_PROMPT

    def test_system_prompt_contains_strategy(self) -> None:
        """Test that system prompt includes exploration strategy."""
        assert "Three-Phase" in SYSTEM_PROMPT or "PHASE" in SYSTEM_PROMPT
        assert "Parallel Scan" in SYSTEM_PROMPT or "PARALLEL" in SYSTEM_PROMPT
        assert "Backtracking" in SYSTEM_PROMPT or "BACKTRACK" in SYSTEM_PROMPT

    def test_system_prompt_contains_index_tools(self) -> None:
        """Test that system prompt documents index-aware tools."""
        assert "semantic_search" in SYSTEM_PROMPT
        assert "get_document" in SYSTEM_PROMPT
        assert "list_indexed_documents" in SYSTEM_PROMPT


class TestSearchFlags:
    """Tests for search flag state and dynamic system prompt."""

    def setup_method(self) -> None:
        clear_index_context()

    def teardown_method(self) -> None:
        clear_index_context()

    def test_set_and_get_search_flags(self) -> None:
        assert get_search_flags() == (False, False)
        set_search_flags(enable_semantic=True, enable_metadata=False)
        assert get_search_flags() == (True, False)
        set_search_flags(enable_semantic=False, enable_metadata=False)
        assert get_search_flags() == (False, False)

    def test_clear_index_context_resets_flags(self) -> None:
        set_search_flags(enable_semantic=True, enable_metadata=True)
        clear_index_context()
        assert get_search_flags() == (False, False)

    def test_build_system_prompt_no_index(self) -> None:
        prompt = _build_system_prompt(False, False)
        assert prompt == SYSTEM_PROMPT

    def test_build_system_prompt_semantic_only(self) -> None:
        prompt = _build_system_prompt(True, False)
        assert "Semantic Only" in prompt
        assert "WITHOUT the `filters`" in prompt

    def test_build_system_prompt_metadata_only(self) -> None:
        prompt = _build_system_prompt(False, True)
        assert "Metadata Only" in prompt
        assert "metadata filtering" in prompt

    def test_build_system_prompt_both(self) -> None:
        prompt = _build_system_prompt(True, True)
        assert "Semantic + Metadata" in prompt

    def test_all_tools_always_available(self) -> None:
        """Filesystem and indexed tools are never blocked."""
        set_search_flags(enable_semantic=False, enable_metadata=False)
        agent = FsExplorerAgent(llm_client=MockLLMClient())
        agent.configure_task("test")
        agent.call_tool("glob", {"directory": "/tmp", "pattern": "*.md"})

        last = agent._chat_history[-1]
        assert "not available" not in last.content
