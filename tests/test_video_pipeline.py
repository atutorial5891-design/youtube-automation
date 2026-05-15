from pathlib import Path

import pytest

from src.core.logger import Logger
from src.video import video_assembler as va_mod
from src.video.video_assembler import VideoAssembler


def test_video_assembler_has_assemble_api(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "logs"

    def _factory(name: str) -> Logger:
        return Logger(name, str(root))

    gen = tmp_path / "generated_videos"
    gen.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(va_mod, "Logger", _factory)
    monkeypatch.setattr(va_mod, "OUTPUT_DIR", gen)
    asm = VideoAssembler()
    assert hasattr(asm, "assemble_video")
    assert hasattr(asm, "verify_final_quality")
