"""Writing-model helper for script generation and quality work."""

from __future__ import annotations

import os
from dataclasses import dataclass

from src.utils.constants import SUPPORTED_PRIMARY_MODELS
from src.utils.exceptions import ExternalServiceError
from src.utils.llm_keys import get_openai_api_key


@dataclass
class WritingModelConfig:
    provider: str = "openai"
    model: str = "gpt-4o-mini"


class ChatGPTClient:
    """Stage 1 wrapper that validates writing-model configuration."""

    def __init__(self, provider: str = "openai") -> None:
        normalized = provider.lower()
        if normalized not in SUPPORTED_PRIMARY_MODELS:
            raise ExternalServiceError(f"Unsupported provider: {provider}")
        self.provider = normalized

    def is_configured(self) -> bool:
        if self.provider == "openai":
            return bool(get_openai_api_key())
        return bool(os.getenv("CLAUDE_API_KEY", ""))

    def current_config(self) -> WritingModelConfig:
        if self.provider == "openai":
            return WritingModelConfig(provider="openai", model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
        return WritingModelConfig(provider="claude", model=os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-latest"))
