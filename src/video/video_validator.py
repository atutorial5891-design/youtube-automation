"""Basic validation for assembled video inputs."""

from __future__ import annotations

from pathlib import Path


class VideoValidator:
    def validate_assets(self, asset_paths: list[Path]) -> bool:
        return all(path.exists() for path in asset_paths)
