"""DeepSeek HTTP client for topic and outline generation only (never final scripts)."""

from __future__ import annotations

import json
import logging
import time
from typing import Any

import requests

from src.utils.constants import PROJECT_ROOT
from src.utils.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)

DEEPSEEK_CHAT_COMPLETIONS_URL = "https://api.deepseek.com/chat/completions"
DEFAULT_MAX_RETRIES = 2  # two retries after the first attempt (three tries total)

_DEFAULT_OUTLINE_USER_TEMPLATE = (
    "Create an outline for this topic:\n{{topic}}\n"
    "Audience: {{audience}}\nTarget length: {{target_length}}"
)


class DeepSeekClient:
    """Call DeepSeek for cheap analytical work: topics and outlines only.

    This client intentionally does **not** expose script-writing helpers; final
    scripts must go through the writing model (see allocation docs).
    """

    def __init__(
        self,
        api_key: str,
        *,
        model: str | None = None,
        base_url: str = DEEPSEEK_CHAT_COMPLETIONS_URL,
        script_prompts: dict[str, Any] | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        """Configure API access and optional prompt templates.

        Args:
            api_key: DeepSeek API bearer token (never commit real keys).
            model: Model id; defaults to ``deepseek-chat`` when omitted.
            base_url: Chat-completions endpoint URL.
            script_prompts: Optional ``script_prompts.json`` structure; when
                omitted, prompts are loaded from ``config/script_prompts.json``.
            max_retries: Additional attempts after a failed request (HTTP 5xx,
                429, or network error). Default is two retries (three tries).
        """
        if not isinstance(api_key, str):
            raise ExternalServiceError("DeepSeek api_key must be a string.")
        self.api_key = api_key.strip()
        self.model = (model or "deepseek-chat").strip()
        self.base_url = base_url.rstrip()
        self.max_retries = max(0, int(max_retries))
        self._script_prompts = script_prompts or self._load_default_script_prompts()

    @staticmethod
    def _load_default_script_prompts() -> dict[str, Any]:
        path = PROJECT_ROOT / "config" / "script_prompts.json"
        if not path.is_file():
            raise ExternalServiceError(
                f"Default script prompts not found at {path}. Pass script_prompts= explicitly."
            )
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            raise ExternalServiceError("script_prompts.json must contain a JSON object.")
        return data

    def is_configured(self) -> bool:
        """Return whether a non-empty API key is present."""
        return bool(self.api_key)

    def build_payload(
        self,
        user_prompt: str,
        *,
        max_tokens: int = 400,
        system_prompt: str | None = None,
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        """Build the JSON body for a chat-completions request (tests / tooling).

        Args:
            user_prompt: User message content.
            max_tokens: ``max_tokens`` field for the API.
            system_prompt: Optional system message.
            temperature: Sampling temperature.

        Returns:
            Serializable request body.
        """
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})
        return {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _post_chat_completion(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        """POST to DeepSeek with retries; return parsed JSON or ``None`` on failure."""
        if not self.is_configured():
            logger.error("DeepSeek request skipped: missing API key.")
            return None

        last_error: str | None = None
        attempts = self.max_retries + 1
        for attempt in range(1, attempts + 1):
            try:
                logger.info(
                    "DeepSeek POST %s attempt=%s/%s model=%s",
                    self.base_url,
                    attempt,
                    attempts,
                    self.model,
                )
                response = requests.post(
                    self.base_url,
                    headers=self._headers(),
                    json=payload,
                    timeout=60,
                )
                logger.debug("DeepSeek HTTP status=%s", response.status_code)
                if response.status_code in (429, 500, 502, 503, 504):
                    last_error = f"HTTP {response.status_code}"
                    logger.warning("DeepSeek transient error: %s", last_error)
                    time.sleep(min(2**attempt, 8))
                    continue
                response.raise_for_status()
                data = response.json()
                keys_preview = (
                    list(data.keys()) if isinstance(data, dict) else type(data).__name__
                )
                logger.debug("DeepSeek response keys=%s", keys_preview)
                return data if isinstance(data, dict) else None
            except requests.RequestException as exc:
                last_error = str(exc)
                logger.warning("DeepSeek request exception (attempt %s): %s", attempt, exc)
                time.sleep(min(2**attempt, 8))

        logger.error("DeepSeek failed after %s attempts: %s", attempts, last_error)
        return None

    @staticmethod
    def _extract_assistant_text(data: dict[str, Any]) -> str | None:
        try:
            choices = data.get("choices") or []
            if not choices:
                return None
            message = choices[0].get("message") or {}
            content = (message.get("content") or "").strip()
            return content or None
        except (TypeError, KeyError, IndexError):
            return None

    def generate_topic(self, category: str = "general", trendy: bool = True) -> str | None:
        """Return a single YouTube-style topic line for the given category.

        DeepSeek is used only for topic ideation (not script text).

        Args:
            category: Broad niche label (for example ``\"health\"`` or ``\"tech\"``).
            trendy: When true, prompt emphasizes timeliness / search intent.

        Returns:
            A single-line topic string, or ``None`` if the API call fails.
        """
        block = self._script_prompts.get("topic_research") or {}
        system = str(block.get("system") or "You are a YouTube niche researcher.")
        template = str(
            block.get("user_template")
            or "Generate topic ideas for niche '{{niche}}'."
        )
        trend = "Prioritize timely, high-search-intent angles." if trendy else ""
        user = (
            template.replace("{{niche}}", category)
            + "\n\n"
            + trend
            + "\nRespond with exactly one topic title on a single line (no bullets, no numbering)."
        )
        payload = self.build_payload(user, system_prompt=system, max_tokens=220, temperature=0.65)
        data = self._post_chat_completion(payload)
        if not data:
            logger.error("DeepSeek generate_topic: no response payload.")
            return None
        text = self._extract_assistant_text(data)
        if not text:
            logger.error("DeepSeek generate_topic: empty assistant content.")
            return None
        first_line = text.splitlines()[0].strip()
        topic = first_line.lstrip("0123456789.-) ").strip()
        logger.info("DeepSeek generate_topic success category=%r", category)
        return topic or None

    def create_outline(self, topic: str, content_type: str = "short") -> str | None:
        """Return a structured outline string for ``topic`` (DeepSeek only).

        Args:
            topic: Video topic produced by :meth:`generate_topic` or supplied upstream.
            content_type: ``\"short\"`` maps to a 2–3 minute outline; other values
                are passed through as a human-readable length hint.

        Returns:
            Outline text, or ``None`` if the API call fails.
        """
        if not (topic or "").strip():
            logger.error("create_outline called with empty topic.")
            return None

        block = self._script_prompts.get("outline_generation") or {}
        system = str(block.get("system") or "You create concise video outlines.")
        template = str(block.get("user_template") or _DEFAULT_OUTLINE_USER_TEMPLATE)
        if content_type == "short":
            length_hint = "2-3 minutes (faceless YouTube)"
        else:
            length_hint = str(content_type)
        user = (
            template.replace("{{topic}}", topic.strip())
            .replace("{{audience}}", "General YouTube viewers")
            .replace("{{target_length}}", length_hint)
        )
        payload = self.build_payload(user, system_prompt=system, max_tokens=900, temperature=0.55)
        data = self._post_chat_completion(payload)
        if not data:
            logger.error("DeepSeek create_outline: no response payload.")
            return None
        text = self._extract_assistant_text(data)
        if not text:
            logger.error("DeepSeek create_outline: empty assistant content.")
            return None
        logger.info("DeepSeek create_outline success topic_len=%s", len(topic))
        return text.strip()
