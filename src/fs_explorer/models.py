from pydantic import BaseModel, Field
from typing import TypeAlias, Literal, Any

Tools: TypeAlias = Literal["read", "grep", "glob", "check_api_key", "parse_file"]
ActionType: TypeAlias = Literal["stop", "godeeper", "toolcall", "askhuman"]


class StopAction(BaseModel):
    """Action that is used when the end goal has been reached"""

    final_result: str = Field(description="Final result of the operation")


class AskHumanAction(BaseModel):
    """Action that is used when clarification from the user is needed on a task or on a file"""

    question: str = Field(description="Clarification question to ask to the user.")


class GoDeeperAction(BaseModel):
    """Action that is used when it is necessary to go one level deeper in the filesystem"""

    directory: str = Field(description="Directory where to go")


class ToolCallArg(BaseModel):
    """Input to the tool call, based on the tool schema"""

    parameter_name: str = Field(description="Name of the parameter")
    parameter_value: Any = Field(description="Value associated to the parameter")


class ToolCallAction(BaseModel):
    """Action thast is used when it is necessary to call one of the available tools"""

    tool_name: Tools = Field(description="Chosen tool")
    tool_input: list[ToolCallArg] = Field(description="Input to call the tool with")

    def to_fn_args(self) -> dict[str, Any]:
        args = {}
        for arg in self.tool_input:
            args[arg.parameter_name] = arg.parameter_value
        return args


class Action(BaseModel):
    """Action to take based on the current chat history"""

    action: ToolCallAction | GoDeeperAction | StopAction | AskHumanAction = Field(
        description="Action specification for the next step"
    )
    reason: str = Field(description="Reason for taking this specific action")

    def to_action_type(self) -> ActionType:
        if isinstance(self.action, ToolCallAction):
            return "toolcall"
        elif isinstance(self.action, GoDeeperAction):
            return "godeeper"
        elif isinstance(self.action, AskHumanAction):
            return "askhuman"
        else:
            return "stop"
