"""Minimal DeepSeek client wrapper for topic and outline work."""

from __future__ import annotations

import os
from typing import Any

import requests

from src.utils.exceptions import ExternalServiceError
from src.utils.llm_keys import get_deepseek_api_key_with_openai_fallback


class DeepSeekClient:
    endpoint = "https://api.deepseek.com/chat/completions"

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        resolved = get_deepseek_api_key_with_openai_fallback() if api_key is None else api_key
        self.api_key = resolved or ""
        self.model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def build_payload(self, prompt: str, max_tokens: int = 300) -> dict[str, Any]:
        return {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": max_tokens,
        }

    def topic_request(self, prompt: str) -> dict[str, Any]:
        if not self.is_configured():
            raise ExternalServiceError("DeepSeek API key is not configured")
        response = requests.post(
            self.endpoint,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=self.build_payload(prompt),
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
