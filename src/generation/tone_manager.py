"""Tone library loading, content-aware tone selection, and ChatGPT-backed rewrites."""

from __future__ import annotations

import json
import logging
import random
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.utils.constants import PROJECT_ROOT
from src.utils.exceptions import ExternalServiceError, ValidationError
from src.utils.llm_keys import get_openai_api_key

logger = logging.getLogger(__name__)

DEFAULT_TONE_ID = "professional_educational"
DEFAULT_TONE_LIBRARY = "config/tone_library.json"


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _resolve_library_path(tone_library_path: str) -> Path:
    raw = Path(tone_library_path).expanduser()
    return raw if raw.is_absolute() else (PROJECT_ROOT / raw).resolve()


class ToneManager:
    """Load tones from JSON, classify scripts, pick tones, and generate variations.

    Variation rewrites use the OpenAI API (same class of model as other quality
    stages). Estimated per-call USD is read from ``tone_library.json`` under
    ``meta.estimated_usd_per_chatgpt_variation`` (fallback when missing).
    """

    def __init__(
        self,
        tone_library_path: str = DEFAULT_TONE_LIBRARY,
        *,
        chatgpt_key: str | None = None,
        openai_model: str = "gpt-4o-mini",
    ) -> None:
        """Load and validate the tone library; configure OpenAI for rewrites.

        Args:
            tone_library_path: Path to ``tone_library.json`` (relative paths are
                resolved from the project root).
            chatgpt_key: Optional OpenAI API key; when omitted, uses
                :func:`src.utils.llm_keys.get_openai_api_key`.
            openai_model: Model id passed to the OpenAI chat completions API.

        Raises:
            ExternalServiceError: If the library file is missing, invalid JSON,
                or fails structural validation.
        """
        self._library_path = _resolve_library_path(tone_library_path)
        self._meta, self._tones = self._load_and_validate_library()
        self._openai_model = openai_model.strip() or "gpt-4o-mini"
        resolved_key = (chatgpt_key or get_openai_api_key() or "").strip()
        self._chatgpt_key = resolved_key
        self._openai_client: Any = None
        if self._chatgpt_key:
            from openai import OpenAI

            self._openai_client = OpenAI(api_key=self._chatgpt_key)
        self.last_variation_cost_usd: float = 0.0
        logger.info(
            "ToneManager initialized path=%s tones=%s openai_ready=%s",
            self._library_path,
            len(self._tones),
            bool(self._openai_client),
        )

    def _load_and_validate_library(self) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        if not self._library_path.is_file():
            raise ExternalServiceError(
                f"Tone library not found: {self._library_path}. "
                "Create config/tone_library.json or pass a valid tone_library_path."
            )
        try:
            with self._library_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except json.JSONDecodeError as exc:
            raise ExternalServiceError(
                f"Invalid JSON in tone library {self._library_path}: {exc}"
            ) from exc
        except OSError as exc:
            raise ExternalServiceError(
                f"Could not read tone library {self._library_path}: {exc}"
            ) from exc

        if not isinstance(data, dict):
            raise ExternalServiceError("Tone library root must be a JSON object.")
        tones = data.get("tones")
        if not isinstance(tones, list) or not tones:
            raise ExternalServiceError("Tone library must contain a non-empty 'tones' array.")
        meta = data.get("meta") if isinstance(data.get("meta"), dict) else {}
        for idx, tone in enumerate(tones):
            if not isinstance(tone, dict):
                raise ExternalServiceError(f"Tone entry {idx} must be an object.")
            for key in ("id", "name", "variations"):
                if key not in tone:
                    raise ExternalServiceError(
                        f"Tone entry {idx} missing required field '{key}' in {self._library_path}."
                    )
            if not isinstance(tone["variations"], list) or not tone["variations"]:
                raise ExternalServiceError(
                    f"Tone '{tone.get('id')}' must include a non-empty 'variations' list."
                )
            if not isinstance(tone.get("best_for", []), list):
                raise ExternalServiceError(
                    f"Tone '{tone.get('id')}' field 'best_for' must be a list when present."
                )
        return meta, tones

    def _default_tone(self) -> dict[str, Any]:
        """Return the configured fallback tone or the first tone in the library."""
        for tone in self._tones:
            if tone.get("id") == DEFAULT_TONE_ID:
                return tone
        logger.warning(
            "Fallback tone id %r not found; using first library entry.", DEFAULT_TONE_ID
        )
        return self._tones[0]

    def _cost_per_variation_call(self) -> float:
        raw = self._meta.get("estimated_usd_per_chatgpt_variation", 0.04)
        try:
            return max(0.0, float(raw))
        except (TypeError, ValueError):
            logger.warning("Invalid meta.estimated_usd_per_chatgpt_variation; using 0.04")
            return 0.04

    def identify_content_type(self, script: str) -> str:
        """Infer a coarse content label from ``script`` text (keyword heuristic).

        The returned string is matched (case-insensitive) against each tone's
        ``best_for`` entries in :meth:`get_applicable_tones`.

        Args:
            script: Full narration script.

        Returns:
            A short category label such as ``\"tutorial\"`` or ``\"news\"``.
        """
        if not (script or "").strip():
            logger.debug("identify_content_type: empty script; defaulting to educational.")
            return "educational"

        text = script.lower()

        rules: list[tuple[tuple[str, ...], str]] = [
            (
                (
                    "tutorial",
                    "step-by-step",
                    "step by step",
                    "lesson",
                    "in this video",
                    "chapter",
                ),
                "tutorial",
            ),
            (("workout", "gym", "reps", "muscle", "cardio", "exercise", "fitness"), "fitness"),
            (("motivat", "mindset", "discipline", "habit", "self-help"), "motivation"),
            (
                ("story", "i remember", "when i was", "personal", "my journey"),
                "personal story",
            ),
            (("lifestyle", "routine", "morning", "aesthetic", "day in the life"), "lifestyle"),
            (("mystery", "what if", "nobody knows", "strange", "unsolved"), "mystery"),
            (("how it works", "under the hood", "engineering", "mechanism"), "how-it-works"),
            (("hack", "tip", "trick", "shortcut", "quick tip"), "quick tips"),
            (("breaking", "headline", "today in", "news"), "news"),
            (("documentary", "evidence", "research shows", "study"), "documentary"),
        ]
        for keywords, label in rules:
            if any(k in text for k in keywords):
                logger.info("identify_content_type matched label=%r", label)
                return label

        if re.search(r"\b\d+\s*(tips|ways|reasons|mistakes)\b", text):
            logger.info("identify_content_type matched listicle heuristic -> quick tips")
            return "quick tips"

        logger.info("identify_content_type default -> educational")
        return "educational"

    def get_applicable_tones(self, content_type: str) -> list[dict[str, Any]]:
        """Return tones whose ``best_for`` matches ``content_type``.

        Matching is case-insensitive and uses substring containment in either
        direction between ``content_type`` and each ``best_for`` string. If no
        tone matches, **all** tones are returned so selection can still proceed.

        Args:
            content_type: Label from :meth:`identify_content_type` or caller.

        Returns:
            List of tone dictionaries from the library.
        """
        needle = (content_type or "").strip().lower()
        if not needle:
            logger.warning("get_applicable_tones: empty content_type; returning all tones.")
            return list(self._tones)

        applicable: list[dict[str, Any]] = []
        for tone in self._tones:
            best_for = [str(b).lower() for b in tone.get("best_for", []) if str(b).strip()]
            for bucket in best_for:
                if needle == bucket or needle in bucket or bucket in needle:
                    applicable.append(tone)
                    break

        if not applicable:
            logger.info(
                "No tone best_for matched content_type=%r; using full library.", content_type
            )
            return list(self._tones)

        logger.info(
            "get_applicable_tones content_type=%r matched_count=%s",
            content_type,
            len(applicable),
        )
        return applicable

    def select_random_tone(
        self,
        applicable_tones: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Randomly pick one tone dict from ``applicable_tones`` or the full library.

        Args:
            applicable_tones: Candidate tones; ``None`` uses the entire library.

        Returns:
            Selected tone object. On empty input, falls back to
            ``professional_educational`` (or the first tone).
        """
        pool = applicable_tones if applicable_tones is not None else list(self._tones)
        if not pool:
            logger.error("select_random_tone: empty pool; using default tone.")
            return self._default_tone()

        try:
            chosen = random.choice(pool)
        except Exception as exc:  # noqa: BLE001
            logger.exception("select_random_tone failed: %s", exc)
            return self._default_tone()

        logger.info(
            "select_random_tone picked id=%r name=%r",
            chosen.get("id"),
            chosen.get("name"),
        )
        return chosen

    def _call_openai_rewrite(self, script: str, variation_prompt: str) -> str:
        if self._openai_client is None:
            raise ExternalServiceError(
                "OpenAI key is not configured. Set OPENAI_API_KEY / keychain or pass chatgpt_key=."
            )
        system = (
            "You rewrite faceless YouTube narration scripts. Preserve factual claims "
            "unless they are clearly placeholder. Output only the rewritten script body."
        )
        user = (
            f"Variation direction:\n{variation_prompt}\n\n"
            f"Original script:\n{script.strip()}\n\n"
            "Return the full rewritten script only."
        )
        try:
            response = self._openai_client.chat.completions.create(
                model=self._openai_model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.75,
                max_tokens=3600,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("OpenAI rewrite failed during tone variation")
            raise ExternalServiceError(f"Tone variation OpenAI call failed: {exc}") from exc

        text = (response.choices[0].message.content or "").strip()
        if not text:
            raise ExternalServiceError("OpenAI returned an empty rewrite for a tone variation.")
        return text

    def generate_variations(self, script: str, tone: dict[str, Any]) -> list[dict[str, Any]]:
        """Produce two or three rewrites of ``script`` guided by ``tone`` prompts.

        Uses the first ``k`` entries from ``tone['variations']`` where ``k`` is
        ``min(3, max(2, len(variations)))`` so libraries with three prompts emit
        three variants; shorter lists emit two when two prompts exist.

        Args:
            script: Source narration script.
            tone: Tone dictionary (typically from :meth:`select_random_tone`).

        Returns:
            List of variation metadata dicts with ``variation_number``, ``tone_id``,
            ``tone_name``, ``script``, ``timestamp``.

        Raises:
            ValidationError: If ``script`` is empty.
            ExternalServiceError: If OpenAI is not configured or a call fails.
        """
        if not (script or "").strip():
            raise ValidationError("generate_variations requires a non-empty script.")

        prompts = [str(p).strip() for p in (tone.get("variations") or []) if str(p).strip()]
        if not prompts:
            raise ExternalServiceError(
                f"Tone id={tone.get('id')!r} has no usable variation prompts."
            )

        count = min(3, max(2, len(prompts)))
        count = min(count, len(prompts))
        selected = prompts[:count]
        per_call = self._cost_per_variation_call()
        self.last_variation_cost_usd = 0.0

        tone_id = str(tone.get("id") or "unknown")
        tone_name = str(tone.get("name") or tone_id)
        out: list[dict[str, Any]] = []

        for idx, prompt in enumerate(selected, start=1):
            rewritten = self._call_openai_rewrite(script, prompt)
            self.last_variation_cost_usd = round(self.last_variation_cost_usd + per_call, 6)
            out.append(
                {
                    "variation_number": idx,
                    "tone_id": tone_id,
                    "tone_name": tone_name,
                    "script": rewritten,
                    "timestamp": _utc_timestamp(),
                }
            )
            logger.info(
                "generate_variations completed n=%s tone_id=%s cost_total_est=%s",
                idx,
                tone_id,
                self.last_variation_cost_usd,
            )

        return out
