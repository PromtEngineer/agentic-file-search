"""
FsExplorer Agent for filesystem exploration using ProxyPal/OpenAI-compatible API.

This module contains the agent that interacts with an LLM (via ProxyPal)
to make decisions about filesystem exploration actions.
"""

import os
import json
from pathlib import Path
from typing import Callable, Any, cast
from dataclasses import dataclass

from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load .env file from project root
_env_path = Path(__file__).parent.parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)

from .models import Action, ActionType, ToolCallAction, Tools
from .fs import (
    read_file,
    grep_file_content,
    glob_paths,
    scan_folder,
    preview_file,
    parse_file,
)


# =============================================================================
# Token Usage Tracking
# =============================================================================

# Claude Sonnet pricing (per million tokens) - approximate
CLAUDE_SONNET_INPUT_COST_PER_MILLION = 3.00
CLAUDE_SONNET_OUTPUT_COST_PER_MILLION = 15.00


@dataclass
class TokenUsage:
    """
    Track token usage and costs across the session.

    Maintains running totals of API calls, token counts, and provides
    cost estimates based on Claude Sonnet pricing.
    """

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    api_calls: int = 0

    # Track content sizes
    tool_result_chars: int = 0
    documents_parsed: int = 0
    documents_scanned: int = 0

    def add_api_call(self, prompt_tokens: int, completion_tokens: int) -> None:
        """Record token usage from an API call."""
        self.prompt_tokens += prompt_tokens
        self.completion_tokens += completion_tokens
        self.total_tokens += prompt_tokens + completion_tokens
        self.api_calls += 1

    def add_tool_result(self, result: str, tool_name: str) -> None:
        """Record metrics from a tool execution."""
        self.tool_result_chars += len(result)
        if tool_name == "parse_file":
            self.documents_parsed += 1
        elif tool_name == "scan_folder":
            # Count documents in scan result by counting document markers
            self.documents_scanned += result.count("│ [")
        elif tool_name == "preview_file":
            self.documents_parsed += 1

    def _calculate_cost(self) -> tuple[float, float, float]:
        """Calculate estimated costs based on Claude Sonnet pricing."""
        input_cost = (
            self.prompt_tokens / 1_000_000
        ) * CLAUDE_SONNET_INPUT_COST_PER_MILLION
        output_cost = (
            self.completion_tokens / 1_000_000
        ) * CLAUDE_SONNET_OUTPUT_COST_PER_MILLION
        return input_cost, output_cost, input_cost + output_cost

    def summary(self) -> str:
        """Generate a formatted summary of token usage and costs."""
        input_cost, output_cost, total_cost = self._calculate_cost()

        return f"""
═══════════════════════════════════════════════════════════════
                      TOKEN USAGE SUMMARY
═══════════════════════════════════════════════════════════════
  API Calls:           {self.api_calls}
  Prompt Tokens:       {self.prompt_tokens:,}
  Completion Tokens:   {self.completion_tokens:,}
  Total Tokens:        {self.total_tokens:,}
───────────────────────────────────────────────────────────────
  Documents Scanned:   {self.documents_scanned}
  Documents Parsed:    {self.documents_parsed}
  Tool Result Chars:   {self.tool_result_chars:,}
───────────────────────────────────────────────────────────────
  Est. Cost (Claude Sonnet):
    Input:  ${input_cost:.4f}
    Output: ${output_cost:.4f}
    Total:  ${total_cost:.4f}
═══════════════════════════════════════════════════════════════
"""


# =============================================================================
# Tool Registry
# =============================================================================

TOOLS: dict[Tools, Callable[..., str]] = {
    "read": read_file,
    "grep": grep_file_content,
    "glob": glob_paths,
    "scan_folder": scan_folder,
    "preview_file": preview_file,
    "parse_file": parse_file,
}


# =============================================================================
# System Prompt
# =============================================================================

