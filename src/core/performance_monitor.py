"""Track API costs, durations, and daily aggregates for the pipeline."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.utils.constants import PROJECT_ROOT


def _today_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


class PerformanceMonitor:
    """In-memory metrics with optional append-only performance log lines."""

    def __init__(self, logs_root: str | Path = "logs") -> None:
        """Initialize counters and performance log path for the current UTC day."""
        raw = Path(logs_root).expanduser()
        self._logs_root = raw if raw.is_absolute() else (PROJECT_ROOT / raw).resolve()
        self._perf_path = self._logs_root / "performance_logs" / f"{_today_stamp()}.log"
        self._perf_path.parent.mkdir(parents=True, exist_ok=True)
        self._total_cost: float = 0.0
        self._durations: list[float] = []
        self._total_videos: int = 0
        self._errors: int = 0

    def track_api_cost(self, api_name: str, cost: float) -> None:
        """Accumulate API cost and append a line to ``logs/api_logs/[date].log``."""
        self._total_cost += float(cost)
        api_path = self._logs_root / "api_logs" / f"{_today_stamp()}.log"
        api_path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(
            {
                "type": "api_cost",
                "api": api_name,
                "cost": cost,
                "running_total": self._total_cost,
                "ts": datetime.now(timezone.utc).isoformat(),
            }
        )
        with api_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")

    def track_duration(self, operation: str, duration: float) -> None:
        """Record operation duration and append to performance log."""
        self._durations.append(float(duration))
        line = json.dumps(
            {
                "operation": operation,
                "duration_sec": duration,
                "ts": datetime.now(timezone.utc).isoformat(),
            }
        )
        with self._perf_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")

    def record_video_completed(self) -> None:
        """Increment successful video count (call when a render finishes)."""
        self._total_videos += 1

    def record_error(self) -> None:
        """Increment error counter for the daily summary."""
        self._errors += 1

    def get_daily_summary(self) -> dict[str, Any]:
        """Return aggregate stats for the current monitor session."""
        avg_dur = sum(self._durations) / len(self._durations) if self._durations else 0.0
        return {
            "total_cost": round(self._total_cost, 6),
            "total_videos": self._total_videos,
            "avg_duration": round(avg_dur, 4),
            "errors": self._errors,
        }
