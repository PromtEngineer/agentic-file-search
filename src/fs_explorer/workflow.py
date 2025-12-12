from workflows import Workflow, Context, step
from workflows.events import StartEvent, StopEvent, Event
from workflows.resource import Resource
from pydantic import BaseModel
from typing import Annotated, cast, Any

from .agent import FsExplorerAgent
from .models import GoDeeperAction, ToolCallAction, StopAction
from .fs import describe_dir_content

AGENT = FsExplorerAgent()


class WorkflowState(BaseModel):
    intial_task: str = ""
    current_directory: str = "."


class InputEvent(StartEvent):
    task: str


class GoDeeperEvent(Event):
    directory: str
    reason: str


class ToolCallEvent(Event):
    tool_name: str
    tool_input: dict[str, Any]
    reason: str


class ExplorationEndEvent(StopEvent):
    final_result: str | None = None
    error: str | None = None


def get_agent(*args, **kwargs) -> FsExplorerAgent:
    return AGENT


class FsExplorerWorkflow(Workflow):
    @step
    async def start_exploration(
        self,
        ev: InputEvent,
        ctx: Context[WorkflowState],
        agent: Annotated[FsExplorerAgent, Resource(get_agent)],
    ) -> ExplorationEndEvent | GoDeeperEvent | ToolCallEvent:
        async with ctx.store.edit_state() as state:
            state.intial_task = ev.task
        dirdescription = describe_dir_content(".")
        agent.configure_task(
            f"Given that the current directory ('.') looks like this:\n\n```text\n{dirdescription}\n```\n\nAnd that the user is giving you this task: '{ev.task}', what action should you take first?"
        )
        result = await agent.take_action()
        if result is None:
            return ExplorationEndEvent(error="Could not produce action to take")
        action, action_type = result
        if action_type == "godeeper":
            godeeper = cast(GoDeeperAction, action.action)
            res = GoDeeperEvent(directory=godeeper.directory, reason=action.reason)
            async with ctx.store.edit_state() as state:
                state.current_directory = godeeper.directory
            ctx.write_event_to_stream(res)
        elif action_type == "toolcall":
            toolcall = cast(ToolCallAction, action.action)
            res = ToolCallEvent(
                tool_name=toolcall.tool_name,
                tool_input=toolcall.to_fn_args(),
                reason=action.reason,
            )
            ctx.write_event_to_stream(res)
        else:
            stopaction = cast(StopAction, action.action)
            res = ExplorationEndEvent(final_result=stopaction.final_result)
        return res

    @step
    async def go_deeper_action(
        self,
        ev: GoDeeperEvent,
        ctx: Context[WorkflowState],
        agent: Annotated[FsExplorerAgent, Resource(get_agent)],
    ) -> ExplorationEndEvent | ToolCallEvent | GoDeeperEvent:
        state = await ctx.store.get_state()
        dirdescription = describe_dir_content(state.current_directory)
        agent.configure_task(
            f"Given that the current directory ('{state.current_directory}') looks like this:\n\n```text\n{dirdescription}\n```\n\nAnd that the user is giving you this task: '{state.intial_task}', what action should you take next?"
        )
        result = await agent.take_action()
        if result is None:
            return ExplorationEndEvent(error="Could not produce action to take")
        action, action_type = result
        if action_type == "godeeper":
            godeeper = cast(GoDeeperAction, action.action)
            res = GoDeeperEvent(directory=godeeper.directory, reason=action.reason)
            async with ctx.store.edit_state() as state:
                state.current_directory = godeeper.directory
            ctx.write_event_to_stream(res)
        elif action_type == "toolcall":
            toolcall = cast(ToolCallAction, action.action)
            res = ToolCallEvent(
                tool_name=toolcall.tool_name,
                tool_input=toolcall.to_fn_args(),
                reason=action.reason,
            )
            ctx.write_event_to_stream(res)
        else:
            stopaction = cast(StopAction, action.action)
            res = ExplorationEndEvent(final_result=stopaction.final_result)
        return res

    @step
    async def tool_call_action(
        self,
        ev: ToolCallEvent,
        ctx: Context[WorkflowState],
        agent: Annotated[FsExplorerAgent, Resource(get_agent)],
    ) -> ExplorationEndEvent | ToolCallEvent | GoDeeperEvent:
        agent.configure_task(
            "Given the result from the tool call you just performed, what action should you take next?"
        )
        result = await agent.take_action()
        if result is None:
            return ExplorationEndEvent(error="Could not produce action to take")
        action, action_type = result
        if action_type == "godeeper":
            godeeper = cast(GoDeeperAction, action.action)
            res = GoDeeperEvent(directory=godeeper.directory, reason=action.reason)
            async with ctx.store.edit_state() as state:
                state.current_directory = godeeper.directory
            ctx.write_event_to_stream(res)
        elif action_type == "toolcall":
            toolcall = cast(ToolCallAction, action.action)
            res = ToolCallEvent(
                tool_name=toolcall.tool_name,
                tool_input=toolcall.to_fn_args(),
                reason=action.reason,
            )
            ctx.write_event_to_stream(res)
        else:
            stopaction = cast(StopAction, action.action)
            res = ExplorationEndEvent(final_result=stopaction.final_result)
        return res


workflow = FsExplorerWorkflow(timeout=120)
