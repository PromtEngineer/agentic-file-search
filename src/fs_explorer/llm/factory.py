"""Factory for LLM provider clients."""

from __future__ import annotations

from .base import LLMClient
from .config import LLMConfig, load_llm_config
from .google_client import GoogleGeminiClient
from .openai_client import OpenAICompatibleClient


from .prompts import action_schema_instructions


def create_llm_client(*, api_key: str | None = None, config: LLMConfig | None = None) -> LLMClient:
    """Instantiate the configured LLM backend."""
    resolved = config or load_llm_config(api_key=api_key)

    if resolved.provider == "google":
        return GoogleGeminiClient(api_key=resolved.api_key, model=resolved.model)

    if resolved.provider == "siliconflow":
        if not resolved.base_url:
            raise ValueError("FS_EXPLORER_LLM_BASE_URL is required for siliconflow")
        return OpenAICompatibleClient(
            api_key=resolved.api_key,
            model=resolved.model,
            base_url=resolved.base_url,
            provider_name="siliconflow",
        )

    if resolved.provider == "openai":
        if not resolved.base_url:
            raise ValueError("FS_EXPLORER_LLM_BASE_URL is required for openai")
        return OpenAICompatibleClient(
            api_key=resolved.api_key,
            model=resolved.model,
            base_url=resolved.base_url,
            provider_name="openai",
        )

    raise ValueError(f"Unsupported provider: {resolved.provider}")
