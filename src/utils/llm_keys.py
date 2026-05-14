"""Resolve OpenAI / DeepSeek API keys via llm_gateway (keychain) with env fallbacks."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _import_secrets_manager():
    try:
        from secrets_manager import SecretsManager
    except ImportError:
        project_root = Path(__file__).resolve().parents[2]
        sibling = project_root.parent / "llm_gateway"
        if not sibling.is_dir():
            raise ImportError(
                "secrets_manager is not installed and ../llm_gateway was not found. "
                "Install with: uv pip install -e ../llm_gateway "
                "or add llm-gateway-secrets to your environment.",
            ) from None
        path = str(sibling)
        if path not in sys.path:
            sys.path.insert(0, path)
        from secrets_manager import SecretsManager

    return SecretsManager


SecretsManager = _import_secrets_manager()


def get_openai_api_key() -> str | None:
    """Prefer keychain ``openai`` (llm_gateway), then ``OPENAI_API_KEY``."""
    key = SecretsManager.get_openai_key()
    if key:
        return key
    env = os.getenv("OPENAI_API_KEY", "")
    return env or None


def get_deepseek_api_key_with_openai_fallback() -> str | None:
    """
    Prefer a dedicated DeepSeek key. If missing, read ``openai`` from the keychain;
    if the first read is empty, try ``get_openai_key`` once more, then env vars.
    """
    ds = SecretsManager.get_deepseek_key()
    if ds:
        return ds
    openai_key = SecretsManager.get_openai_key()
    if openai_key:
        return openai_key
    openai_retry = SecretsManager.get_openai_key()
    if openai_retry:
        return openai_retry
    env_ds = os.getenv("DEEPSEEK_API_KEY", "")
    if env_ds:
        return env_ds
    env_openai = os.getenv("OPENAI_API_KEY", "")
    return env_openai or None
