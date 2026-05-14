"""Tone selection and variation planning."""

from __future__ import annotations

import random
from typing import Any

from src.core.config_loader import ConfigLoader


class ToneManager:
    def __init__(self, config_loader: ConfigLoader | None = None) -> None:
        self.config_loader = config_loader or ConfigLoader()
        self.tone_library = self.config_loader.load_tones()["profiles"]

    def pick_tone(self, content_type: str) -> dict[str, Any]:
        eligible = [
            profile
            for profile in self.tone_library
            if content_type in profile.get("use_when", [])
        ]
        pool = eligible or self.tone_library
        return random.choice(pool)

    def expected_variations(self, content_type: str) -> int:
        return int(self.pick_tone(content_type).get("variation_count", 2))
