import json
import asyncio

from typer import Typer, Option
from typing import Annotated
from rich.markdown import Markdown
from rich.panel import Panel
from rich.console import Console

from .workflow import workflow, InputEvent, ToolCallEvent, GoDeeperAction

app = Typer()


async def run_workflow(task: str):
    console = Console()
    handler = workflow.run(start_event=InputEvent(task=task))
    with console.status(status="Working on your request...") as status:
        async for event in handler.stream_events():
            if isinstance(event, ToolCallEvent):
                status.update("Tool calling...")
                content = f"Calling tool `{event.tool_name}` with input:\n\n```\n{json.dumps(event.tool_input, indent=2)}\n```\n\nThe tool call is motivated by: {event.reason}"
                panel = Panel(
                    Markdown(content),
                    title_align="left",
                    title="Tool Call",
                    border_style="bold yellow",
                )
                console.print(panel)
                status.update("Working on the next move...")
            elif isinstance(event, GoDeeperAction):
                status.update("Tool calling...")
                content = f"Going to directory: `{event.directory}` because of: {event.reason}"
                panel = Panel(
                    Markdown(content),
                    title_align="left",
                    title="Moving within the file system",
                    border_style="bold magenta",
                )
                console.print(panel)
                status.update("Working on the next move...")
        result = await handler
        status.update("Gathering the final result...")
        await asyncio.sleep(0.1)
        status.update("Tool calling...")
        content = result.final_result
        panel = Panel(
            Markdown(content),
            title_align="left",
            title="Final result",
            border_style="bold green",
        )
        console.print(panel)
        status.stop()
    return None


@app.command()
def main(
    task: Annotated[
        str,
        Option(
            "--task",
            "-t",
            help="Task that the FsExplorer Agent has to perform while exploring the current directory.",
        ),
    ],
) -> None:
    asyncio.run(run_workflow(task))
