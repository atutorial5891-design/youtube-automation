"""Tests for :class:`VideoAssembler` in ``src.video.video_assembler``."""

from __future__ import annotations

import shutil
import struct
import wave
from pathlib import Path

import pytest
from PIL import Image

from src.core.logger import Logger
from src.core.performance_monitor import PerformanceMonitor
from src.utils.exceptions import ValidationError
from src.video import video_assembler as va_mod
from src.video.video_assembler import VideoAssembler


@pytest.fixture(autouse=True)
def _isolate_logs_and_output(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "logs"

    def _factory(name: str) -> Logger:
        return Logger(name, str(root))

    gen = tmp_path / "generated_videos"
    gen.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(va_mod, "Logger", _factory)
    monkeypatch.setattr(va_mod, "OUTPUT_DIR", gen)


@pytest.fixture
def log_root(tmp_path: Path) -> Path:
    return tmp_path / "logs"


@pytest.fixture
def out_dir(tmp_path: Path) -> Path:
    return tmp_path / "generated_videos"


def _write_wav(path: Path, seconds: float = 0.4) -> None:
    n = int(44100 * seconds)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(44100)
        w.writeframes(struct.pack("<" + "h" * n, *([0] * n)))


def _write_png(path: Path) -> None:
    Image.new("RGB", (64, 48), color=(10, 120, 200)).save(path)


def test_video_assembler_init(log_root: Path) -> None:
    asm = VideoAssembler()
    assert asm._fps == 30
    assert asm._size == (1920, 1080)
    assert (log_root / "daily_logs").is_dir()


def test_assemble_video_returns_string(
    log_root: Path, out_dir: Path, tmp_path: Path
) -> None:
    wav = tmp_path / "a.wav"
    png = tmp_path / "i.png"
    _write_wav(wav)
    _write_png(png)
    asm = VideoAssembler()
    out = asm.assemble_video(str(wav), [str(png)], {"topic": "unit_test"})
    assert isinstance(out, str)
    assert out.endswith(".mp4")


def test_assemble_video_creates_file(
    log_root: Path, out_dir: Path, tmp_path: Path
) -> None:
    wav = tmp_path / "a.wav"
    png1 = tmp_path / "i1.png"
    png2 = tmp_path / "i2.png"
    _write_wav(wav, 0.6)
    _write_png(png1)
    _write_png(png2)
    asm = VideoAssembler()
    out = asm.assemble_video(str(wav), [str(png1), str(png2)], {})
    p = Path(out)
    assert p.is_file()
    assert p.stat().st_size > 500


def test_add_transitions(log_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from moviepy import ImageClip, vfx

    png = tmp_path / "t.png"
    _write_png(png)
    _size = (1920, 1080)
    clips = [
        ImageClip(str(png))
        .with_duration(0.5)
        .with_fps(30)
        .with_effects([vfx.Resize(_size)]),
        ImageClip(str(png))
        .with_duration(0.5)
        .with_fps(30)
        .with_effects([vfx.Resize(_size)]),
    ]
    monkeypatch.setattr(va_mod.rnd, "random", lambda: 0.05)
    monkeypatch.setattr(va_mod.rnd, "uniform", lambda _a, _b: 0.35)
    asm = VideoAssembler()
    out = asm.add_transitions(clips, random=True)
    assert len(out) == 2
    for c in out:
        c.close()


def test_apply_subtitles(log_root: Path, out_dir: Path, tmp_path: Path) -> None:
    if not shutil.which("ffmpeg"):
        pytest.skip("ffmpeg not available")

    wav = tmp_path / "a.wav"
    png = tmp_path / "i.png"
    _write_wav(wav, 0.5)
    _write_png(png)
    asm = VideoAssembler()
    mp4 = asm.assemble_video(str(wav), [str(png)], {})
    out = asm.apply_subtitles(mp4, "First line. Second line.")
    assert Path(out).is_file()
    assert out.endswith("_subtitled.mp4")


def test_verify_final_quality(log_root: Path, out_dir: Path, tmp_path: Path) -> None:
    wav = tmp_path / "a.wav"
    png = tmp_path / "i.png"
    _write_wav(wav, 0.45)
    _write_png(png)
    asm = VideoAssembler()
    mp4 = asm.assemble_video(str(wav), [str(png)], {})
    assert asm.verify_final_quality(mp4) is True
    assert asm.verify_final_quality(str(tmp_path / "missing.mp4")) is False


def test_error_handling_missing_files(log_root: Path, tmp_path: Path) -> None:
    asm = VideoAssembler()
    with pytest.raises(ValidationError):
        asm.assemble_video(str(tmp_path / "nope.wav"), [str(tmp_path / "x.png")], {})
    wav = tmp_path / "ok.wav"
    _write_wav(wav)
    with pytest.raises(ValidationError):
        asm.assemble_video(str(wav), [], {})


def test_logger_api_and_video_logs(tmp_path: Path) -> None:
    log = Logger("pytest_logger", str(tmp_path / "logs"))
    log.log_info("hello", k=1)
    log.log_api_call("openai", "chat", 0.001, 0.5)
    log.log_video_generation("topic_a", "ok", 12.3)
    log.log_performance("frame_timing", ms=16.2)
    day = log._daily_path.name
    assert (tmp_path / "logs" / "api_logs" / day).is_file()
    assert (tmp_path / "logs" / "performance_logs" / day).read_text(encoding="utf-8")


def test_performance_monitor_summary(tmp_path: Path) -> None:
    mon = PerformanceMonitor(tmp_path / "logs")
    mon.track_api_cost("x", 0.01)
    mon.track_duration("op", 2.0)
    mon.record_video_completed()
    mon.record_error()
    s = mon.get_daily_summary()
    assert s["total_cost"] >= 0.01
    assert s["total_videos"] == 1
    assert s["errors"] == 1
    assert s["avg_duration"] == 2.0
