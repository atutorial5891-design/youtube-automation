"""Load JSON configuration from the project's config directory."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.utils.constants import CONFIG_DIR
from src.utils.exceptions import ConfigurationError


class ConfigLoader:
    """Thin config loader used during the Stage 1 scaffold."""

    def __init__(self, config_dir: Path | None = None) -> None:
        self.config_dir = config_dir or CONFIG_DIR

    def load_json(self, filename: str) -> dict[str, Any]:
        path = self.config_dir / filename
        if not path.exists():
            raise ConfigurationError(f"Config file not found: {path}")
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def load_settings(self) -> dict[str, Any]:
        return self.load_json("settings.json")

    def load_tones(self) -> dict[str, Any]:
        return self.load_json("tone_library.json")
