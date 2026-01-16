"""
Workflow orchestration for the FsExplorer agent.

This module defines the event-driven workflow that coordinates the agent's
exploration of the filesystem, handling tool calls, directory navigation,
and human interaction.
"""

from workflows import Workflow, Context, step
from workflows.events import (
    StartEvent,
    StopEvent,
    Event,
    InputRequiredEvent,
    HumanResponseEvent,
)
from pydantic import BaseModel
from typing import cast, Any

from .agent import FsExplorerAgent
from .models import GoDeeperAction, ToolCallAction, StopAction, AskHumanAction, Action
from .fs import describe_dir_content

# Lazy agent initialization - created on first access
_AGENT: FsExplorerAgent | None = None


def get_agent() -> FsExplorerAgent:
    """Get or create the singleton agent instance."""
    global _AGENT
    if _AGENT is None:
        _AGENT = FsExplorerAgent()
    return _AGENT


def reset_agent() -> None:
    """Reset the agent's state for a new exploration (preserves instance for stats)."""
    global _AGENT
    if _AGENT is not None:
        _AGENT.reset()
    else:
        # Create agent if it doesn't exist
        _AGENT = FsExplorerAgent()


class WorkflowState(BaseModel):
    """State maintained throughout the workflow execution."""
    
    initial_task: str = ""
    current_directory: str = "."


class InputEvent(StartEvent):
    """Initial event containing the user's task."""
    
    task: str


class GoDeeperEvent(Event):
    """Event triggered when navigating into a subdirectory."""
    
    directory: str
    reason: str


class ToolCallEvent(Event):
    """Event triggered when executing a tool."""
    
    tool_name: str
    tool_input: dict[str, Any]
    reason: str


class AskHumanEvent(InputRequiredEvent):
    """Event triggered when human input is required."""
    
    question: str
    reason: str


class HumanAnswerEvent(HumanResponseEvent):
    """Event containing the human's response."""
    
    response: str


class ExplorationEndEvent(StopEvent):
    """Event signaling the end of exploration."""
    
    final_result: str | None = None
    error: str | None = None


# Type alias for the union of possible workflow events
WorkflowEvent = ExplorationEndEvent | GoDeeperEvent | ToolCallEvent | AskHumanEvent


def _handle_action_result(
    action: Action,
    action_type: str,
    ctx: Context[WorkflowState],
) -> WorkflowEvent:
    """
    Convert an action result into the appropriate workflow event.
    
    This helper extracts the common logic for handling agent action results,
    reducing code duplication across workflow steps.
    
    Args:
        action: The action returned by the agent
        action_type: The type of action ("godeeper", "toolcall", "askhuman", "stop")
        ctx: The workflow context for state updates and event streaming
    
    Returns:
        The appropriate workflow event based on the action type
    """
    if action_type == "godeeper":
        godeeper = cast(GoDeeperAction, action.action)
        event = GoDeeperEvent(directory=godeeper.directory, reason=action.reason)
        ctx.write_event_to_stream(event)
        return event
    
    elif action_type == "toolcall":
        toolcall = cast(ToolCallAction, action.action)
        event = ToolCallEvent(
            tool_name=toolcall.tool_name,
            tool_input=toolcall.to_fn_args(),
            reason=action.reason,
        )
        ctx.write_event_to_stream(event)
        return event
    
    elif action_type == "askhuman":
        askhuman = cast(AskHumanAction, action.action)
        # InputRequiredEvent is written to the stream by default
        return AskHumanEvent(question=askhuman.question, reason=action.reason)
    
    else:  # stop
        stopaction = cast(StopAction, action.action)
        return ExplorationEndEvent(final_result=stopaction.final_result)


async def _process_agent_action(
    agent: FsExplorerAgent,
    ctx: Context[WorkflowState],
    update_directory: bool = False,
) -> WorkflowEvent:
    """
    Process the agent's next action and return the appropriate event.
    
    Args:
        agent: The agent instance
        ctx: The workflow context
        update_directory: Whether to update the current directory on godeeper action
    
    Returns:
        The appropriate workflow event
    """
    result = await agent.take_action()
    
    if result is None:
        return ExplorationEndEvent(error="Could not produce action to take")
    
    action, action_type = result
    
    # Update directory state if needed for godeeper actions
    if update_directory and action_type == "godeeper":
        godeeper = cast(GoDeeperAction, action.action)
        async with ctx.store.edit_state() as state:
            state.current_directory = godeeper.directory
    
    return _handle_action_result(action, action_type, ctx)


class FsExplorerWorkflow(Workflow):
    """
    Event-driven workflow for filesystem exploration.
    
    Coordinates the agent's actions through a series of steps:
    - start_exploration: Initial task processing
    - go_deeper_action: Directory navigation
    - tool_call_action: Tool execution
    - receive_human_answer: Human interaction handling
    """
    
    @step
    async def start_exploration(
        self,
        ev: InputEvent,
        ctx: Context[WorkflowState],
    ) -> WorkflowEvent:
        """Initialize exploration with the user's task."""
        agent = get_agent()
        async with ctx.store.edit_state() as state:
            state.initial_task = ev.task

        dirdescription = describe_dir_content(".")
        agent.configure_task(
            f"Given that the current directory ('.') looks like this:\n\n"
            f"```text\n{dirdescription}\n```\n\n"
            f"And that the user is giving you this task: '{ev.task}', "
            f"what action should you take first?"
        )

        return await _process_agent_action(agent, ctx, update_directory=True)

    @step
    async def go_deeper_action(
        self,
        ev: GoDeeperEvent,
        ctx: Context[WorkflowState],
    ) -> WorkflowEvent:
        """Handle navigation into a subdirectory."""
        agent = get_agent()
        state = await ctx.store.get_state()
        dirdescription = describe_dir_content(state.current_directory)

        agent.configure_task(
            f"Given that the current directory ('{state.current_directory}') "
            f"looks like this:\n\n```text\n{dirdescription}\n```\n\n"
            f"And that the user is giving you this task: '{state.initial_task}', "
            f"what action should you take next?"
        )

        return await _process_agent_action(agent, ctx, update_directory=True)

    @step
    async def receive_human_answer(
        self,
        ev: HumanAnswerEvent,
        ctx: Context[WorkflowState],
    ) -> WorkflowEvent:
        """Process the human's response to a question."""
        agent = get_agent()
        state = await ctx.store.get_state()

        agent.configure_task(
            f"Human response to your question: {ev.response}\n\n"
            f"Based on it, proceed with your exploration based on the "
            f"original task: {state.initial_task}"
        )

        return await _process_agent_action(agent, ctx, update_directory=True)

    @step
    async def tool_call_action(
        self,
        ev: ToolCallEvent,
        ctx: Context[WorkflowState],
    ) -> WorkflowEvent:
        """Process the result of a tool call."""
        agent = get_agent()
        agent.configure_task(
            "Given the result from the tool call you just performed, "
            "what action should you take next?"
        )

        return await _process_agent_action(agent, ctx, update_directory=True)


# Workflow timeout for complex multi-document analysis (5 minutes)
WORKFLOW_TIMEOUT_SECONDS = 300

workflow = FsExplorerWorkflow(timeout=WORKFLOW_TIMEOUT_SECONDS)
