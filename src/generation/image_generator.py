"""Ollama-backed image generation with local saves and prompt templates."""

from __future__ import annotations

import base64
import json
import logging
import random
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from src.utils.constants import PROJECT_ROOT
from src.utils.exceptions import ExternalServiceError, ValidationError

logger = logging.getLogger(__name__)

DEFAULT_IMAGE_PROMPTS = PROJECT_ROOT / "config" / "image_prompts.json"
DEFAULT_IMAGE_OUTPUT_DIR = PROJECT_ROOT / "data" / "generated_videos" / "images"


class ImageGenerator:
    """Generate images via Ollama HTTP API and persist PNGs under ``data/``."""

    def __init__(
        self,
        model: str = "sdxl",
        base_url: str = "http://localhost:11434",
        *,
        image_prompts_path: Path | str | None = None,
        output_dir: Path | str | None = None,
    ) -> None:
        """Configure model host, template source, and output directory.

        Args:
            model: Ollama model tag responsible for image generation.
            base_url: Ollama server root (no trailing slash required).
            image_prompts_path: Optional override for ``image_prompts.json``.
            output_dir: Optional override for PNG output directory.
        """
        self._model = (model or "sdxl").strip()
        self._base = base_url.rstrip("/")
        raw_prompts = Path(image_prompts_path or DEFAULT_IMAGE_PROMPTS).expanduser()
        self._prompts_path = (
            raw_prompts if raw_prompts.is_absolute() else (PROJECT_ROOT / raw_prompts).resolve()
        )
        raw_out = Path(output_dir or DEFAULT_IMAGE_OUTPUT_DIR).expanduser()
        self._output_dir = (
            raw_out if raw_out.is_absolute() else (PROJECT_ROOT / raw_out).resolve()
        )
        self._templates = self._load_templates()
        logger.info(
            "ImageGenerator init model=%s base_url=%s templates=%s",
            self._model,
            self._base,
            len(self._templates),
        )

    def _load_templates(self) -> list[str]:
        if not self._prompts_path.is_file():
            raise ExternalServiceError(
                f"image_prompts.json not found at {self._prompts_path}. "
                "Create the file or pass image_prompts_path=."
            )
        with self._prompts_path.open("r", encoding="utf-8") as handle:
            try:
                data = json.load(handle)
            except json.JSONDecodeError as exc:
                raise ExternalServiceError(
                    f"Invalid JSON in image prompts file {self._prompts_path}: {exc}"
                ) from exc
        templates = data.get("templates") if isinstance(data, dict) else None
        if not isinstance(templates, list) or not templates:
            raise ExternalServiceError(
                f"{self._prompts_path} must contain a non-empty 'templates' array."
            )
        return [str(t) for t in templates if str(t).strip()]

    def _ollama_tags_ok(self) -> bool:
        """Return True if the Ollama daemon responds to ``/api/tags``."""
        try:
            response = requests.get(f"{self._base}/api/tags", timeout=3)
            return response.ok
        except requests.RequestException as exc:
            logger.warning("Ollama health check failed: %s", exc)
            return False

    @staticmethod
    def _unique_filename(index: int) -> str:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        return f"{stamp}_{time.time_ns()}_{index}.png"

    def _write_placeholder(self, path: Path) -> None:
        """Write a simple solid PNG when remote generation is unavailable."""
        try:
            from PIL import Image
        except ImportError as exc:  # pragma: no cover - pillow is a project dependency
            raise ExternalServiceError("Pillow is required for placeholder images.") from exc

        path.parent.mkdir(parents=True, exist_ok=True)
        image = Image.new("RGB", (512, 512), color=(32, 36, 48))
        image.save(path, format="PNG")
        logger.warning("Wrote placeholder PNG at %s", path)

    def _persist_decoded_png(self, raw: bytes, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)

    def _decode_image_from_response(self, payload: dict[str, Any]) -> bytes | None:
        """Extract PNG/JPEG bytes from common Ollama / auxiliary JSON shapes."""
        for key in ("images", "image", "data"):
            value = payload.get(key)
            if isinstance(value, list) and value:
                value = value[0]
            if not isinstance(value, str):
                continue
            text = value.strip()
            if text.startswith("data:") and "," in text:
                text = text.split(",", 1)[1]
            try:
                return base64.b64decode(text, validate=False)
            except (ValueError, TypeError):
                continue
        return None

    def _request_generation(self, prompt: str, target: Path) -> bool:
        """Call Ollama ``/api/generate`` and write decoded image bytes if found."""
        url = f"{self._base}/api/generate"
        body = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
        }
        try:
            response = requests.post(url, json=body, timeout=120)
        except requests.RequestException as exc:
            logger.warning("Ollama POST failed: %s", exc)
            return False

        if not response.ok:
            err_body = response.content[:200]
            try:
                err_text = (response.text or "")[:200]
            except UnicodeDecodeError:
                err_text = repr(err_body)
            logger.warning("Ollama HTTP %s: %s", response.status_code, err_text or err_body)
            return False

        raw = response.content
        if raw.startswith(b"\x89PNG"):
            self._persist_decoded_png(raw, target)
            return True

        try:
            payload = response.json()
        except ValueError:
            logger.warning("Ollama response was not JSON and not raw PNG.")
            return False

        image_bytes = self._decode_image_from_response(payload)
        if image_bytes and image_bytes.startswith(b"\x89PNG"):
            self._persist_decoded_png(image_bytes, target)
            return True
        if isinstance(payload.get("response"), str):
            decoded = self._decode_image_from_response({"image": payload["response"]})
            if decoded and decoded.startswith(b"\x89PNG"):
                self._persist_decoded_png(decoded, target)
                return True
        return False

    def generate_image(self, prompt: str, num_images: int = 1) -> list[str]:
        """Generate ``num_images`` PNGs for ``prompt`` and return absolute paths.

        On model/network failure, writes **placeholder** PNGs so callers always
        receive usable paths.

        Args:
            prompt: Full image prompt text.
            num_images: How many files to create (incrementing filename suffix).

        Returns:
            List of absolute ``.png`` paths under ``data/generated_videos/images/``.

        Raises:
            ValidationError: If ``prompt`` is empty.
        """
        if not (prompt or "").strip():
            raise ValidationError("generate_image requires a non-empty prompt.")

        if num_images < 1:
            raise ValidationError("num_images must be >= 1.")

        base_out = self._output_dir
        base_out.mkdir(parents=True, exist_ok=True)

        ollama_ok = self._ollama_tags_ok()
        if not ollama_ok:
            logger.warning(
                "Ollama does not appear reachable at %s; using placeholders.",
                self._base,
            )

        paths: list[str] = []
        for i in range(num_images):
            filename = self._unique_filename(i + 1)
            target = base_out / filename
            ok = False
            if ollama_ok:
                ok = self._request_generation(prompt.strip(), target)
            if not ok or not target.is_file():
                self._write_placeholder(target)
            paths.append(str(target.resolve()))
            logger.info("generate_image saved path=%s ok=%s", target, ok)

        return paths

    def select_random_prompt(self, topic: str, count: int = 3) -> list[str]:
        """Build ``count`` varied prompts from ``image_prompts.json`` templates.

        Args:
            topic: Subject text substituted for ``{{subject}}``.
            count: Number of prompts (may repeat templates if count exceeds pool).

        Returns:
            List of prompt strings.

        Raises:
            ValidationError: If ``topic`` is empty or ``count`` < 1.
        """
        if not (topic or "").strip():
            raise ValidationError("select_random_prompt requires a non-empty topic.")
        if count < 1:
            raise ValidationError("count must be >= 1.")

        if not self._templates:
            raise ExternalServiceError("No image prompt templates are loaded.")

        pool = list(self._templates)
        random.shuffle(pool)
        picks: list[str] = []
        for idx in range(count):
            template = pool[idx % len(pool)]
            picks.append(template.replace("{{subject}}", topic.strip()))
        logger.debug("select_random_prompt count=%s unique_templates=%s", count, len(set(picks)))
        return picks

    def generate_with_variation(self, topic: str, num_variations: int = 3) -> list[str]:
        """Generate one image per varied prompt derived from ``topic``.

        Args:
            topic: Subject for template substitution.
            num_variations: Number of prompt variations (and images).

        Returns:
            Flat list of image paths (length ``num_variations`` when successful
            or placeholder-backed).
        """
        prompts = self.select_random_prompt(topic, num_variations)
        paths: list[str] = []
        for line in prompts:
            paths.extend(self.generate_image(line, num_images=1))
        return paths
