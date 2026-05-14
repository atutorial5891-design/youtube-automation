"""YouTube upload configuration helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class UploadMetadata:
    title: str
    description: str
    tags: list[str] = field(default_factory=list)
    privacy_status: str = "private"


class YouTubeClient:
    def __init__(self, credentials_path: str | None = None) -> None:
        self.credentials_path = credentials_path or os.getenv(
            "YOUTUBE_CREDENTIALS_PATH",
            "config/youtube-credentials.json",
        )

    def credentials_ready(self) -> bool:
        return Path(self.credentials_path).exists()

    def build_metadata(self, title: str, description: str, tags: list[str] | None = None) -> UploadMetadata:
        return UploadMetadata(title=title, description=description, tags=tags or [])
