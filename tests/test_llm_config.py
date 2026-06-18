"""Tests for LLM provider configuration."""

import os

import pytest

from fs_explorer.llm.config import load_llm_config


def test_load_google_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FS_EXPLORER_LLM_PROVIDER", "google")
    monkeypatch.setenv("GOOGLE_API_KEY", "g-key")
    monkeypatch.delenv("FS_EXPLORER_LLM_MODEL", raising=False)
    config = load_llm_config()
    assert config.provider == "google"
    assert config.api_key == "g-key"
    assert config.model == "gemini-3-flash-preview"


def test_load_siliconflow_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FS_EXPLORER_LLM_PROVIDER", "siliconflow")
    monkeypatch.setenv("SILICONFLOW_API_KEY", "sf-key")
    config = load_llm_config()
    assert config.provider == "siliconflow"
    assert config.api_key == "sf-key"
    assert config.base_url == "https://api.siliconflow.cn/v1"


def test_load_openai_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FS_EXPLORER_LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "o-key")
    monkeypatch.delenv("FS_EXPLORER_LLM_BASE_URL", raising=False)
    config = load_llm_config()
    assert config.provider == "openai"
    assert config.api_key == "o-key"
    assert config.base_url == "https://api.openai.com/v1"


def test_explicit_api_key_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FS_EXPLORER_LLM_PROVIDER", "google")
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    config = load_llm_config(api_key="override")
    assert config.api_key == "override"


def test_missing_api_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FS_EXPLORER_LLM_PROVIDER", "siliconflow")
    monkeypatch.delenv("SILICONFLOW_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="No API key found"):
        load_llm_config()
