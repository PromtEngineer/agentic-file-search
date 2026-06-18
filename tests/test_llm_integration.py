"""Optional live integration tests for configured LLM providers."""

from __future__ import annotations

import os

import pytest

from fs_explorer.agent import FsExplorerAgent
from fs_explorer.models import StopAction


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("SILICONFLOW_API_KEY"),
    reason="SILICONFLOW_API_KEY not set",
)
async def test_siliconflow_take_action_stop() -> None:
    os.environ["FS_EXPLORER_LLM_PROVIDER"] = "siliconflow"
    agent = FsExplorerAgent()
    agent.configure_task(
        "Respond with a stop action. final_result should be exactly: siliconflow-ok"
    )
    result = await agent.take_action()
    assert result is not None
    action, action_type = result
    assert action_type == "stop"
    assert isinstance(action.action, StopAction)
    assert "siliconflow-ok" in action.action.final_result.lower()
