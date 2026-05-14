"""Load and validate JSON configuration from the project's ``config/`` directory."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.utils.constants import PROJECT_ROOT
from src.utils.exceptions import ConfigurationError


class ConfigLoader:
    """Load required pipeline JSON files and expose typed accessors.

    On construction, ``settings.json``, ``agent_prompts.json``, and
    ``script_prompts.json`` are read and validated. Other JSON files (for
    example ``tone_library.json``) are loaded on demand via :meth:`load_json`.
    """

    def __init__(self, config_dir: str = "config") -> None:
        """Load core configuration files and validate JSON.

        Args:
            config_dir: Directory containing JSON config files. Relative paths
                are resolved from the project repository root.

        Raises:
            ConfigurationError: If a required file is missing or contains
                invalid JSON.
        """
        base = Path(config_dir).expanduser()
        self.config_dir = base if base.is_absolute() else (PROJECT_ROOT / base).resolve()
        if not self.config_dir.is_dir():
            raise ConfigurationError(
                f"Configuration directory does not exist or is not a directory: "
                f"{self.config_dir}"
            )

        self._settings = self._read_required_json("settings.json")
        self._agent_prompts = self._read_required_json("agent_prompts.json")
        self._script_prompts = self._read_required_json("script_prompts.json")

    def _read_required_json(self, filename: str) -> dict[str, Any]:
        """Read a JSON object from ``config_dir`` / ``filename``.

        Args:
            filename: File name inside the configuration directory.

        Returns:
            Parsed JSON object (Python ``dict``).

        Raises:
            ConfigurationError: If the file is missing or invalid JSON.
        """
        path = self.config_dir / filename
        if not path.is_file():
            raise ConfigurationError(
                f"Required configuration file is missing: {path}. "
                f"Create this file under {self.config_dir} or fix the config path."
            )
        try:
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except json.JSONDecodeError as exc:
            raise ConfigurationError(
                f"Invalid JSON in configuration file {path}: {exc.msg} at line "
                f"{exc.lineno} column {exc.colno}."
            ) from exc
        except OSError as exc:
            raise ConfigurationError(
                f"Could not read configuration file {path}: {exc}"
            ) from exc

        if not isinstance(payload, dict):
            raise ConfigurationError(
                f"Configuration file {path} must contain a JSON object at the top level, "
                f"not {type(payload).__name__}."
            )
        return payload

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Return a value from ``settings.json`` using dotted key paths.

        Args:
            key: Dotted path such as ``\"api.chatgpt.model\"`` or a single
                segment for a top-level key.
            default: Value returned when the path is missing or intermediate
                nodes are not objects.

        Returns:
            The resolved setting, or ``default`` when not found.
        """
        if not key:
            return default

        current: Any = self._settings
        for part in key.split("."):
            if not isinstance(current, dict) or part not in current:
                return default
            current = current[part]
        return current

    def get_agent_prompts(self) -> dict[str, Any]:
        """Return the parsed ``agent_prompts.json`` object.

        Returns:
            Agent prompt templates and system strings.
        """
        return self._agent_prompts

    def get_script_prompts(self) -> dict[str, Any]:
        """Return the parsed ``script_prompts.json`` object.

        Returns:
            Script-related prompt templates.
        """
        return self._script_prompts

    def load_json(self, filename: str) -> dict[str, Any]:
        """Load an arbitrary JSON object from the configuration directory.

        Args:
            filename: File name (for example ``\"tone_library.json\"``).

        Returns:
            Parsed JSON object.

        Raises:
            ConfigurationError: If the file is missing or invalid.
        """
        return self._read_required_json(filename)

    def load_settings(self) -> dict[str, Any]:
        """Return a shallow copy of all settings loaded at construction time.

        Returns:
            Settings dictionary (copy of the in-memory ``settings.json`` data).
        """
        return dict(self._settings)

    def load_tones(self) -> dict[str, Any]:
        """Load ``tone_library.json`` from the configuration directory.

        Returns:
            Parsed tone library object.

        Raises:
            ConfigurationError: If the file is missing or invalid.
        """
        return self._read_required_json("tone_library.json")
