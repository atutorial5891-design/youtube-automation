"""Assemble narration + image sequences into MP4 with optional subtitles."""

from __future__ import annotations

import logging
import random as rnd
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from moviepy import (
    AudioFileClip,
    ColorClip,
    CompositeVideoClip,
    ImageClip,
    VideoFileClip,
    concatenate_videoclips,
    vfx,
)

from src.core.logger import Logger
from src.utils.constants import PROJECT_ROOT
from src.utils.exceptions import ExternalServiceError, ValidationError

logger = logging.getLogger(__name__)

DEFAULT_SIZE = (1920, 1080)
DEFAULT_FPS = 30
OUTPUT_DIR = PROJECT_ROOT / "data" / "generated_videos"


class VideoAssembler:
    """Assemble final video from audio, images, and metadata using MoviePy."""

    def __init__(self) -> None:
        """Initialize MoviePy-oriented defaults (1080p, 30 fps) and structured logging."""
        self._size = DEFAULT_SIZE
        self._fps = DEFAULT_FPS
        self._file_logger = Logger("VideoAssembler")
        self._file_logger.log_info(
            "VideoAssembler initialized",
            width=self._size[0],
            height=self._size[1],
            fps=self._fps,
        )
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    def assemble_video(self, audio_path: str, images: list[str], metadata: dict[str, Any]) -> str:
        """Build an MP4 from ``audio_path`` and image paths; write under ``data/generated_videos/``.

        Args:
            audio_path: Path to a readable audio file (e.g. WAV).
            images: Non-empty list of image paths (PNG/JPG).
            metadata: Optional dict for logging (e.g. ``topic``).

        Returns:
            Absolute path to ``[timestamp].mp4`` under ``data/generated_videos/``.

        Raises:
            ValidationError: Missing inputs or invalid paths.
            ExternalServiceError: MoviePy/FFmpeg failures after fallbacks.
        """
        topic = str(metadata.get("topic", "")) if metadata else ""
        self._file_logger.log_info("assemble_video start", topic=topic, images=len(images))

        audio_p = self._require_file(audio_path, "audio_path")
        if not images:
            raise ValidationError("assemble_video requires a non-empty images list.")
        image_paths = [self._require_file(p, "images") for p in images]

        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        out_path = OUTPUT_DIR / f"{stamp}.mp4"
        t_assemble0 = time.perf_counter()

        audio_clip: AudioFileClip | None = None
        video: Any = None
        clips: list[Any] = []
        try:
            audio_clip = AudioFileClip(str(audio_p))
            total_dur = float(audio_clip.duration or 0.0)
            if total_dur <= 0:
                raise ValidationError(f"Audio duration invalid: {audio_p}")

            n = len(image_paths)
            per = max(total_dur / n, 0.05)

            for img in image_paths:
                clip = (
                    ImageClip(str(img))
                    .with_duration(per)
                    .with_fps(self._fps)
                    .with_effects([vfx.Resize(self._size)])
                )
                clips.append(clip)

            try:
                clips = self.add_transitions(clips, random=True)
            except Exception as exc:
                logger.warning("add_transitions failed, using raw clips: %s", exc)
                self._file_logger.log_warning(f"add_transitions fallback: {exc}")

            video = concatenate_videoclips(clips, method="compose")
            video = video.with_effects([vfx.Resize(self._size)])
            video = video.with_audio(audio_clip)

            video.write_videofile(
                str(out_path),
                fps=self._fps,
                codec="libx264",
                audio_codec="aac",
                logger=None,
                preset="medium",
            )

        except (ValidationError, ExternalServiceError):
            raise
        except Exception as exc:
            self._file_logger.log_error("assemble_video encoding failure", exception=exc)
            raise ExternalServiceError(f"Video assembly failed: {exc}") from exc
        finally:
            if video is not None:
                try:
                    video.close()
                except Exception:
                    pass
            if audio_clip is not None:
                try:
                    audio_clip.close()
                except Exception:
                    pass
            for c in clips:
                try:
                    c.close()
                except Exception:
                    pass

        self._file_logger.log_video_generation(
            topic or "unknown", "assembled", time.perf_counter() - t_assemble0
        )
        self._file_logger.log_info("assemble_video done", output=str(out_path))
        return str(out_path.resolve())

    def add_transitions(self, clips: list[Any], random: bool = True) -> list[Any]:
        """Apply weighted random entry transitions (fade / zoom / wipe).

        Weights: fade 60%, zoom 20%, wipe 20%. Transition duration is random in
        ``[0.3, 1.0]`` s when ``random`` is True, else fixed at 0.5 s.

        Args:
            clips: MoviePy video clips (each should already have duration and fps).
            random: If True, randomize effect type and duration; otherwise fade only.

        Returns:
            New list of clips with effects applied (may be composite clips).

        Raises:
            ValidationError: Empty ``clips``.
        """
        if not clips:
            raise ValidationError("add_transitions requires at least one clip.")

        out: list[Any] = []
        w, h = self._size

        for idx, clip in enumerate(clips):
            dur = rnd.uniform(0.3, 1.0) if random else 0.5
            dur = min(dur, max((clip.duration or 1.0) * 0.9, 0.15))

            if not random:
                choice = "fade"
            else:
                r = rnd.random()
                if r < 0.6:
                    choice = "fade"
                elif r < 0.8:
                    choice = "zoom"
                else:
                    choice = "wipe"

            try:
                if choice == "fade":
                    out.append(clip.with_effects([vfx.FadeIn(dur)]))
                elif choice == "zoom":
                    trans = float(dur)

                    def scale_fn(t: float, tr: float = trans) -> float:
                        if t >= tr:
                            return 1.0
                        return 1.0 + 0.12 * (1.0 - t / max(tr, 1e-6))

                    out.append(clip.with_effects([vfx.Resize(scale_fn)]))
                else:
                    side = rnd.choice(("left", "right", "top", "bottom"))
                    bg = ColorClip(size=(w, h), color=(0, 0, 0), duration=clip.duration).with_fps(
                        self._fps
                    )
                    sized = clip.with_effects([vfx.Resize((w, h))])
                    fg = sized.with_effects([vfx.SlideIn(dur, side)])
                    comp = CompositeVideoClip([bg, fg], size=(w, h)).with_duration(
                        clip.duration
                    ).with_fps(self._fps)
                    out.append(comp)
            except Exception as exc:
                logger.warning("Transition %s failed for clip %s: %s", choice, idx, exc)
                self._file_logger.log_warning(f"transition fallback fade clip={idx}: {exc}")
                out.append(clip.with_effects([vfx.FadeIn(min(dur, 0.5))]))

        self._file_logger.log_info("add_transitions applied", count=len(out))
        return out

    def apply_subtitles(self, video_path: str, script: str) -> str:
        """Write a simple SRT from ``script`` and burn subtitles into a new MP4.

        Args:
            video_path: Source MP4 path.
            script: Full narration text; split into timed cues from video duration.

        Returns:
            Path to a new ``*_subtitled.mp4`` next to the source file.

        Raises:
            ValidationError: Missing ffmpeg/ffprobe, empty script, or invalid video.
            ExternalServiceError: Subtitle burn-in failed.
        """
        src = self._require_file(video_path, "video_path")
        text = (script or "").strip()
        if not text:
            raise ValidationError("apply_subtitles requires non-empty script.")

        ffmpeg_bin = shutil.which("ffmpeg")
        if not ffmpeg_bin:
            raise ValidationError("ffmpeg not found on PATH; cannot burn subtitles.")

        self._file_logger.log_info("apply_subtitles start", video=str(src))

        try:
            probe = VideoFileClip(str(src))
            duration = float(probe.duration or 0.0)
            probe.close()
        except Exception as exc:
            raise ValidationError(f"Cannot read video duration: {exc}") from exc

        if duration <= 0:
            raise ValidationError("Video has zero duration.")

        srt_body = self._build_srt(text, duration)
        srt_path = src.with_name(f"{src.stem}_subs.srt")
        srt_path.write_text(srt_body, encoding="utf-8")

        out_path = src.with_name(f"{src.stem}_subtitled.mp4")
        raw_sub = str(srt_path.resolve()).replace("\\", "/")
        subs_esc = raw_sub.replace(":", r"\:").replace("'", r"\'")

        cmd = [
            ffmpeg_bin,
            "-y",
            "-i",
            str(src),
            "-vf",
            f"subtitles='{subs_esc}'",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-c:a",
            "copy",
            str(out_path),
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as exc:
            self._file_logger.log_error("ffmpeg subtitles failed", exception=exc)
            raise ExternalServiceError(exc.stderr or str(exc)) from exc

        self._file_logger.log_info("apply_subtitles done", output=str(out_path))
        return str(out_path.resolve())

    def verify_final_quality(self, video_path: str) -> bool:
        """Check file presence, duration, resolution, and approximate bitrate.

        Args:
            video_path: Path to rendered MP4.

        Returns:
            True if checks pass, False otherwise.
        """
        path = Path(video_path).expanduser()
        if not path.is_file():
            self._file_logger.log_warning("verify_final_quality missing file", path=str(path))
            return False

        clip: VideoFileClip | None = None
        try:
            clip = VideoFileClip(str(path))
            duration = float(clip.duration or 0.0)
            w, h = clip.size
        except Exception as exc:
            logger.warning("verify_final_quality open failed: %s", exc)
            return False
        finally:
            if clip is not None:
                clip.close()

        if duration < 0.2:
            return False
        if w < 640 or h < 360:
            return False

        br_ok = self._bitrate_ok(path, duration)
        self._file_logger.log_info(
            "verify_final_quality",
            duration=duration,
            width=w,
            height=h,
            bitrate_ok=br_ok,
        )
        return br_ok

    @staticmethod
    def _require_file(path_str: str, field: str) -> Path:
        p = Path(path_str).expanduser()
        if not p.is_file():
            raise ValidationError(f"{field}: file not found: {path_str}")
        return p.resolve()

    @staticmethod
    def _build_srt(script: str, total_duration: float) -> str:
        parts = [s.strip() for s in re.split(r"(?<=[.!?])\s+", script) if s.strip()]
        if not parts:
            parts = [script[:200]]
        n = len(parts)
        chunk = total_duration / n
        blocks: list[str] = []
        for i, line in enumerate(parts):
            t0 = i * chunk
            t1 = (i + 1) * chunk if i < n - 1 else total_duration

            def fmt(t: float) -> str:
                h = int(t // 3600)
                m = int((t % 3600) // 60)
                s = t % 60
                return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")

            blocks.append(f"{i + 1}\n{fmt(t0)} --> {fmt(t1)}\n{line}\n")
        return "\n".join(blocks)

    @staticmethod
    def _bitrate_ok(path: Path, duration: float) -> bool:
        ffprobe = shutil.which("ffprobe")
        if not ffprobe or duration <= 0:
            return path.stat().st_size > 1024
        try:
            out = subprocess.run(
                [
                    ffprobe,
                    "-v",
                    "error",
                    "-show_entries",
                    "format=bit_rate",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    str(path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            rate = int((out.stdout or "0").strip() or 0)
            if rate <= 0:
                return path.stat().st_size / duration > 5_000
            return rate >= 10_000
        except Exception:
            return path.stat().st_size / duration > 5_000
