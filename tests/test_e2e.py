import pytest
import os

from workflows.testing import WorkflowTestRunner

SKIP_IF, SKIP_REASON = (
    os.getenv("GOOGLE_API_KEY") is None,
    "GOOGLE_API_KEY not available",
)


@pytest.mark.asyncio
@pytest.mark.skipif(condition=SKIP_IF, reason=SKIP_REASON)
async def test_e2e() -> None:
    from fs_explorer.workflow import (
        workflow,
        InputEvent,
        ExplorationEndEvent,
        ToolCallEvent,
        GoDeeperEvent,
    )

    start_event = InputEvent(
        task="Starting from the current directory, individuate the python file responsible for file system operations and explain what it does"
    )
    runner = WorkflowTestRunner(workflow=workflow)
    result = await runner.run(start_event=start_event)
    assert isinstance(result.result, ExplorationEndEvent)
    assert result.result.error is None
    assert result.result.final_result is not None
    assert len(result.collected) > 1
    assert ToolCallEvent in result.event_types or GoDeeperEvent in result.event_types
