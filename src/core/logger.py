"""Central logging setup for scripts and future pipeline runs."""

from __future__ import annotations

import logging
from pathlib import Path

from src.utils.constants import LOG_DIR


def build_logger(name: str = "youtube_automation", log_file: str = "daily_logs/app.log") -> logging.Logger:
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
