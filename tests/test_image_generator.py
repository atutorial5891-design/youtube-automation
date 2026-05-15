"""Tests for :class:`ImageGenerator` (Ollama + local PNG output)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.generation.image_generator import ImageGenerator
from src.utils.exceptions import ExternalServiceError, ValidationError


def _write_prompts(path: Path) -> None:
    data = {
        "templates": [
            "wide shot of {{subject}}",
            "macro detail of {{subject}}",
            "studio portrait of {{subject}}",
        ]
    }
    path.write_text(json.dumps(data), encoding="utf-8")


def test_image_generator_init(tmp_path: Path) -> None:
    prompts = tmp_path / "image_prompts.json"
    _write_prompts(prompts)
    out = tmp_path / "out"
    gen = ImageGenerator(
        model="sdxl",
        base_url="http://127.0.0.1:9",
        image_prompts_path=prompts,
        output_dir=out,
    )
    assert gen._model == "sdxl"
    assert len(gen._templates) == 3


def test_generate_image_returns_list(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    prompts = tmp_path / "image_prompts.json"
    _write_prompts(prompts)
    out = tmp_path / "out"
    monkeypatch.setattr(
        "src.generation.image_generator.ImageGenerator._ollama_tags_ok",
        lambda self: False,
    )
    gen = ImageGenerator(
        base_url="http://127.0.0.1:9",
        image_prompts_path=prompts,
        output_dir=out,
    )
    paths = gen.generate_image("a futuristic city", num_images=2)
    assert isinstance(paths, list)
    assert len(paths) == 2


def test_generate_image_creates_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    prompts = tmp_path / "image_prompts.json"
    _write_prompts(prompts)
    out = tmp_path / "out"
    monkeypatch.setattr(
        "src.generation.image_generator.ImageGenerator._ollama_tags_ok",
        lambda self: False,
    )
    gen = ImageGenerator(image_prompts_path=prompts, output_dir=out)
    paths = gen.generate_image("mountain landscape", num_images=1)
    p = Path(paths[0])
    assert p.is_file()
    assert p.suffix.lower() == ".png"


def test_select_random_prompt_returns_list(tmp_path: Path) -> None:
    prompts = tmp_path / "image_prompts.json"
    _write_prompts(prompts)
    gen = ImageGenerator(image_prompts_path=prompts, output_dir=tmp_path / "o")
    lines = gen.select_random_prompt("electric vehicles", count=3)
    assert len(lines) == 3
    assert all("electric vehicles" in line for line in lines)


def test_generate_with_variation_returns_list(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    prompts = tmp_path / "image_prompts.json"
    _write_prompts(prompts)
    out = tmp_path / "out"
    monkeypatch.setattr(
        "src.generation.image_generator.ImageGenerator._ollama_tags_ok",
        lambda self: False,
    )
    gen = ImageGenerator(image_prompts_path=prompts, output_dir=out)
    paths = gen.generate_with_variation("coffee brewing", num_variations=2)
    assert isinstance(paths, list)
    assert len(paths) == 2


def test_error_handling_ollama_not_running(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    prompts = tmp_path / "image_prompts.json"
    _write_prompts(prompts)
    out = tmp_path / "out"

    def boom(_self) -> bool:
        return False

    monkeypatch.setattr("src.generation.image_generator.ImageGenerator._ollama_tags_ok", boom)
    gen = ImageGenerator(image_prompts_path=prompts, output_dir=out)
    paths = gen.generate_image("still saves placeholders", num_images=1)
    assert Path(paths[0]).is_file()


def test_select_random_prompt_empty_topic(tmp_path: Path) -> None:
    prompts = tmp_path / "image_prompts.json"
    _write_prompts(prompts)
    gen = ImageGenerator(image_prompts_path=prompts, output_dir=tmp_path / "o")
    with pytest.raises(ValidationError):
        gen.select_random_prompt("   ", count=2)


def test_missing_templates_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"
    with pytest.raises(ExternalServiceError):
        ImageGenerator(image_prompts_path=missing, output_dir=tmp_path / "o")


def test_invalid_json_image_prompts(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{ not json", encoding="utf-8")
    with pytest.raises(ExternalServiceError) as exc:
        ImageGenerator(image_prompts_path=bad, output_dir=tmp_path / "o")
    assert "Invalid JSON" in str(exc.value)
