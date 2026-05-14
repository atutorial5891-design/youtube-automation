"""Google TTS configuration helper."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class VoiceSettings:
    language_code: str = "en-US"
    voice_name: str = "en-US-Neural2-C"
    speaking_rate: float = 1.0


class GoogleTTSClient:
    def __init__(self, credentials_path: str | None = None) -> None:
        self.credentials_path = credentials_path or os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS",
            "config/google-credentials.json",
        )

    def credentials_ready(self) -> bool:
        return Path(self.credentials_path).exists()

    def default_voice(self) -> VoiceSettings:
        return VoiceSettings()
