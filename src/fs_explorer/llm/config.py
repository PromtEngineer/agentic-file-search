"""Environment-based LLM provider configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

LLMProviderName = Literal["google", "siliconflow", "openai"]

_DEFAULT_MODELS: dict[LLMProviderName, str] = {
    "google": "gemini-3-flash-preview",
    "siliconflow": "Qwen/Qwen2.5-72B-Instruct",
    "openai": "gpt-4o-mini",
}

_DEFAULT_BASE_URLS: dict[LLMProviderName, str] = {
    "siliconflow": "https://api.siliconflow.cn/v1",
    "openai": "https://api.openai.com/v1",
}


@dataclass(frozen=True)
class LLMConfig:
    """Resolved LLM settings for the active provider."""

    provider: LLMProviderName
    api_key: str
    model: str
    base_url: str | None = None


def _resolve_provider() -> LLMProviderName:
    raw = os.getenv("FS_EXPLORER_LLM_PROVIDER", "google").strip().lower()
    aliases = {
        "gemini": "google",
        "google": "google",
        "siliconflow": "siliconflow",
        "silicon-flow": "siliconflow",
        "sf": "siliconflow",
        "openai": "openai",
    }
    provider = aliases.get(raw)
    if provider is None:
        supported = ", ".join(sorted(set(aliases.values())))
        raise ValueError(
            f"Unsupported FS_EXPLORER_LLM_PROVIDER={raw!r}. "
            f"Supported values: {supported}"
        )
    return provider  # type: ignore[return-value]


def _resolve_api_key(provider: LLMProviderName, explicit_key: str | None) -> str:
    if explicit_key:
        return explicit_key

    env_keys: dict[LLMProviderName, tuple[str, ...]] = {
        "google": ("GOOGLE_API_KEY",),
        "siliconflow": ("SILICONFLOW_API_KEY", "OPENAI_API_KEY"),
        "openai": ("OPENAI_API_KEY",),
    }
    for env_name in env_keys[provider]:
        value = os.getenv(env_name)
        if value:
            return value

    expected = " or ".join(env_keys[provider])
    raise ValueError(
        f"No API key found for provider {provider!r}. "
        f"Set {expected}, or pass api_key to FsExplorerAgent."
    )


def load_llm_config(*, api_key: str | None = None) -> LLMConfig:
    """Load provider settings from environment variables."""
    provider = _resolve_provider()
    resolved_key = _resolve_api_key(provider, api_key)
    model = os.getenv("FS_EXPLORER_LLM_MODEL", _DEFAULT_MODELS[provider])
    base_url = os.getenv("FS_EXPLORER_LLM_BASE_URL")
    if base_url is None and provider in _DEFAULT_BASE_URLS:
        base_url = _DEFAULT_BASE_URLS[provider]
    return LLMConfig(
        provider=provider,
        api_key=resolved_key,
        model=model,
        base_url=base_url,
    )