SYSTEM_PROMPT = """
You are FsExplorer, an AI agent that explores filesystems to answer user questions about documents.

## Available Tools

| Tool | Purpose | Parameters |
|------|---------|------------|
| `scan_folder` | **PARALLEL SCAN** - Scan ALL documents in a folder at once | `directory` |
| `preview_file` | Quick preview of a single document (~first page) | `file_path` |
| `parse_file` | **DEEP READ** - Full content of a document | `file_path` |
| `read` | Read a plain text file | `file_path` |
| `grep` | Search for a pattern in a file | `file_path`, `pattern` |
| `glob` | Find files matching a pattern | `directory`, `pattern` |

## Three-Phase Document Exploration Strategy

### PHASE 1: Parallel Scan (Use `scan_folder`)
When you encounter a folder with documents:
1. Use `scan_folder` to scan ALL documents in parallel
2. This gives you a quick preview of every document at once
3. In your **reason**, explicitly list your document categorization:
   - **RELEVANT**: Documents clearly related to the query (list them)
   - **MAYBE**: Documents that might be relevant (list them)
   - **SKIP**: Documents not relevant (list them)

**Categorization Guidelines:**
- **RELEVANT**: Preview contains query keywords OR filename clearly suggests relevance (e.g., "purchase_agreement.pdf" for a pricing query)
- **MAYBE**: Preview is ambiguous OR filename might be relevant but content unclear (e.g., "exhibits.pdf" could contain anything)
- **SKIP**: Clearly unrelated content AND filename doesn't suggest relevance (e.g., "employee_handbook.pdf" for a financial query)
- **When uncertain, choose MAYBE over SKIP.** Better to check extra documents than miss the answer.

### PHASE 2: Deep Dive (Use `parse_file`)
1. Use `parse_file` on documents marked RELEVANT
2. In your **reason**, explain what key information you found
3. **WATCH FOR CROSS-REFERENCES** - look for mentions like:
   - "See Exhibit A/B/C..."
   - "As stated in the [Document Name]..."
   - "Refer to [filename]..."
   - Document numbers, exhibit labels, or file names
4. In your **reason**, note any cross-references you discovered

### PHASE 3: Backtracking (Revisit if Cross-Referenced)
**CRITICAL**: If a document you're reading references another document that you SKIPPED:
1. In your **reason**, explain: "Found cross-reference to [document] - need to backtrack"
2. Use `preview_file` or `parse_file` to read the referenced document
3. Continue this until all relevant cross-references are resolved

**Backtracking Rules:**
- **Maximum depth**: Follow at most 3 levels of cross-references per chain (A→B→C→D, then stop)
- **No circular parsing**: If you've already parsed a document with `parse_file`, don't parse it again
- **"Resolved" means**: You've extracted the referenced information OR confirmed the reference doesn't contain what you need
- **When to stop backtracking**: You have the answer OR you've hit the depth limit OR all references lead to already-parsed documents

**If you decide NOT to backtrack** despite finding a cross-reference:
- Explain in your **reason**: "Found reference to [document] but sufficient information already gathered"
- This helps the user understand your decision-making process

## Providing Detailed Reasoning

Your `reason` field is displayed to the user, so make it informative:
- After scanning: List which documents you're categorizing as RELEVANT/MAYBE/SKIP and why
- After parsing: Summarize key findings and any cross-references discovered
- When backtracking: Explain which reference led you back to a skipped document

## CRITICAL: Citation Requirements for Final Answers

When providing your final answer, you MUST include citations for ALL factual claims:

### Citation Format
Use inline citations in this format: `[Source: filename, Section/Page]`

Example:
> The total purchase price is $125,000,000 [Source: 01_master_agreement.pdf, Section 2.1],
> consisting of $80M cash [Source: 01_master_agreement.pdf, Section 2.1(a)],
> $30M in stock [Source: 10_stock_purchase.pdf, Section 1], and
> $15M in escrow [Source: 09_escrow_agreement.pdf, Section 2].

### Citation Rules
1. **Every factual claim needs a citation** - dates, numbers, names, terms, etc.
2. **Be specific** - include section numbers, article numbers, or page references when available
3. **Use the actual filename** - not paraphrased names
4. **Multiple sources** - if information comes from multiple documents, cite all of them

### Final Answer Structure
Your final answer should:
1. **Start with a direct answer** to the user's question
2. **Provide details** with inline citations
3. **End with a Sources section** listing all documents consulted:

```
## Sources Consulted
- 01_master_agreement.pdf - Main acquisition terms
- 10_stock_purchase.pdf - Stock component details
- 09_escrow_agreement.pdf - Escrow terms and release schedule
```

## Example Workflow

```
User asks: "What is the purchase price?"

1. scan_folder("./documents/")
   Reason: "Scanned 10 documents. Categorizing:
   - RELEVANT: purchase_agreement.pdf (mentions 'Purchase Price' in preview)
   - RELEVANT: financial_terms.pdf (contains pricing tables)
   - MAYBE: exhibits.pdf (referenced by other docs)
   - SKIP: employee_handbook.pdf, hr_policies.pdf (unrelated to pricing)"

2. parse_file("purchase_agreement.pdf")
   Reason: "Found purchase price of $50M in Section 2.1. Document references
   'Exhibit B for price adjustments' - need to check exhibits.pdf next."

3. parse_file("exhibits.pdf")  [BACKTRACKING]
   Reason: "Backtracking to exhibits.pdf because purchase_agreement.pdf
   referenced it for adjustment details. Found working capital adjustment
   formula in Exhibit B."

4. STOP with final answer including citations:
   "The purchase price is $50,000,000 [Source: purchase_agreement.pdf, Section 2.1],
   subject to working capital adjustments [Source: exhibits.pdf, Exhibit B]..."
```

## Error Handling

If a tool returns an error, recover gracefully:

| Error Type | Recovery Action |
|------------|-----------------|
| "No such file or directory" | Check filename spelling, use `glob()` to find similar files |
| "Unsupported file extension" | Try `read()` for plain text files, or skip if truly unsupported |
| "Error parsing document" | File may be corrupted - try `preview_file()` instead, or skip |
| "Permission denied" | Skip the file and note the limitation in your answer |
| Multiple consecutive errors | Use `askhuman` to ask the user for guidance |

**When encountering errors:**
1. In your **reason**, acknowledge the error and explain your recovery strategy
2. Try an alternative approach before giving up
3. If you can't access a critical document, mention this limitation in your final answer

## Response Format

You MUST respond with valid JSON in this exact format:

For tool calls:
{
  "action": {
    "tool_name": "scan_folder",
    "tool_input": [{"parameter_name": "directory", "parameter_value": "./path"}]
  },
  "reason": "Your reasoning here"
}

For navigating deeper:
{
  "action": {"directory": "./path/to/explore"},
  "reason": "Your reasoning here"
}

For asking the user:
{
  "action": {"question": "Your question here"},
  "reason": "Your reasoning here"
}

For final answer:
{
  "action": {"final_result": "Your complete answer with citations"},
  "reason": "Your reasoning here"
}
"""


