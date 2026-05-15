"""Unit tests for DeepSeekClient, ChatGPTClient, and HybridScriptGenerator."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.api.chatgpt_client import ChatGPTClient
from src.api.deepseek_client import DeepSeekClient
from src.core.config_loader import ConfigLoader
from src.generation.script_generator import HybridScriptGenerator
from src.utils.exceptions import ExternalServiceError, ValidationError


def _write_config_bundle(target: Path) -> None:
    """Minimal config tree for :class:`ConfigLoader` in isolated tests."""
    settings = {
        "hybrid_generation": {
            "deepseek_topic_usd": 0.01,
            "deepseek_outline_usd": 0.02,
            "chatgpt_script_usd": 0.1,
        }
    }
    (target / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
    (target / "agent_prompts.json").write_text(json.dumps({"x": 1}), encoding="utf-8")
    prompts = {
        "topic_research": {
            "system": "sys",
            "user_template": "Niche: {{niche}}",
        },
        "outline_generation": {
            "system": "sys2",
            "user_template": "Topic {{topic}} audience {{audience}} length {{target_length}}",
        },
        "script_generation": {
            "system": "sys3",
            "user_template": "Outline:\n{{outline}}\nTone {{tone}} len {{target_duration}}",
        },
    }
    (target / "script_prompts.json").write_text(json.dumps(prompts), encoding="utf-8")


def _minimal_prompts() -> dict:
    return {
        "topic_research": {"system": "s", "user_template": "{{niche}}"},
        "outline_generation": {
            "system": "s2",
            "user_template": "{{topic}} / {{audience}} / {{target_length}}",
        },
        "script_generation": {
            "system": "s3",
            "user_template": "{{outline}} / {{tone}} / {{target_duration}}",
        },
    }


@pytest.fixture
def mock_post(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Patch ``requests.post`` used by :class:`DeepSeekClient`."""
    m = MagicMock()
    monkeypatch.setattr("src.api.deepseek_client.requests.post", m)
    return m


