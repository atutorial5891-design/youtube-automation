"""Unit tests for :class:`ToneManager` and ``tone_library.json``."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.generation.tone_manager import DEFAULT_TONE_ID, ToneManager
from src.utils.exceptions import ExternalServiceError, ValidationError


def _minimal_library() -> dict:
    return {
        "meta": {"estimated_usd_per_chatgpt_variation": 0.01},
        "tones": [
            {
                "id": "professional_educational",
                "name": "Professional Educational",
                "description": "Formal",
                "best_for": ["tutorial", "educational"],
                "variations": ["v1", "v2", "v3"],
            },
            {
                "id": "quick_direct",
                "name": "Quick",
                "description": "Fast",
                "best_for": ["news", "quick tips"],
                "variations": ["q1", "q2", "q3"],
            },
        ],
    }


@pytest.fixture
def library_path(tmp_path: Path) -> Path:
    p = tmp_path / "tone_library.json"
    p.write_text(json.dumps(_minimal_library()), encoding="utf-8")
    return p


@pytest.fixture
def mock_openai(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    create = MagicMock()
    fake = MagicMock()
    fake.chat.completions.create = create
    monkeypatch.setattr("openai.OpenAI", MagicMock(return_value=fake))
    return create


def test_tone_manager_init(library_path: Path) -> None:
    tm = ToneManager(str(library_path), chatgpt_key="sk-test")
    assert len(tm._tones) == 2
    assert tm._library_path == library_path.resolve()


def test_tone_library_loads(library_path: Path) -> None:
    tm = ToneManager(str(library_path))
    ids = {t["id"] for t in tm._tones}
    assert ids == {"professional_educational", "quick_direct"}


def test_identify_content_type(library_path: Path) -> None:
    tm = ToneManager(str(library_path))
    assert tm.identify_content_type("Welcome to this step by step tutorial") == "tutorial"
    assert tm.identify_content_type("Today's news update") == "news"
    assert tm.identify_content_type("x" * 50) == "educational"


def test_get_applicable_tones(library_path: Path) -> None:
    tm = ToneManager(str(library_path))
    hits = tm.get_applicable_tones("tutorial")
    assert any(t["id"] == "professional_educational" for t in hits)
    all_tones = tm.get_applicable_tones("nonexistent_label_xyz")
    assert len(all_tones) == len(tm._tones)


def test_select_random_tone(library_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    tm = ToneManager(str(library_path))
    fixed = tm._tones[1]
    monkeypatch.setattr("random.choice", lambda pool: fixed)
    picked = tm.select_random_tone(tm._tones)
    assert picked["id"] == "quick_direct"


def test_select_random_tone_empty_pool_fallback(library_path: Path) -> None:
    tm = ToneManager(str(library_path))
    picked = tm.select_random_tone([])
    assert picked.get("id") == DEFAULT_TONE_ID


def test_generate_variations_returns_list(
    library_path: Path, mock_openai: MagicMock
) -> None:
    def _resp(text: str) -> MagicMock:
        msg = MagicMock()
        msg.content = text
        ch = MagicMock()
        ch.message = msg
        r = MagicMock()
        r.choices = [ch]
        return r

    mock_openai.side_effect = [
        _resp("Rewrite A"),
        _resp("Rewrite B"),
        _resp("Rewrite C"),
    ]
    tm = ToneManager(str(library_path), chatgpt_key="sk")
    tone = next(t for t in tm._tones if t["id"] == "professional_educational")
    out = tm.generate_variations("Original script body.", tone)
    assert isinstance(out, list)
    assert len(out) == 3


def test_variations_have_correct_format(
    library_path: Path, mock_openai: MagicMock
) -> None:
    msg = MagicMock()
    msg.content = "Only rewrite"
    ch = MagicMock()
    ch.message = msg
    mock_openai.return_value = MagicMock(choices=[ch])

    tm = ToneManager(str(library_path), chatgpt_key="sk")
    tone = tm._tones[0]
    # Two prompts only -> expect 2 variations
    tone = {
        **tone,
        "variations": ["a", "b"],
    }
    out = tm.generate_variations("Script", tone)
    for row in out:
        for key in ("variation_number", "tone_id", "tone_name", "script", "timestamp"):
            assert key in row
        assert isinstance(row["variation_number"], int)
        assert isinstance(row["script"], str)


def test_variation_count_is_2_or_3(library_path: Path, mock_openai: MagicMock) -> None:
    msg = MagicMock()
    msg.content = "x"
    ch = MagicMock()
    ch.message = msg
    mock_openai.return_value = MagicMock(choices=[ch])

    tm = ToneManager(str(library_path), chatgpt_key="sk")

    tone3 = {**tm._tones[0], "variations": ["p1", "p2", "p3"]}
    out3 = tm.generate_variations("s" * 40, tone3)
    assert len(out3) in (2, 3)
    assert len(out3) == 3

    tone2 = {**tm._tones[0], "variations": ["p1", "p2"]}
    out2 = tm.generate_variations("s" * 40, tone2)
    assert len(out2) == 2


def test_generate_variations_cost_tracking(
    library_path: Path, mock_openai: MagicMock
) -> None:
    msg = MagicMock()
    msg.content = "rewritten"
    mock_openai.return_value = MagicMock(choices=[MagicMock(message=msg)])

    tm = ToneManager(str(library_path), chatgpt_key="sk")
    tone = {**tm._tones[0], "variations": ["a", "b"]}
    tm.generate_variations("body", tone)
    assert tm.last_variation_cost_usd == pytest.approx(0.02, rel=1e-3)


def test_generate_variations_empty_script_raises(library_path: Path) -> None:
    tm = ToneManager(str(library_path), chatgpt_key="sk")
    with pytest.raises(ValidationError):
        tm.generate_variations("   ", tm._tones[0])


def test_missing_tone_file_raises(tmp_path: Path) -> None:
    missing = tmp_path / "nope.json"
    with pytest.raises(ExternalServiceError):
        ToneManager(str(missing))
