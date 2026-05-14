"""Render-plan scaffold for future MoviePy/FFmpeg assembly."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class RenderPlan:
    script_path: Path
    narration_path: Path
    image_paths: list[Path]
    output_path: Path


class VideoAssembler:
    def build_plan(
        self,
        script_path: Path,
        narration_path: Path,
        image_paths: list[Path],
        output_path: Path,
    ) -> RenderPlan:
        return RenderPlan(
            script_path=script_path,
            narration_path=narration_path,
            image_paths=image_paths,
            output_path=output_path,
        )
