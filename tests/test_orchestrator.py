"""Unit tests for Stage 2 orchestrator and configuration loading."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from src.core.config_loader import ConfigLoader
from src.core.orchestrator import VideoProductionOrchestrator
from src.utils.exceptions import ConfigurationError


def _write_minimal_configs(target_dir: Path) -> None:
    """Create the three required JSON config files for :class:`ConfigLoader`."""
    settings = {
        "orchestrator": {
            "default_topic": "Test topic from settings",
            "default_category": "education",
            "log_level": "INFO",
            "verbose": False,
            "video_output_relative": "data/videos",
            "placeholder_video_basename": "unit_test_output.mp4",
            "placeholder_tone": "calm",
            "placeholder_agent_pass": True,
            "placeholder_script_template": "Script for {topic} in {category}.",
        }
    }
    (target_dir / "settings.json").write_text(
        json.dumps(settings),
        encoding="utf-8",
    )
    (target_dir / "agent_prompts.json").write_text(
        json.dumps({"verification": {"system": "test"}}),
        encoding="utf-8",
    )
    (target_dir / "script_prompts.json").write_text(
        json.dumps({"script_generation": {"system": "test"}}),
        encoding="utf-8",
    )


def test_config_loader_init(tmp_path: Path) -> None:
    """``ConfigLoader`` loads the three required JSON files from a directory."""
    _write_minimal_configs(tmp_path)
    loader = ConfigLoader(str(tmp_path))
    assert loader.get_setting("orchestrator.default_topic") == "Test topic from settings"


def test_config_loader_returns_dict(tmp_path: Path) -> None:
    """Prompt accessors return mapping objects."""
    _write_minimal_configs(tmp_path)
    loader = ConfigLoader(str(tmp_path))
    assert isinstance(loader.get_agent_prompts(), dict)
    assert isinstance(loader.get_script_prompts(), dict)
    assert "verification" in loader.get_agent_prompts()


def test_error_handling_missing_config(tmp_path: Path) -> None:
    """Missing required JSON raises :class:`ConfigurationError` with a clear path."""
    empty = tmp_path / "empty_cfg"
    empty.mkdir()
    with pytest.raises(ConfigurationError) as excinfo:
        ConfigLoader(str(empty))
    message = str(excinfo.value).lower()
    assert "settings.json" in message or "missing" in message


def test_orchestrator_init(tmp_path: Path) -> None:
    """``VideoProductionOrchestrator`` wires config, logging, and placeholders."""
    _write_minimal_configs(tmp_path)
    orch = VideoProductionOrchestrator(str(tmp_path))
    assert orch.config is not None
    assert orch.deepseek_client is None
    assert orch.chatgpt_client is None


def test_orchestrator_has_required_methods() -> None:
    """Public API surface for the production orchestrator."""
    public = {m for m in dir(VideoProductionOrchestrator) if not m.startswith("_")}
    assert "generate_video" in public
    assert "run_pipeline" in public


def test_orchestrator_run_pipeline_returns_dict(tmp_path: Path) -> None:
    """``run_pipeline`` returns the standardized metadata shape."""
    _write_minimal_configs(tmp_path)
    orch = VideoProductionOrchestrator(str(tmp_path))
    out = orch.run_pipeline()
    assert isinstance(out, dict)
    assert "success" in out
    assert "video_path" in out
    assert "script" in out
    assert "topic" in out
    assert "tone_used" in out
    assert "agent_verification_passed" in out
    assert "timestamp" in out
    assert "duration_seconds" in out
    assert out["success"] is True
    assert out["topic"] == "Test topic from settings"


def test_generate_video_handles_filesystem_errors(tmp_path: Path) -> None:
    """Filesystem failures during assembly return a dict and do not propagate."""
    _write_minimal_configs(tmp_path)
    orch = VideoProductionOrchestrator(str(tmp_path))
    with patch.object(Path, "write_bytes", side_effect=OSError("simulated write failure")):
        out = orch.generate_video(topic="Mock topic", category="general")
    assert isinstance(out, dict)
    assert out["success"] is False
    assert out["failed_step"] == "video_assembly"
    assert out["error"] is not None
    assert "simulated write failure" in out["error"]


def test_config_loader_invalid_json_error_message(tmp_path: Path) -> None:
    """Malformed ``settings.json`` raises :class:`ConfigurationError` with context."""
    cfg = tmp_path / "bad_json"
    cfg.mkdir()
    (cfg / "settings.json").write_text("{not-json", encoding="utf-8")
    (cfg / "agent_prompts.json").write_text("{}", encoding="utf-8")
    (cfg / "script_prompts.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ConfigurationError) as excinfo:
        ConfigLoader(str(cfg))
    assert "invalid json" in str(excinfo.value).lower()
