"""Resolve OpenAI / DeepSeek API keys via llm_gateway (keychain) with env fallbacks."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _mask_secret(raw: str) -> str:
    if len(raw) <= 8:
        return "****"
    return f"{raw[:4]}…{raw[-4:]}"


class _EnvOnlySecretsManager:
    """Keychain-free stub when ``secrets_manager`` or ``keyring`` is unavailable.

    Uses only ``OPENAI_API_KEY`` and ``DEEPSEEK_API_KEY``. Same call shape as
    llm_gateway's ``SecretsManager`` (``masked`` / ``context``) so tests can
    monkeypatch the class.
    """

    @staticmethod
    def get_openai_key(masked: bool = False, context: Any = None) -> str | None:
        raw = (os.getenv("OPENAI_API_KEY") or "").strip()
        if not raw:
            return None
        return _mask_secret(raw) if masked else raw

    @staticmethod
    def get_deepseek_key(masked: bool = False, context: Any = None) -> str | None:
        raw = (os.getenv("DEEPSEEK_API_KEY") or "").strip()
        if not raw:
            return None
        return _mask_secret(raw) if masked else raw


def _import_secrets_manager() -> type:
    """Load llm_gateway ``SecretsManager`` when possible; else env-only stub."""
    try:
        from secrets_manager import SecretsManager

        return SecretsManager
    except (ImportError, ModuleNotFoundError):
        pass

    project_root = Path(__file__).resolve().parents[2]
    sibling = project_root.parent / "llm_gateway"
    if sibling.is_dir():
        path = str(sibling)
        if path not in sys.path:
            sys.path.insert(0, path)
        try:
            from secrets_manager import SecretsManager

            return SecretsManager
        except (ImportError, ModuleNotFoundError) as exc:
            logger.warning(
                "llm_gateway at %s could not be imported (%s). "
                "Using OPENAI_API_KEY / DEEPSEEK_API_KEY from the environment only. "
                "Install dependencies with: uv pip install -e .  (includes keyring) "
                "or: uv pip install -e ../llm_gateway",
                sibling,
                exc,
            )

    logger.warning(
        "secrets_manager not available; using OPENAI_API_KEY / DEEPSEEK_API_KEY only. "
        "For keychain support: uv pip install -e ../llm_gateway (and keyring)."
    )
    return _EnvOnlySecretsManager


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
