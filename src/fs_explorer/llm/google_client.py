"""Google Gemini LLM client."""

from __future__ import annotations

from google.genai import Client as GenAIClient
from google.genai.types import Content, HttpOptions, Part

from ..models import Action
from .base import ChatMessage, LLMUsage


class GoogleGeminiClient:
    """Gemini backend with native JSON schema support."""

    def __init__(self, *, api_key: str, model: str) -> None:
        self._client = GenAIClient(
            api_key=api_key,
            http_options=HttpOptions(api_version="v1beta"),
        )
        self._model = model

    @property
    def provider_name(self) -> str:
        return "google"

    @property
    def model_name(self) -> str:
        return self._model

    async def generate_action_json(
        self,
        *,
        messages: list[ChatMessage],
        system_instruction: str,
    ) -> tuple[str, LLMUsage]:
        contents = [
            Content(
                role="user" if message.role == "user" else "model",
                parts=[Part.from_text(text=message.content)],
            )
            for message in messages
        ]
        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=contents,  # type: ignore[arg-type]
            config={
                "system_instruction": system_instruction,
                "response_mime_type": "application/json",
                "response_schema": Action,
            },
        )

        usage = LLMUsage()
        if response.usage_metadata:
            usage = LLMUsage(
                prompt_tokens=response.usage_metadata.prompt_token_count or 0,
                completion_tokens=response.usage_metadata.candidates_token_count or 0,
            )

        if response.text is None:
            raise RuntimeError("Gemini returned an empty response")

        return response.text, usage
