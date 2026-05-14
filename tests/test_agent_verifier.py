"""Unit tests for :class:`AgentVerifier` (Gate 2)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from src.quality.agent_verifier import MAX_SCRIPT_RETRIES, AgentVerifier
from src.utils.exceptions import ExternalServiceError, ValidationError


@pytest.fixture
def minimal_prompts() -> dict:
    return {
        "verification": {
            "system": "You verify scripts. Return JSON only.",
            "user_template": "Topic: {{topic}}\nScript:\n{{script}}",
        }
    }


@pytest.fixture
def mock_completion(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Patch ``openai.OpenAI`` so no network I/O runs."""
    create = MagicMock()
    fake_client = MagicMock()
    fake_client.chat.completions.create = create
    monkeypatch.setattr("openai.OpenAI", MagicMock(return_value=fake_client))
    return create


def _choice_content(payload: dict) -> MagicMock:
    msg = MagicMock()
    msg.content = json.dumps(payload)
    choice = MagicMock()
    choice.message = msg
    resp = MagicMock()
    resp.choices = [choice]
    return resp


def test_agent_verifier_init(mock_completion: MagicMock, minimal_prompts: dict) -> None:
    v = AgentVerifier("sk-test", model="gpt-4o-mini", agent_prompts=minimal_prompts)
    assert v._model == "gpt-4o-mini"
    mock_completion.assert_not_called()


def test_verify_script_returns_dict(
    mock_completion: MagicMock, minimal_prompts: dict
) -> None:
    mock_completion.return_value = _choice_content(
        {
            "clarity": 90,
            "flow": 88,
            "engagement": 80,
            "issues_count": 0,
            "feedback": "Strong structure.",
            "suggestion": "Ship it.",
        }
    )
    v = AgentVerifier("sk", agent_prompts=minimal_prompts)
    out = v.verify_script("Hook\nBody\nCTA", topic="Sleep")
    assert isinstance(out, dict)


def test_verify_script_result_is_pass_or_fail(
    mock_completion: MagicMock, minimal_prompts: dict
) -> None:
    mock_completion.return_value = _choice_content(
        {
            "clarity": 50,
            "flow": 50,
            "engagement": 50,
            "issues_count": 2,
            "feedback": "Weak",
            "suggestion": "Rewrite hook.",
        }
    )
    v = AgentVerifier("sk", agent_prompts=minimal_prompts)
    out = v.verify_script("short script")
    assert out["result"] in ("PASS", "FAIL")


def test_verify_script_has_all_keys(mock_completion: MagicMock, minimal_prompts: dict) -> None:
    mock_completion.return_value = _choice_content(
        {
            "clarity": 85,
            "flow": 82,
            "engagement": 75,
            "issues_count": 0,
            "feedback": "ok",
            "suggestion": "ok",
        }
    )
    v = AgentVerifier("sk", agent_prompts=minimal_prompts)
    out = v.verify_script("x" * 200)
    for key in ("result", "scores", "feedback", "suggestion", "attempt", "timestamp"):
        assert key in out
    for sk in ("clarity", "flow", "engagement", "issues_count"):
        assert sk in out["scores"]


def test_verify_script_scores_are_integers(
    mock_completion: MagicMock, minimal_prompts: dict
) -> None:
    mock_completion.return_value = _choice_content(
        {
            "clarity": 81.2,
            "flow": 80.0,
            "engagement": 71,
            "issues_count": 0,
            "feedback": "f",
            "suggestion": "s",
        }
    )
    v = AgentVerifier("sk", agent_prompts=minimal_prompts)
    out = v.verify_script("script body here")
    scores = out["scores"]
    assert isinstance(scores["clarity"], int)
    assert isinstance(scores["flow"], int)
    assert isinstance(scores["engagement"], int)
    assert isinstance(scores["issues_count"], int)


def test_verify_script_with_high_quality_script(
    mock_completion: MagicMock, minimal_prompts: dict
) -> None:
    mock_completion.return_value = _choice_content(
        {
            "clarity": 92,
            "flow": 90,
            "engagement": 85,
            "issues_count": 0,
            "feedback": "Clear hook, smooth pacing.",
            "suggestion": "Optional polish on CTA timing.",
        }
    )
    v = AgentVerifier("sk", agent_prompts=minimal_prompts)
    out = v.verify_script("A" * 500, topic="Health habits")
    assert out["result"] == "PASS"
    assert out["scores"]["issues_count"] == 0


def test_verify_script_with_low_quality_script(
    mock_completion: MagicMock, minimal_prompts: dict
) -> None:
    mock_completion.return_value = _choice_content(
        {
            "clarity": 60,
            "flow": 55,
            "engagement": 50,
            "issues_count": 1,
            "feedback": "Critical pacing and clarity issues.",
            "suggestion": "Rebuild hook and remove contradictory claims.",
        }
    )
    v = AgentVerifier("sk", agent_prompts=minimal_prompts)
    out = v.verify_script("bad")
    assert out["result"] == "FAIL"


def test_verify_script_attempt_metadata(
    mock_completion: MagicMock, minimal_prompts: dict
) -> None:
    mock_completion.return_value = _choice_content(
        {
            "clarity": 90,
            "flow": 85,
            "engagement": 72,
            "issues_count": 0,
            "feedback": "ok",
            "suggestion": "ok",
        }
    )
    v = AgentVerifier("sk", agent_prompts=minimal_prompts)
    out = v.verify_script("script", attempt=2)
    assert out["attempt"] == 2


def test_verify_script_empty_raises(minimal_prompts: dict) -> None:
    v = AgentVerifier("sk", agent_prompts=minimal_prompts)
    with pytest.raises(ValidationError):
        v.verify_script("   ")


def test_verify_script_parse_failure_raises(
    mock_completion: MagicMock, minimal_prompts: dict
) -> None:
    msg = MagicMock()
    msg.content = "not json at all"
    choice = MagicMock()
    choice.message = msg
    mock_completion.return_value = MagicMock(choices=[choice])
    v = AgentVerifier("sk", agent_prompts=minimal_prompts)
    with pytest.raises(ExternalServiceError):
        v.verify_script("some script text")


def test_max_retries_constant() -> None:
    assert AgentVerifier.MAX_SCRIPT_RETRIES == MAX_SCRIPT_RETRIES == 3
