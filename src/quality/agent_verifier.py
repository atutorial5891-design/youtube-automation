"""Gate 2 script verification using a ChatGPT-class writing model (no DeepSeek)."""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from typing import Any

from src.utils.constants import PROJECT_ROOT
from src.utils.exceptions import ExternalServiceError, ValidationError

logger = logging.getLogger(__name__)

# Orchestration policy (this class does not retry; callers enforce the cap).
MAX_SCRIPT_RETRIES = 3

_PASS_CLARITY = 80
_PASS_FLOW = 80
_PASS_ENGAGEMENT = 70


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_default_agent_prompts() -> dict[str, Any]:
    path = PROJECT_ROOT / "config" / "agent_prompts.json"
    if not path.is_file():
        raise ExternalServiceError(
            f"Agent prompts not found at {path}. Pass agent_prompts= to AgentVerifier."
        )
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ExternalServiceError("agent_prompts.json must contain a JSON object.")
    return data


def _strip_code_fence(text: str) -> str:
    stripped = text.strip()
    if not stripped.startswith("```"):
        return stripped
    lines = stripped.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def _extract_json_object(text: str) -> dict[str, Any] | None:
    """Parse the first JSON object found in ``text``."""
    cleaned = _strip_code_fence(text)
    try:
        parsed = json.loads(cleaned)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{[\s\S]*\}", cleaned)
    if not match:
        return None
    try:
        parsed = json.loads(match.group(0))
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        return None


