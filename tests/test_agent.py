import pytest
import os

from unittest.mock import patch
from google.genai import Client as GenAIClient
from google.genai.types import HttpOptions
from fs_explorer.agent import FsExplorerAgent, SYSTEM_PROMPT
from fs_explorer.models import Action, StopAction
from .conftest import MockGenAIClient


@patch.dict(os.environ, {"GOOGLE_API_KEY": "test-api-key"})
def test_agent_init():
    agent = FsExplorerAgent()
    assert isinstance(agent._client, GenAIClient)
    assert len(agent._chat_history) == 1
    assert agent._chat_history[0].role == "system"
    assert isinstance(agent._chat_history[0].parts, list)
    assert agent._chat_history[0].parts[0].text == SYSTEM_PROMPT
    del os.environ["GOOGLE_API_KEY"]
    with pytest.raises(ValueError):
        FsExplorerAgent()


@patch.dict(os.environ, {"GOOGLE_API_KEY": "test-api-key"})
def test_agent_configure_task():
    agent = FsExplorerAgent()
    agent.configure_task("this is a task")
    assert len(agent._chat_history) == 2
    assert isinstance(agent._chat_history[1].parts, list)
    assert agent._chat_history[1].parts[0].text == "this is a task"


@pytest.mark.asyncio
@patch.dict(os.environ, {"GOOGLE_API_KEY": "test-api-key"})
async def test_agent_take_action():
    agent = FsExplorerAgent()
    agent.configure_task("this is a task")
    agent._client = MockGenAIClient(  # type: ignore
        os.getenv("GOOGLE_API_KEY", ""), http_options=HttpOptions(api_version="v1beta")
    )
    result = await agent.take_action()
    assert result is not None
    action, action_type = result
    assert isinstance(action, Action)
    assert isinstance(action.action, StopAction)
    assert action.action.final_result == "this is a final result"
    assert action.reason == "I am done"
    assert action_type == "stop"
