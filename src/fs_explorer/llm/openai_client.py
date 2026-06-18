"""OpenAI-compatible LLM client (SiliconFlow, OpenAI, etc.)."""

from __future__ import annotations

from openai import AsyncOpenAI

from .base import ChatMessage, LLMUsage
from .prompts import action_schema_instructions


class OpenAICompatibleClient:
    """Chat-completions backend for OpenAI-compatible APIs."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str,
        provider_name: str,
    ) -> None:
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self._model = model
        self._provider_name = provider_name

    @property
    def provider_name(self) -> str:
        return self._provider_name

    @property
    def model_name(self) -> str:
        return self._model

    async def generate_action_json(
        self,
        *,
        messages: list[ChatMessage],
        system_instruction: str,
    ) -> tuple[str, LLMUsage]:
        schema_hint = (
            f"{system_instruction}\n\n{action_schema_instructions()}"
        )
        payload = [
            {"role": "system", "content": schema_hint},
            *[
                {"role": message.role, "content": message.content}
                for message in messages
            ],
        ]
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=payload,  # type: ignore[arg-type]
            response_format={"type": "json_object"},
            temperature=0.2,
        )

        content = response.choices[0].message.content or ""
        usage = LLMUsage()
        if response.usage is not None:
            usage = LLMUsage(
                prompt_tokens=response.usage.prompt_tokens or 0,
                completion_tokens=response.usage.completion_tokens or 0,
            )

        json_str = content.strip()
        if not json_str.startswith("{"):
            start = json_str.find("{")
            end = json_str.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = json_str[start:end]

        if not json_str:
            raise RuntimeError(f"{self._provider_name} returned an empty response")

        return json_str, usage
