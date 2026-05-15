"""Application logging: daily, error, API, and performance log files."""

from __future__ import annotations

import json
import logging
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.utils.constants import LOG_DIR, PROJECT_ROOT


def _today_stamp() -> str:
    """UTC date string used for log filenames."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


class Logger:
    """Structured application logging with separate files per category."""

    def __init__(self, name: str, log_dir: str = "logs") -> None:
        """Configure handlers under ``log_dir`` for daily, error, API, and performance logs.

        Args:
            name: Logical logger name (appears in log lines).
            log_dir: Directory relative to project root, or absolute path.
        """
        self._name = name
        raw = Path(log_dir).expanduser()
        self._root = raw if raw.is_absolute() else (PROJECT_ROOT / raw).resolve()
        for sub in ("daily_logs", "error_logs", "api_logs", "performance_logs"):
            (self._root / sub).mkdir(parents=True, exist_ok=True)

        self._logger = logging.getLogger(f"youtube_automation.{name}")
        self._logger.setLevel(logging.DEBUG)
        self._logger.propagate = False
        self._logger.handlers.clear()

        fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        date_str = _today_stamp()

        daily_path = self._root / "daily_logs" / f"{date_str}.log"
        daily_h = logging.FileHandler(daily_path, encoding="utf-8")
        daily_h.setLevel(logging.INFO)
        daily_h.setFormatter(fmt)
        self._logger.addHandler(daily_h)

        err_path = self._root / "error_logs" / f"{date_str}.log"
        err_h = logging.FileHandler(err_path, encoding="utf-8")
        err_h.setLevel(logging.ERROR)
        err_h.setFormatter(fmt)
        self._logger.addHandler(err_h)

        stream = logging.StreamHandler()
        stream.setLevel(logging.INFO)
        stream.setFormatter(fmt)
        self._logger.addHandler(stream)

        self._daily_path = daily_path
        self._api_path = self._root / "api_logs" / f"{date_str}.log"
        self._perf_path = self._root / "performance_logs" / f"{date_str}.log"

    def log_info(self, message: str, **kwargs: Any) -> None:
        """Log an informational message."""
        if kwargs:
            message = f"{message} | {json.dumps(kwargs, default=str)}"
        self._logger.info(message)

    def log_error(self, message: str, exception: Exception | None = None) -> None:
        """Log an error; optional exception adds its traceback to the error log."""
        if exception is not None:
            tb = "".join(
                traceback.format_exception(
                    type(exception), exception, exception.__traceback__
                )
            )
            message = f"{message}\n{tb}"
        self._logger.error(message)

    def log_debug(self, message: str) -> None:
        """Log a debug message."""
        self._logger.debug(message)

    def log_warning(self, message: str, **kwargs: Any) -> None:
        """Log a warning."""
        if kwargs:
            message = f"{message} | {json.dumps(kwargs, default=str)}"
        self._logger.warning(message)

    def log_performance(self, message: str, **kwargs: Any) -> None:
        """Append a structured line to ``performance_logs/[date].log``."""
        record = {
            "message": message,
            "ts": datetime.now(timezone.utc).isoformat(),
            **kwargs,
        }
        line = json.dumps(record, default=str)
        self._perf_path.parent.mkdir(parents=True, exist_ok=True)
        with self._perf_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
        self._logger.debug("performance %s", line)

    def log_api_call(self, api_name: str, method: str, cost: float, duration: float) -> None:
        """Append a structured API call record to ``logs/api_logs/[date].log``."""
        line = json.dumps(
            {
                "api": api_name,
                "method": method,
                "cost": cost,
                "duration_sec": duration,
                "ts": datetime.now(timezone.utc).isoformat(),
            }
        )
        self._api_path.parent.mkdir(parents=True, exist_ok=True)
        with self._api_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
        self._logger.info("api_call %s", line)

    def log_video_generation(self, topic: str, status: str, duration: float) -> None:
        """Append a video-generation event to ``logs/daily_logs/[date].log`` (structured)."""
        line = json.dumps(
            {
                "event": "video_generation",
                "topic": topic,
                "status": status,
                "duration_sec": duration,
                "ts": datetime.now(timezone.utc).isoformat(),
            }
        )
        with self._daily_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
        self._logger.info("video_generation %s", line)


def build_logger(
    name: str = "youtube_automation",
    log_file: str = "daily_logs/app.log",
) -> logging.Logger:
    """Return a stdlib :class:`logging.Logger` with stream + file handlers (orchestrator compat).

    Args:
        name: Logger name.
        log_file: Path relative to ``LOG_DIR`` for the file handler.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_path = LOG_DIR / log_file
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(file_path)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
