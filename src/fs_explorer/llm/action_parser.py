"""Parse agent actions from LLM JSON with flexible recovery."""

from __future__ import annotations

import json
from typing import cast

from ..models import (
    Action,
    ActionType,
    AskHumanAction,
    GoDeeperAction,
    StopAction,
    ToolCallAction,
    ToolCallArg,
    Tools,
)


def parse_action_json(json_str: str) -> tuple[Action, ActionType]:
    """Parse an action from JSON, with flexible recovery for weaker models."""
    try:
        action = Action.model_validate_json(json_str)
        return action, action.to_action_type()
    except Exception:
        pass

    try:
        raw = json.loads(json_str)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {json_str[:200]}") from exc

    action_data = raw.get("action", {})
    reason = raw.get("reason", "")

    if isinstance(action_data, dict) and "final_result" in action_data:
        return Action(
            action=StopAction(final_result=str(action_data["final_result"])),
            reason=str(reason),
        ), "stop"

    if isinstance(action_data, dict) and action_data.get("tool_name") == "final_result":
        answer = reason or str(action_data.get("tool_input", ""))
        return Action(
            action=StopAction(final_result=answer),
            reason="Recovered: tool_name was final_result",
        ), "stop"

    if isinstance(action_data, dict) and "directory" in action_data and "tool_name" not in action_data:
        return Action(
            action=GoDeeperAction(directory=str(action_data["directory"])),
            reason=str(reason),
        ), "godeeper"

    if isinstance(action_data, dict) and "question" in action_data:
        return Action(
            action=AskHumanAction(question=str(action_data["question"])),
            reason=str(reason),
        ), "askhuman"

    if not isinstance(action_data, dict):
        raise ValueError(f"Unsupported action payload: {json_str[:200]}")

    tool_name = action_data.get("tool_name")
    tool_input_raw = action_data.get("tool_input", [])
    if not tool_name:
        raise ValueError(f"Missing tool_name in action: {json_str[:200]}")

    args = _normalize_tool_args(tool_input_raw)
    tool = cast(Tools, tool_name)
    return Action(
        action=ToolCallAction(tool_name=tool, tool_input=args),
        reason=str(reason),
    ), "toolcall"


def _normalize_tool_args(tool_input_raw: object) -> list[ToolCallArg]:
    if isinstance(tool_input_raw, dict):
        return [
            ToolCallArg(parameter_name=str(key), parameter_value=value)
            for key, value in tool_input_raw.items()
        ]

    if not isinstance(tool_input_raw, list):
        return []

    args: list[ToolCallArg] = []
    for item in tool_input_raw:
        if isinstance(item, ToolCallArg):
            args.append(item)
        elif isinstance(item, dict):
            if "parameter_name" in item and "parameter_value" in item:
                args.append(
                    ToolCallArg(
                        parameter_name=str(item["parameter_name"]),
                        parameter_value=item["parameter_value"],
                    )
                )
            elif len(item) == 1:
                key, value = next(iter(item.items()))
                args.append(
                    ToolCallArg(parameter_name=str(key), parameter_value=value)
                )
            else:
                for key, value in item.items():
                    args.append(
                        ToolCallArg(parameter_name=str(key), parameter_value=value)
                    )
    return args
