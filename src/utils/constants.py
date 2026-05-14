"""Application constants used across the scaffold."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"

SUPPORTED_PRIMARY_MODELS = ("openai", "claude")
DEFAULT_TONE_VARIATIONS = 3
DEFAULT_MAX_RETRIES = 3