class AgentVerifier:
    """Run structured quality scoring on a script via OpenAI (Gate 2).

    **Allocation:** verification uses the same class of model as script writing
    (OpenAI/Anthropic in ``ChatGPTClient`` style), never DeepSeek.

    **Gate 2 operations:** production targets **≥80% first-pass** verification
    success; the orchestrator may call :meth:`verify_script` up to ``1 +
    MAX_SCRIPT_RETRIES`` times total. This class performs **one** model call per
    invocation and does not loop internally.
    """

    MAX_SCRIPT_RETRIES: int = MAX_SCRIPT_RETRIES

    def __init__(
        self,
        chatgpt_key: str,
        model: str = "gpt-4o-mini",
        *,
        agent_prompts: dict[str, Any] | None = None,
    ) -> None:
        """Store credentials and verification prompts.

        Args:
            chatgpt_key: OpenAI API key for the verifier.
            model: Chat model id (default ``gpt-4o-mini``).
            agent_prompts: Optional ``agent_prompts.json`` structure; otherwise
                loaded from ``config/agent_prompts.json``.

        Raises:
            ExternalServiceError: If prompts cannot be loaded.
            ValidationError: If ``chatgpt_key`` is empty.
        """
        if not isinstance(chatgpt_key, str) or not chatgpt_key.strip():
            raise ValidationError("chatgpt_key must be a non-empty string.")
        self._api_key = chatgpt_key.strip()
        self._model = model.strip() or "gpt-4o-mini"
        self._prompts = agent_prompts or _load_default_agent_prompts()
        block = self._prompts.get("verification") or {}
        if not isinstance(block, dict) or "system" not in block:
            raise ExternalServiceError(
                "agent_prompts['verification'] must include a 'system' string."
            )
        self._system_prompt = str(block.get("system"))
        self._user_template = str(
            block.get("user_template")
            or "Review the script and return JSON scores.\n\nScript:\n{{script}}"
        )
        self._init_openai_client()

    def _init_openai_client(self) -> None:
        from openai import OpenAI

        self._client = OpenAI(api_key=self._api_key)

    def _invoke_model(self, user_message: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": self._system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.2,
                max_tokens=1200,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Agent verification API call failed")
            raise ExternalServiceError(f"Agent verification request failed: {exc}") from exc

        choice0 = response.choices[0]
        content = (choice0.message.content or "").strip()
        if not content:
            raise ExternalServiceError("Agent verification returned empty content.")
        return content

    @staticmethod
    def _safe_int(value: Any, default: int = 0) -> int:
        try:
            if isinstance(value, bool):
                return default
            if isinstance(value, (int, float)):
                return int(round(float(value)))
            if isinstance(value, str) and value.strip().isdigit():
                return int(value.strip())
            return int(float(str(value).strip()))
        except (TypeError, ValueError):
            return default

    def _evaluate_pass(
        self,
        clarity: int,
        flow: int,
        engagement: int,
        issues_count: int,
    ) -> bool:
        return (
            clarity >= _PASS_CLARITY
            and flow >= _PASS_FLOW
            and engagement >= _PASS_ENGAGEMENT
            and issues_count == 0
        )

    def verify_script(
        self,
        script: str,
        topic: str | None = None,
        *,
        attempt: int = 1,
    ) -> dict[str, Any]:
        """Score ``script`` and return a Gate 2 style verdict dict.

        A single OpenAI call is made; retries are the caller's responsibility
        (up to :attr:`MAX_SCRIPT_RETRIES` additional attempts).

        Args:
            script: Full narration script text.
            topic: Optional topic line for evaluator context.
            attempt: 1-based attempt index for logging and output metadata.

        Returns:
            Dictionary with ``result`` (``PASS`` / ``FAIL``), ``scores``,
            ``feedback``, ``suggestion``, ``attempt``, and ``timestamp``.

        Raises:
            ValidationError: If ``script`` is empty after stripping.
            ExternalServiceError: If the model call fails or returns unusable text.
        """
        if not (script or "").strip():
            raise ValidationError("verify_script requires a non-empty script.")

        topic_context = (topic or "").strip() or "(none provided)"
        schema_hint = (
            "Return ONLY one JSON object with keys: "
            "clarity (int 0-100), flow (int 0-100), engagement (int 0-100), "
            "issues_count (int, count of CRITICAL issues only: safety, incoherence, "
            "unfilmable or policy-blocking problems), "
            "feedback (string summarizing the verdict), "
            "suggestion (string with one concrete improvement if FAIL, else brief praise)."
        )
        user_body = (
            self._user_template.replace("{{script}}", script.strip()).replace(
                "{{topic}}", topic_context
            )
            + "\n\n"
            + schema_hint
        )

        logger.info(
            "Agent verification starting attempt=%s model=%s script_len=%s",
            attempt,
            self._model,
            len(script),
        )
        raw = self._invoke_model(user_body)
        payload = _extract_json_object(raw)
        if not payload:
            logger.error("Agent verification could not parse JSON from model output.")
            raise ExternalServiceError(
                "Agent verifier could not parse JSON scores from the model response."
            )

        clarity = max(0, min(100, self._safe_int(payload.get("clarity"), 0)))
        flow = max(0, min(100, self._safe_int(payload.get("flow"), 0)))
        engagement = max(0, min(100, self._safe_int(payload.get("engagement"), 0)))
        issues_count = max(0, self._safe_int(payload.get("issues_count"), 999))
        feedback = str(payload.get("feedback") or "").strip() or "No feedback provided."
        suggestion = str(payload.get("suggestion") or "").strip() or "No suggestion provided."

        passed = self._evaluate_pass(clarity, flow, engagement, issues_count)
        result_label = "PASS" if passed else "FAIL"

        out: dict[str, Any] = {
            "result": result_label,
            "scores": {
                "clarity": clarity,
                "flow": flow,
                "engagement": engagement,
                "issues_count": issues_count,
            },
            "feedback": feedback,
            "suggestion": suggestion,
            "attempt": int(attempt),
            "timestamp": _utc_timestamp(),
        }
        logger.info(
            "Agent verification finished attempt=%s result=%s clarity=%s flow=%s "
            "engagement=%s issues_count=%s",
            attempt,
            result_label,
            clarity,
            flow,
            engagement,
            issues_count,
        )
        return out
