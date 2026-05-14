"""Hybrid script generation: DeepSeek for topic + outline, writing model for script only."""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any, Literal

from src.api.chatgpt_client import ChatGPTClient
from src.api.deepseek_client import DeepSeekClient
from src.core.config_loader import ConfigLoader
from src.utils.exceptions import ExternalServiceError, ValidationError

logger = logging.getLogger(__name__)

WritingProvider = Literal["openai", "anthropic"]


class HybridScriptGenerator:
    """Orchestrate cheap DeepSeek steps then a quality writing model for the script.

    Cost figures are **estimates** (USD) read from ``settings.json`` under
    ``hybrid_generation`` so monitoring stays configuration-driven.
    """

    def __init__(
        self,
        deepseek_key: str,
        chatgpt_key: str,
        chatgpt_model: str = "gpt-4o-mini",
        *,
        writing_provider: WritingProvider = "openai",
        config_loader: ConfigLoader | None = None,
    ) -> None:
        """Wire both API clients and optional config overrides.

        Args:
            deepseek_key: API key for DeepSeek (topics + outlines only).
            chatgpt_key: API key for OpenAI or Anthropic script drafting.
            chatgpt_model: Model id passed to :class:`ChatGPTClient`.
            writing_provider: ``\"openai\"`` or ``\"anthropic\"``.
            config_loader: Optional :class:`ConfigLoader` (defaults to ``config/``).
        """
        if not isinstance(deepseek_key, str) or not deepseek_key.strip():
            raise ValidationError("deepseek_key must be a non-empty string.")
        if not isinstance(chatgpt_key, str) or not chatgpt_key.strip():
            raise ValidationError("chatgpt_key must be a non-empty string.")

        self.config = config_loader or ConfigLoader()
        prompts = self.config.get_script_prompts()

        self._deepseek = DeepSeekClient(deepseek_key.strip(), script_prompts=prompts)
        self._writer = ChatGPTClient(
            chatgpt_key.strip(),
            model=chatgpt_model,
            provider=writing_provider,
            script_prompts=prompts,
        )
        self._last_metadata: dict[str, Any] = {}
        logger.info(
            "HybridScriptGenerator ready writing_provider=%s deepseek_model=%s writer_model=%s",
            writing_provider,
            self._deepseek.model,
            self._writer.model,
        )

    def _estimated_costs(self) -> tuple[float, float, float]:
        """Return (deepseek_topic_usd, deepseek_outline_usd, chatgpt_script_usd)."""
        topic = float(
            self.config.get_setting("hybrid_generation.deepseek_topic_usd", 0.015)
        )
        outline = float(
            self.config.get_setting("hybrid_generation.deepseek_outline_usd", 0.025)
        )
        script = float(
            self.config.get_setting("hybrid_generation.chatgpt_script_usd", 0.125)
        )
        return topic, outline, script

    def _retry_deepseek(self, label: str, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Call ``fn`` twice on ``None`` results (log between attempts)."""
        result = fn(*args, **kwargs)
        if result is not None:
            return result
        logger.warning("DeepSeek step %s returned empty; retrying once.", label)
        return fn(*args, **kwargs)

    def generate_script(self, category: str = "general") -> dict[str, Any]:
        """Run topic → outline → script and attach cost metadata.

        Args:
            category: Niche/category label forwarded to DeepSeek topic generation.

        Returns:
            Dictionary with topic, outline, script, cost breakdown, timestamps,
            and model ids.

        Raises:
            ValidationError: If ``category`` is empty after stripping.
            ExternalServiceError: If DeepSeek cannot produce topic/outline after
                one retry each, or if the writing model raises.
        """
        category_clean = (category or "").strip()
        if not category_clean:
            raise ValidationError(
                "category must be a non-empty string (for example 'health' or 'tech')."
            )

        ds_topic_cost, ds_outline_cost, cg_script_cost = self._estimated_costs()
        logger.info(
            "Hybrid generate_script start category=%r "
            "est_costs ds_topic=%.4f ds_outline=%.4f writer=%.4f",
            category_clean,
            ds_topic_cost,
            ds_outline_cost,
            cg_script_cost,
        )

        topic = self._retry_deepseek(
            "generate_topic",
            self._deepseek.generate_topic,
            category_clean,
            True,
        )
        if not topic:
            raise ExternalServiceError(
                "DeepSeek could not generate a topic after one retry. "
                "Check API key, quota, and network connectivity."
            )

        outline = self._retry_deepseek(
            "create_outline",
            self._deepseek.create_outline,
            topic,
            "short",
        )
        if not outline:
            raise ExternalServiceError(
                "DeepSeek could not create an outline after one retry. "
                "Check API key, quota, and network connectivity."
            )

        script = self._writer.write_script(
            topic,
            outline=outline,
            style="youtube_faceless",
        )

        api_split = {
            "deepseek": round(ds_topic_cost + ds_outline_cost, 6),
            "chatgpt": round(cg_script_cost, 6),
        }
        api_cost = round(api_split["deepseek"] + api_split["chatgpt"], 6)
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        payload: dict[str, Any] = {
            "topic": topic,
            "outline": outline,
            "script": script,
            "category": category_clean,
            "api_cost": api_cost,
            "api_split": api_split,
            "timestamp": timestamp,
            "model_versions": {
                "deepseek_model": self._deepseek.model,
                "chatgpt_model": self._writer.model,
            },
        }
        self._last_metadata = dict(payload)
        logger.info(
            "Hybrid generate_script complete api_cost_estimate=%s api_split=%s",
            api_cost,
            api_split,
        )
        return payload
