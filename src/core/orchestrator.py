"""Main workflow coordinator for the video generation pipeline (Stage 2+)."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from src.core.config_loader import ConfigLoader
from src.core.logger import build_logger
from src.utils.constants import PROJECT_ROOT


def _resolve_config_directory(config_path: str) -> Path:
    """Resolve ``config_path`` to a directory containing JSON configs.

    If ``config_path`` points to a ``.json`` file, its parent directory is used.

    Args:
        config_path: Path to the configuration directory or to ``settings.json``.

    Returns:
        Absolute path to the configuration directory.
    """
    raw = Path(config_path).expanduser()
    candidate = raw if raw.is_absolute() else (PROJECT_ROOT / raw).resolve()
    if candidate.is_file() and candidate.suffix.lower() == ".json":
        return candidate.parent
    return candidate


class VideoProductionOrchestrator:
    """Coordinate topic, script, verification, tone, TTS, images, and assembly.

    Client integrations (DeepSeek, ChatGPT, agent verifier, tone manager, TTS,
    image generator, video assembler) are stored as placeholders until their
    respective stages are wired in. The pipeline still runs end-to-end using
    configuration-driven placeholders so tests and smoke runs can validate
    flow, logging, and error handling.
    """

    def __init__(self, config_path: str) -> None:
        """Load configuration, configure logging, and register client placeholders.

        Args:
            config_path: Path to the ``config`` directory or to ``settings.json``
                under that directory. Relative paths are resolved from the
                project root.
        """
        self._config_dir = _resolve_config_directory(config_path)
        self.config = ConfigLoader(str(self._config_dir))

        self._logger = build_logger("youtube_automation.video_production")
        self._apply_log_level_from_settings()

        # Placeholders for future integrations (no network I/O in Stage 2).
        self.deepseek_client: Any = None
        self.chatgpt_client: Any = None
        self.agent_verifier: Any = None
        self.tone_manager: Any = None
        self.tts_client: Any = None
        self.image_generator: Any = None
        self.video_assembler: Any = None

        self._logger.info(
            "VideoProductionOrchestrator initialized; config_dir=%s",
            self._config_dir,
        )
        self._logger.debug(
            "Placeholder clients registered: DeepSeek, ChatGPT, agent verifier, "
            "tone manager, TTS, image generator, video assembler."
        )

        self._last_run_state: dict[str, Any] = {}

    def _apply_log_level_from_settings(self) -> None:
        """Set logger and handler levels from ``settings.json``."""
        level_name = str(
            self.config.get_setting("orchestrator.log_level", "INFO")
        ).upper()
        level = getattr(logging, level_name, logging.INFO)
        if self.config.get_setting("orchestrator.verbose", False):
            level = logging.DEBUG

        self._logger.setLevel(level)
        for handler in self._logger.handlers:
            handler.setLevel(level)

    def _timestamp_iso(self) -> str:
        """UTC ISO-8601 timestamp string for outputs and logs."""
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _base_result(self) -> dict[str, Any]:
        """Build a result dictionary with all required keys and error slots."""
        return {
            "success": False,
            "video_path": "",
            "script": "",
            "topic": "",
            "tone_used": "",
            "agent_verification_passed": False,
            "timestamp": self._timestamp_iso(),
            "duration_seconds": 0.0,
            "error": None,
            "failed_step": None,
        }

    def _video_output_dir(self) -> Path:
        """Directory for rendered videos from settings (created if missing)."""
        rel = str(
            self.config.get_setting(
                "orchestrator.video_output_relative",
                "data/videos",
            )
        )
        out = (PROJECT_ROOT / rel).resolve()
        out.mkdir(parents=True, exist_ok=True)
        return out

    def _finalize_result(
        self,
        result: dict[str, Any],
        start_perf: float,
        *,
        success: bool,
    ) -> dict[str, Any]:
        """Attach elapsed duration and success flag."""
        result["duration_seconds"] = round(time.perf_counter() - start_perf, 4)
        result["success"] = success
        result["timestamp"] = self._timestamp_iso()
        self._last_run_state = dict(result)
        return result

    def _run_step(
        self,
        step_name: str,
        result: dict[str, Any],
        func: Callable[[dict[str, Any]], None],
        start_perf: float,
    ) -> bool:
        """Execute one pipeline step with logging and error capture.

        Args:
            step_name: Logical step identifier for logs and ``failed_step``.
            result: Mutable result dictionary updated by ``func``.
            func: Callable that mutates ``result`` on success.
            start_perf: :func:`time.perf_counter` value at pipeline start.

        Returns:
            ``True`` if the step completed, ``False`` if an exception was caught.
        """
        self._logger.info("Pipeline step started: %s", step_name)
        try:
            func(result)
        except Exception as exc:  # noqa: BLE001 — orchestrator must not crash
            self._logger.exception("Pipeline step failed: %s", step_name)
            result["error"] = str(exc)
            result["failed_step"] = step_name
            self._finalize_result(result, start_perf, success=False)
            return False

        self._logger.info("Pipeline step completed: %s", step_name)
        return True

    def generate_video(self, topic: str | None = None, category: str = "general") -> dict[str, Any]:
        """Run the full video production workflow for one topic.

        Stages (in order): topic generation, script generation, agent
        verification, tone variation, TTS, images, video assembly. Real API
        calls are not performed yet; values are driven from configuration and
        placeholders.

        Args:
            topic: Optional explicit topic. When omitted, the configured default
                topic is used after a placeholder topic-generation step.
            category: Content category passed through the placeholder topic step.

        Returns:
            Standardized metadata dictionary. On failure, ``success`` is
            ``False`` and ``error`` / ``failed_step`` describe the first fault.
        """
        start = time.perf_counter()
        result = self._base_result()
        self._logger.info(
            "generate_video started category=%s topic_supplied=%s",
            category,
            topic is not None,
        )

        try:

            def step_topic(res: dict[str, Any]) -> None:
                if topic:
                    res["topic"] = topic
                else:
                    default_topic = self.config.get_setting(
                        "orchestrator.default_topic",
                        None,
                    )
                    if not default_topic or not isinstance(default_topic, str):
                        raise ValueError(
                            "No topic provided and settings key "
                            "'orchestrator.default_topic' is missing or not a string. "
                            "Set orchestrator.default_topic in config/settings.json "
                            "or pass topic= to generate_video()."
                        )
                    res["topic"] = str(default_topic)
                self._logger.debug("Topic resolved: %s", res["topic"])

            if not self._run_step("topic_generation", result, step_topic, start):
                return result

            def step_script(res: dict[str, Any]) -> None:
                template = self.config.get_setting(
                    "orchestrator.placeholder_script_template",
                    None,
                )
                if not template or not isinstance(template, str):
                    raise ValueError(
                        "settings key 'orchestrator.placeholder_script_template' "
                        "must be a non-empty string in config/settings.json."
                    )
                res["script"] = template.format(
                    topic=res["topic"],
                    category=category,
                )

            if not self._run_step("script_generation", result, step_script, start):
                return result

            def step_agent(res: dict[str, Any]) -> None:
                # Placeholder: real AgentVerifier integration in a later stage.
                _ = self.agent_verifier
                res["agent_verification_passed"] = bool(
                    self.config.get_setting(
                        "orchestrator.placeholder_agent_pass",
                        True,
                    )
                )

            if not self._run_step("agent_verification", result, step_agent, start):
                return result

            def step_tone(res: dict[str, Any]) -> None:
                _ = self.tone_manager
                tone = self.config.get_setting(
                    "orchestrator.placeholder_tone",
                    "general",
                )
                if not isinstance(tone, str):
                    raise ValueError(
                        "settings key 'orchestrator.placeholder_tone' must be a string."
                    )
                res["tone_used"] = tone

            if not self._run_step("tone_variation", result, step_tone, start):
                return result

            def step_tts(res: dict[str, Any]) -> None:
                _ = self.tts_client
                self._logger.debug(
                    "TTS placeholder (topic_len=%s script_len=%s)",
                    len(res.get("topic", "")),
                    len(res.get("script", "")),
                )

            if not self._run_step("tts", result, step_tts, start):
                return result

            def step_images(res: dict[str, Any]) -> None:
                _ = self.image_generator
                self._logger.debug("Image generation placeholder completed.")

            if not self._run_step("images", result, step_images, start):
                return result

            def step_assembly(res: dict[str, Any]) -> None:
                _ = self.video_assembler
                basename = str(
                    self.config.get_setting(
                        "orchestrator.placeholder_video_basename",
                        "stage2_placeholder.mp4",
                    )
                )
                out_path = self._video_output_dir() / basename
                out_path.parent.mkdir(parents=True, exist_ok=True)
                # Empty placeholder file until real FFmpeg/MoviePy assembly exists.
                out_path.write_bytes(b"")
                res["video_path"] = str(out_path)

            if not self._run_step("video_assembly", result, step_assembly, start):
                return result

        except Exception as exc:  # noqa: BLE001
            self._logger.exception("generate_video aborted with an unexpected error")
            result["error"] = str(exc)
            result["failed_step"] = result.get("failed_step") or "unknown"
            return self._finalize_result(result, start, success=False)

        self._logger.info("generate_video finished successfully")
        return self._finalize_result(result, start, success=True)

    def run_pipeline(self) -> dict[str, Any]:
        """Run the pipeline using configured defaults (for tests and smoke runs).

        Returns:
            Same structure as :meth:`generate_video`.
        """
        default_category = self.config.get_setting(
            "orchestrator.default_category",
            "general",
        )
        if not isinstance(default_category, str):
            self._logger.error(
                "orchestrator.default_category must be a string; falling back to "
                "'general'."
            )
            default_category = "general"

        self._logger.info("run_pipeline invoked with default topic/category from settings")
        return self.generate_video(topic=None, category=default_category)


@dataclass
class PipelineState:
    """Lightweight state object used by the Stage 1 scaffold orchestrator."""

    stage: str = "stage_1"
    topic: str | None = None
    status: str = "initialized"
    metadata: dict[str, Any] = field(default_factory=dict)


class Orchestrator:
    """Coordinates the Stage 1 scaffold and records high-level state transitions."""

    def __init__(self, config_loader: ConfigLoader | None = None) -> None:
        self.config_loader = config_loader or ConfigLoader()
        self.logger = build_logger("youtube_automation.orchestrator")
        self.settings = self.config_loader.load_settings()

    def bootstrap(self) -> PipelineState:
        """Return initial pipeline state for Stage 1 helpers."""
        self.logger.info("Stage 1 scaffold loaded.")
        return PipelineState(metadata={"app": self.settings.get("app", {})})

    def summarize_next_steps(self) -> list[str]:
        """Human-readable reminders shown by ``scripts/run_stage_1.py``."""
        return [
            "Update .env with real API credentials.",
            "Run python scripts/test_apis.py after setup.",
            "Follow docs/STAGE_1_EXECUTION_PLAN.md before Stage 2 coding.",
        ]
