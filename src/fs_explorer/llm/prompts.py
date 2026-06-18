"""Compact action-format instructions for OpenAI-compatible models."""


def action_schema_instructions() -> str:
    """Return JSON action format guidance for chat-completions backends."""
    return """
You MUST respond with exactly one JSON object containing `action` and `reason`.

Stop when you have the final answer:
{"action": {"final_result": "Your answer with citations"}, "reason": "Why you are done"}

Call a tool:
{"action": {"tool_name": "scan_folder", "tool_input": [{"parameter_name": "directory", "parameter_value": "/path"}]}, "reason": "Why this tool"}

Navigate into a subdirectory:
{"action": {"directory": "/path/to/subdir"}, "reason": "Why go deeper"}

Ask the user a clarifying question:
{"action": {"question": "Your question"}, "reason": "Why you need input"}

Allowed tool_name values:
read, grep, glob, scan_folder, preview_file, parse_file, semantic_search, get_document, list_indexed_documents

Rules:
- Output JSON only. No markdown fences.
- tool_input must be a list of {"parameter_name": ..., "parameter_value": ...} objects.
- Use stop only when you can answer the user's task.
"""
