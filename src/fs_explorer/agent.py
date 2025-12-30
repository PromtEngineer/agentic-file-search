import os
from typing import Callable, Any, cast
from google.genai.types import Content, HttpOptions, Part
from google.genai import Client as GenAIClient
from .models import Action, ActionType, ToolCallAction, Tools
from .fs import read_file, grep_file_content, glob_paths, parse_file, check_api_key

TOOLS: dict[Tools, Callable] = {
    "read": read_file,
    "grep": grep_file_content,
    "glob": glob_paths,
    "check_api_key": check_api_key,
    "parse_file": parse_file,
}

SYSTEM_PROMPT = """
You are FsExplorer, an AI agent whose task is to help the user to explore the filesystem (starting from the current directory and, eventually, going deeper) in order to complete a given task.

Every time, you will be asked to take one of the following actions:

- Tool call - call one of the file-system tools available to you, specifically:
    + `read`: read a **text-based** file, providing its path (`file_path` parameter, a string)
    + `grep`: grep the content of a file, providing its path and the pattern (`file_path` and `pattern` parameters, both strings)
    + `glob`: list files within a directory that comply with a certain pattern, providing the directory path and the pattern to search for (`directory` and `pattern` parameters, both strings)
    + `check_api_key`: check whether or not the `LLAMA_CLOUD_API_KEY` is set before using the `parse_file` tool. No paramaeter needed for this tool. Use only once per session, as you can assume that the API key will not change status throughout the course of the session.
    + `parse_file`: read the content of an **unstructured file** (allowed extensions: .pdf, .doc, .docx, .pptx, .xlsx). Call only if `LLAMA_CLOUD_API_KEY` is set within the environment.
- Go deeper - go one level deeper in the filesystem, accessing a subfolder of the folder you are currently exploring
- Ask human - ask a question to the user in order to clarify their intent for a task or if you are uncertain about how to proceed when you reached a certain point. This should be treated as an emergency measure, and you should try to not use human help unless you **really** need it.
- Stop - you have reached your goal, so you can exit, returning to the user with a final result of all the operations

Choose the action based on the current situation, inferred from the previous chat history.
"""


class FsExplorerAgent:
    def __init__(self, api_key: str | None = None):
        if api_key is None:
            api_key = os.getenv("GOOGLE_API_KEY")
        if api_key is None:
            raise ValueError(
                "GOOGLE_API_KEY not found within the current environment: please export it or provide it to the class constructor."
            )
        self._client = GenAIClient(
            api_key=api_key, http_options=HttpOptions(api_version="v1")
        )
        self._chat_history: list[Content] = [
            Content(role="system", parts=[Part.from_text(text=SYSTEM_PROMPT)])
        ]

    def configure_task(self, task: str) -> None:
        self._chat_history.append(
            Content(role="user", parts=[Part.from_text(text=task)])
        )

    async def take_action(self) -> tuple[Action, ActionType] | None:
        response = await self._client.aio.models.generate_content(
            model="gemini-3-flash-preview",
            contents=self._chat_history,  # type: ignore
            config={
                "response_mime_type": "application/json",
                "response_json_schema": Action.model_json_schema(),
            },
        )
        if response.candidates is not None:
            if response.candidates[0].content is not None:
                self._chat_history.append(response.candidates[0].content)
            if response.text is not None:
                action = Action.model_validate_json(response.text)
                if action.to_action_type() == "toolcall":
                    toolcall = cast(ToolCallAction, action.action)
                    await self.call_tool(
                        tool_name=toolcall.tool_name, tool_input=toolcall.to_fn_args()
                    )
                return action, action.to_action_type()
        return None

    async def call_tool(self, tool_name: Tools, tool_input: dict[str, Any]) -> None:
        try:
            if tool_name != "parse_file":
                result = TOOLS[tool_name](**tool_input)
            else:
                result = await TOOLS[tool_name](**tool_input)
        except Exception as e:
            result = f"An error occurred while calling tool {tool_name} with {tool_input}: {e}"
        self._chat_history.append(
            Content(
                role="user",
                parts=[
                    Part.from_text(text=f"Tool result for {tool_name}:\n\n{result}")
                ],
            )
        )
        return None