@pytest.fixture
def mock_openai_create(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Patch ``openai.OpenAI`` so ``ChatGPTClient`` never opens a real session."""
    create = MagicMock()
    fake_client = MagicMock()
    fake_client.chat.completions.create = create
    monkeypatch.setattr("openai.OpenAI", MagicMock(return_value=fake_client))
    return create


def test_deepseek_init() -> None:
    """DeepSeek client stores key, model, and loads prompts from disk."""
    client = DeepSeekClient("sk-test", model="deepseek-chat")
    assert client.api_key == "sk-test"
    assert client.model == "deepseek-chat"
    assert client.is_configured() is True


def test_chatgpt_init() -> None:
    """ChatGPT client normalizes OpenAI defaults."""
    client = ChatGPTClient("sk-openai-test", model="gpt-4o-mini", provider="openai")
    assert client.api_key == "sk-openai-test"
    assert client.model == "gpt-4o-mini"
    cfg = client.current_config()
    assert cfg["provider"] == "openai"


def test_generate_topic(mock_post: MagicMock) -> None:
    """Topic generation parses assistant text from a mocked DeepSeek response."""
    resp = MagicMock()
    resp.status_code = 200
    resp.raise_for_status = MagicMock()
    resp.json.return_value = {"choices": [{"message": {"content": "1) How sleep affects focus"}}]}
    mock_post.return_value = resp

    client = DeepSeekClient("k", script_prompts=_minimal_prompts())
    topic = client.generate_topic("health", trendy=False)
    assert isinstance(topic, str)
    assert "sleep" in topic.lower()
    mock_post.assert_called()


def test_create_outline(mock_post: MagicMock) -> None:
    """Outline creation returns assistant body text."""
    resp = MagicMock()
    resp.status_code = 200
    resp.raise_for_status = MagicMock()
    resp.json.return_value = {
        "choices": [{"message": {"content": "I. Intro\nII. Main"}}]
    }
    mock_post.return_value = resp

    client = DeepSeekClient("k", script_prompts=_minimal_prompts())
    outline = client.create_outline("Test topic", content_type="short")
    assert isinstance(outline, str)
    assert "Intro" in outline


def test_write_script(mock_openai_create: MagicMock) -> None:
    """Script writing unwraps OpenAI chat completion content."""
    choice = MagicMock()
    choice.message.content = "HOOK\n...\nBODY\n...\nCTA\nSubscribe!"
    mock_openai_create.return_value.choices = [choice]

    client = ChatGPTClient("k", model="gpt-4o-mini", script_prompts=_minimal_prompts())
    text = client.write_script("Topic", outline="Outline text", style="youtube_faceless")
    assert isinstance(text, str)
    assert "HOOK" in text
    mock_openai_create.assert_called_once()


def test_hybrid_script_generator_init(tmp_path: Path) -> None:
    """Hybrid generator wires DeepSeek + writer with a config loader."""
    _write_config_bundle(tmp_path)
    loader = ConfigLoader(str(tmp_path))
    gen = HybridScriptGenerator(
        "deepseek-key",
        "writer-key",
        chatgpt_model="gpt-4o-mini",
        config_loader=loader,
    )
    assert gen._deepseek.is_configured()
    assert gen._writer.is_configured()


def test_generate_script_returns_dict(tmp_path: Path) -> None:
    """End-to-end hybrid output exposes all required metadata keys."""
    _write_config_bundle(tmp_path)
    loader = ConfigLoader(str(tmp_path))

    with patch.object(DeepSeekClient, "generate_topic", return_value="My Topic"), patch.object(
        DeepSeekClient, "create_outline", return_value="My Outline"
    ), patch.object(ChatGPTClient, "write_script", return_value="Full script body."):
        gen = HybridScriptGenerator("ds", "cg", config_loader=loader)
        out = gen.generate_script("tech")

    assert isinstance(out, dict)
    for key in (
        "topic",
        "outline",
        "script",
        "category",
        "api_cost",
        "api_split",
        "timestamp",
        "model_versions",
    ):
        assert key in out
    assert out["topic"] == "My Topic"
    assert out["category"] == "tech"
    assert "deepseek_model" in out["model_versions"]
    assert "chatgpt_model" in out["model_versions"]


def test_api_split_in_output(tmp_path: Path) -> None:
    """Cost breakdown sums to ``api_cost`` using configured estimates."""
    _write_config_bundle(tmp_path)
    loader = ConfigLoader(str(tmp_path))

    with patch.object(DeepSeekClient, "generate_topic", return_value="T"), patch.object(
        DeepSeekClient, "create_outline", return_value="O"
    ), patch.object(ChatGPTClient, "write_script", return_value="S"):
        gen = HybridScriptGenerator("ds", "cg", config_loader=loader)
        out = gen.generate_script("finance")

    assert out["api_split"]["deepseek"] == pytest.approx(0.03)
    assert out["api_split"]["chatgpt"] == pytest.approx(0.1)
    assert out["api_cost"] == pytest.approx(0.13)


def test_generate_script_with_locked_topic_skips_topic_generation(
    tmp_path: Path,
) -> None:
    """When ``topic`` is provided, DeepSeek topic generation is skipped."""
    _write_config_bundle(tmp_path)
    loader = ConfigLoader(str(tmp_path))

    with patch.object(DeepSeekClient, "generate_topic") as mock_topic, patch.object(
        DeepSeekClient, "create_outline", return_value="Outline body"
    ), patch.object(ChatGPTClient, "write_script", return_value="Final script"):
        gen = HybridScriptGenerator("ds", "cg", config_loader=loader)
        out = gen.generate_script("tech", topic="Locked title")

    mock_topic.assert_not_called()
    assert out["topic"] == "Locked title"
    assert out["api_split"]["deepseek"] == pytest.approx(0.02)
    assert out["api_split"]["chatgpt"] == pytest.approx(0.1)


def test_error_handling_deepseek(tmp_path: Path) -> None:
    """Hybrid retries DeepSeek topic once, then raises if still empty."""
    _write_config_bundle(tmp_path)
    loader = ConfigLoader(str(tmp_path))

    with patch.object(
        DeepSeekClient,
        "generate_topic",
        side_effect=[None, None],
    ):
        gen = HybridScriptGenerator("ds", "cg", config_loader=loader)
        with pytest.raises(ExternalServiceError) as exc:
            gen.generate_script("lifestyle")
    assert "topic" in str(exc.value).lower()


def test_error_handling_chatgpt(tmp_path: Path) -> None:
    """Writing model failures propagate (orchestrator-level retries)."""
    _write_config_bundle(tmp_path)
    loader = ConfigLoader(str(tmp_path))

    with patch.object(DeepSeekClient, "generate_topic", return_value="T"), patch.object(
        DeepSeekClient, "create_outline", return_value="O"
    ), patch.object(
        ChatGPTClient,
        "write_script",
        side_effect=ExternalServiceError("writer down"),
    ):
        gen = HybridScriptGenerator("ds", "cg", config_loader=loader)
        with pytest.raises(ExternalServiceError) as exc:
            gen.generate_script("general")
    assert "writer down" in str(exc.value)


def test_hybrid_invalid_category(tmp_path: Path) -> None:
    """Empty category is rejected before any API call."""
    _write_config_bundle(tmp_path)
    loader = ConfigLoader(str(tmp_path))
    gen = HybridScriptGenerator("ds", "cg", config_loader=loader)
    with pytest.raises(ValidationError):
        gen.generate_script("   ")


def test_deepseek_retries_on_transient_http(mock_post: MagicMock) -> None:
    """DeepSeek client retries after HTTP 503 then succeeds."""
    fail = MagicMock()
    fail.status_code = 503
    fail.raise_for_status = MagicMock()

    ok = MagicMock()
    ok.status_code = 200
    ok.raise_for_status = MagicMock()
    ok.json.return_value = {"choices": [{"message": {"content": "Topic line"}}]}

    mock_post.side_effect = [fail, ok]

    client = DeepSeekClient("k", script_prompts=_minimal_prompts(), max_retries=2)
    topic = client.generate_topic("general", trendy=False)
    assert topic == "Topic line"
    assert mock_post.call_count >= 2