# =============================================================================
# Agent Implementation
# =============================================================================


class FsExplorerAgent:
    """
    AI agent for exploring filesystems using ProxyPal/OpenAI-compatible API.

    The agent maintains a conversation history with the LLM and uses
    structured JSON output to make decisions about which actions to take.

    Attributes:
        token_usage: Tracks API call statistics and costs.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        """
        Initialize the agent with ProxyPal/OpenAI credentials.

        Args:
            api_key: API key. If not provided, reads from PROXYPAL_API_KEY env var.
            base_url: Base URL for the API. If not provided, reads from PROXYPAL_BASE_URL env var.
            model: Model to use. If not provided, reads from PROXYPAL_MODEL env var.

        Raises:
            ValueError: If required configuration is not available.
        """
        if api_key is None:
            api_key = os.getenv("PROXYPAL_API_KEY")
        if api_key is None:
            raise ValueError(
                "PROXYPAL_API_KEY not found within the current environment: "
                "please export it or provide it to the class constructor."
            )

        if base_url is None:
            base_url = os.getenv("PROXYPAL_BASE_URL", "http://localhost:8317/v1")

        if model is None:
            model = os.getenv("PROXYPAL_MODEL", "claude-sonnet-4-20250514")

        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self._model = model
        self._chat_history: list[dict[str, str]] = []
        self._system_prompt = SYSTEM_PROMPT
        self.token_usage = TokenUsage()

    def configure_task(self, task: str) -> None:
        """
        Add a task message to the conversation history.

        Args:
            task: The task or context to add to the conversation.
        """
        self._chat_history.append({"role": "user", "content": task})

    async def take_action(self) -> tuple[Action, ActionType] | None:
        """
        Request the next action from the AI model.

        Sends the current conversation history to the LLM and receives
        a structured JSON response indicating the next action to take.

        Returns:
            A tuple of (Action, ActionType) if successful, None otherwise.
        """
        messages = [
            {"role": "system", "content": self._system_prompt},
            *self._chat_history,
        ]

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,  # type: ignore
            max_tokens=4096,
        )

        # Track token usage from response (always count API call, even if usage is None)
        prompt_tokens = 0
        completion_tokens = 0
        if response.usage:
            prompt_tokens = response.usage.prompt_tokens or 0
            completion_tokens = response.usage.completion_tokens or 0
        self.token_usage.add_api_call(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

        if response.choices and response.choices[0].message.content:
            content = response.choices[0].message.content

            # Add assistant response to history
            self._chat_history.append({"role": "assistant", "content": content})

            # Extract JSON from response (handle markdown code blocks and preamble text)
            json_content = content
            if "```json" in content:
                json_content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_content = content.split("```")[1].split("```")[0].strip()
            elif "{" in content:
                # Handle case where model returns text before JSON
                start_idx = content.find("{")
                # Find matching closing brace
                brace_count = 0
                end_idx = start_idx
                for i, char in enumerate(content[start_idx:], start_idx):
                    if char == "{":
                        brace_count += 1
                    elif char == "}":
                        brace_count -= 1
                        if brace_count == 0:
                            end_idx = i + 1
                            break
                json_content = content[start_idx:end_idx]

            try:
                action = Action.model_validate_json(json_content)
                if action.to_action_type() == "toolcall":
                    toolcall = cast(ToolCallAction, action.action)
                    self.call_tool(
                        tool_name=toolcall.tool_name,
                        tool_input=toolcall.to_fn_args(),
                    )
                return action, action.to_action_type()
            except Exception as e:
                # If JSON parsing fails, log error (encode safely for Windows console)
                safe_content = (
                    content[:500].encode("ascii", errors="replace").decode("ascii")
                )
                print(f"Warning: Failed to parse action JSON: {e}")
                print(f"Response content: {safe_content}...")
                return None

        return None

    def call_tool(self, tool_name: Tools, tool_input: dict[str, Any]) -> None:
        """
        Execute a tool and add the result to the conversation history.

        Args:
            tool_name: Name of the tool to execute.
            tool_input: Dictionary of arguments to pass to the tool.
        """
        try:
            result = TOOLS[tool_name](**tool_input)
        except Exception as e:
            result = (
                f"An error occurred while calling tool {tool_name} "
                f"with {tool_input}: {e}"
            )

        # Track tool result sizes
        self.token_usage.add_tool_result(result, tool_name)

        self._chat_history.append(
            {"role": "user", "content": f"Tool result for {tool_name}:\n\n{result}"}
        )

    def reset(self) -> None:
        """Reset the agent's conversation history and token tracking."""
        self._chat_history.clear()
        self.token_usage = TokenUsage()
