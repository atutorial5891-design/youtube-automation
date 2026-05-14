"""High-quality script generation using OpenAI or Anthropic (never cheap topic-only work)."""

from __future__ import annotations

import json
import logging
from typing import Any, Literal

from src.utils.constants import PROJECT_ROOT
from src.utils.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)

ProviderName = Literal["openai", "anthropic"]

_DEFAULT_SCRIPT_USER_TEMPLATE = (
    "Write a script from this outline:\n{{outline}}\n"
    "Tone goal: {{tone}}\nTarget duration: {{target_duration}}"
)


class ChatGPTClient:
    """Writing-model client for monetization-critical script text.

    Topics and outlines must be produced elsewhere (DeepSeek); this class only
    implements final script drafting per allocation rules.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        *,
        provider: ProviderName = "openai",
        script_prompts: dict[str, Any] | None = None,
    ) -> None:
        """Store credentials and load default script prompts when needed.

        Args:
            api_key: Provider API key (OpenAI or Anthropic).
            model: Model id for the selected provider.
            provider: ``\"openai\"`` (default) or ``\"anthropic\"``.
            script_prompts: Optional ``script_prompts.json`` structure.

        Raises:
            ExternalServiceError: If ``api_key`` is missing or prompts cannot be loaded.
        """
        if not isinstance(api_key, str) or not api_key.strip():
            raise ExternalServiceError("ChatGPTClient requires a non-empty api_key string.")
        self.api_key = api_key.strip()
        self.provider: ProviderName = provider
        self.model = self._normalize_model(model)
        self._script_prompts = script_prompts or self._load_default_script_prompts()
        self._openai_client: Any = None
        self._anthropic_client: Any = None
        self._init_sdk_clients()

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

    def _normalize_model(self, model: str) -> str:
        m = (model or "").strip()
        if self.provider == "anthropic" and m in {"", "gpt-4o-mini"}:
            return "claude-3-5-sonnet-latest"
        return m or ("gpt-4o-mini" if self.provider == "openai" else "claude-3-5-sonnet-latest")

    def _init_sdk_clients(self) -> None:
        if self.provider == "openai":
            from openai import OpenAI

            self._openai_client = OpenAI(api_key=self.api_key)
            self._anthropic_client = None
        else:
            import anthropic

            self._anthropic_client = anthropic.Anthropic(api_key=self.api_key)
            self._openai_client = None

    def is_configured(self) -> bool:
        """Return whether a non-empty API key was supplied."""
        return bool(self.api_key)

    def current_config(self) -> dict[str, str]:
        """Return provider and model for logging and metadata."""
        return {"provider": self.provider, "model": self.model}

    def _quality_script_instructions(self, style: str) -> str:
        return (
            "You write faceless YouTube narration scripts. Structure explicitly:\n"
            "1) HOOK (first ~15 seconds): pattern interrupt or bold claim tied to the topic.\n"
            "2) BODY: clear sections with natural transitions; keep pacing conversational.\n"
            "3) CTA: one concise call-to-action (subscribe / next video / comment).\n"
            f"Style tag: {style}. Aim for roughly 2–3 minutes spoken at a moderate pace.\n"
            "No stage directions in brackets unless essential; optimize for voiceover."
        )

    def write_script(
        self,
        topic: str,
        outline: str | None = None,
        style: str = "youtube_faceless",
    ) -> str:
        """Generate the full script body (quality-critical path).

        Retries are intentionally **not** implemented here; the orchestrator
        should decide whether to retry a failed draft.

        Args:
            topic: Video topic line.
            outline: Optional outline from DeepSeek; improves structure when present.
            style: Channel / format hint (default faceless YouTube).

        Returns:
            Full script text.

        Raises:
            ExternalServiceError: On empty inputs or provider failures / empty responses.
        """
        if not (topic or "").strip():
            raise ExternalServiceError("write_script requires a non-empty topic.")
        block = self._script_prompts.get("script_generation") or {}
        base_system = str(
            block.get("system")
            or "You write compelling YouTube scripts with hooks, transitions, and pacing."
        )
        system = base_system + "\n\n" + self._quality_script_instructions(style)
        template = str(block.get("user_template") or _DEFAULT_SCRIPT_USER_TEMPLATE)
        if (outline or "").strip():
            outline_text = outline.strip()
        else:
            outline_text = f"(No outline — expand from topic: {topic.strip()})"
        user = (
            template.replace("{{outline}}", outline_text)
            .replace("{{tone}}", "engaging, clear, trustworthy")
            .replace("{{target_duration}}", "2-3 minutes")
            + f"\n\nPrimary topic line:\n{topic.strip()}\n"
        )

        logger.info(
            "Writing script via provider=%s model=%s topic_len=%s outline=%s",
            self.provider,
            self.model,
            len(topic),
            bool(outline and outline.strip()),
        )

        if self.provider == "openai":
            text = self._write_script_openai(system, user)
        else:
            text = self._write_script_anthropic(system, user)

        if not text.strip():
            raise ExternalServiceError("Writing model returned an empty script.")
        logger.info("write_script completed output_len=%s", len(text))
        return text.strip()

    def _write_script_openai(self, system: str, user: str) -> str:
        if self._openai_client is None:
            raise ExternalServiceError("OpenAI client is not initialized.")
        try:
            response = self._openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.75,
                max_tokens=3600,
            )
        except Exception as exc:  # noqa: BLE001 — surface as ExternalServiceError
            logger.exception("OpenAI write_script failed")
            raise ExternalServiceError(f"OpenAI script generation failed: {exc}") from exc

        choice0 = response.choices[0]
        content = (choice0.message.content or "").strip()
        return content

    def _write_script_anthropic(self, system: str, user: str) -> str:
        if self._anthropic_client is None:
            raise ExternalServiceError("Anthropic client is not initialized.")
        try:
            response = self._anthropic_client.messages.create(
                model=self.model,
                max_tokens=3600,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Anthropic write_script failed")
            raise ExternalServiceError(f"Anthropic script generation failed: {exc}") from exc

        parts: list[str] = []
        for block in response.content:
            text = getattr(block, "text", None)
            if text:
                parts.append(text)
        return "".join(parts).strip()
