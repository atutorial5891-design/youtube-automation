"""Small validation helpers used by setup-time modules."""

from pathlib import Path

from src.utils.exceptions import ValidationError


def require_file(path: str | Path, label: str) -> Path:
    resolved = Path(path)
    if not resolved.exists():
        raise ValidationError(f"{label} not found: {resolved}")
    return resolved


def require_range(name: str, value: int | float, minimum: int | float) -> None:
    if value < minimum:
        raise ValidationError(f"{name} must be >= {minimum}, got {value}")


def require_non_empty(name: str, value: str | None) -> str:
    if not value or not value.strip():
        raise ValidationError(f"{name} must not be empty")
    return value.strip()
