"""Main workflow coordinator for future stage implementation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.core.config_loader import ConfigLoader
from src.core.logger import build_logger


@dataclass
class PipelineState:
    stage: str = "stage_1"
    topic: str | None = None
    status: str = "initialized"
    metadata: dict[str, Any] = field(default_factory=dict)


class Orchestrator:
    """Coordinates the pipeline and records high-level state transitions."""

    def __init__(self, config_loader: ConfigLoader | None = None) -> None:
        self.config_loader = config_loader or ConfigLoader()
        self.logger = build_logger("youtube_automation.orchestrator")
        self.settings = self.config_loader.load_settings()

    def bootstrap(self) -> PipelineState:
        self.logger.info("Stage 1 scaffold loaded.")
        return PipelineState(metadata={"app": self.settings.get("app", {})})

    def summarize_next_steps(self) -> list[str]:
        return [
            "Update .env with real API credentials.",
            "Run python scripts/test_apis.py after setup.",
            "Follow docs/STAGE_1_EXECUTION_PLAN.md before Stage 2 coding.",
        ]
