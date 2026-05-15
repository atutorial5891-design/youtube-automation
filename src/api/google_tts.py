"""Google Cloud Text-to-Speech handler (WAV output, SSML helpers, validation)."""

from __future__ import annotations

import html
import io
import logging
import re
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.utils.exceptions import ExternalServiceError, ValidationError

logger = logging.getLogger(__name__)

_MIN_WAV_BYTES = 44 + 200  # RIFF header + a little PCM payload


@dataclass
class VoiceSettings:
    """Default Google TTS voice parameters (legacy helper)."""

    language_code: str = "en-US"
    voice_name: str = "en-US-Neural2-C"
    speaking_rate: float = 1.0


class TTSHandler:
    """Synthesize narration audio via Google Cloud Text-to-Speech."""

    def __init__(self, credentials_path: str, project_id: str) -> None:
        """Create a client using a service-account JSON file.

        Args:
            credentials_path: Path to the Google Cloud service account JSON.
            project_id: Google Cloud project id (stored for logging and optional
                client configuration).

        Raises:
            ValidationError: If ``credentials_path`` is missing or not a file.
            ExternalServiceError: If the Text-to-Speech client cannot be created.
        """
        self.credentials_path = str(Path(credentials_path).expanduser())
        self.project_id = (project_id or "").strip()
        path_obj = Path(self.credentials_path)
        if not path_obj.is_file():
            raise ValidationError(
                f"Google TTS credentials file not found: {path_obj}. "
                "Set credentials_path to a valid service account JSON."
            )

        try:
            from google.cloud import texttospeech
            from google.oauth2 import service_account

            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path
            )
            self._client: Any = texttospeech.TextToSpeechClient(credentials=credentials)
            self._texttospeech = texttospeech
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to initialize Google Cloud Text-to-Speech client")
            raise ExternalServiceError(f"Google TTS client initialization failed: {exc}") from exc

        self._default_voice = "en-US-Neural2-C"
        logger.info(
            "TTSHandler ready credentials=%s project_id=%s",
            path_obj.name,
            self.project_id or "(unset)",
        )

    def _language_code_for_voice(self, voice_name: str) -> str:
        """Derive BCP-47 language code from a voice name like ``en-US-Neural2-C``."""
        parts = voice_name.split("-")
        if len(parts) >= 2 and len(parts[0]) == 2:
            return f"{parts[0]}-{parts[1]}"
        return "en-US"

    def add_ssml_formatting(self, script: str) -> str:
        """Wrap plain narration in SSML for pacing, pauses, and light emphasis.

        Escapes XML-sensitive characters, adds paragraph breaks on blank lines,
        and slightly slows the global rate for clarity.

        Args:
            script: Raw script text (no SSML wrapper).

        Returns:
            A string suitable for ``SynthesisInput(ssml=...)`` (includes
            ``<speak>...</speak>`` root).
        """
        text = (script or "").strip()
        if not text:
            return "<speak></speak>"

        escaped = html.escape(text, quote=False)
        chunks = [c.strip() for c in re.split(r"\n\s*\n+", escaped) if c.strip()]
        inner_parts: list[str] = []
        for block in chunks:
            with_breaks = block.replace("\n", '<break time="200ms"/>')
            inner_parts.append(f"<p>{with_breaks}</p>")
        inner = "\n".join(inner_parts)
        ssml = (
            "<speak>\n"
            '<prosody rate="95%">'
            f"{inner}"
            "</prosody>\n"
            '<break time="300ms"/>\n'
            "</speak>"
        )
        logger.debug("Built SSML from script_len=%s blocks=%s", len(script), len(chunks))
        return ssml

    def generate_audio(self, text: str, voice_name: str = "en-US-Neural2-C") -> bytes:
        """Synthesize ``text`` to mono 16-bit PCM wrapped in a WAV container (44.1 kHz).

        Args:
            text: Plain text or SSML body (wrapped with SSML if it does not
                start with ``<speak``).
            voice_name: Google TTS voice id (default Neural2 ``en-US``).

        Returns:
            WAV file bytes.

        Raises:
            ValidationError: If ``text`` is empty after stripping.
            ExternalServiceError: On API or encoding failures.
        """
        raw = (text or "").strip()
        if not raw:
            raise ValidationError("generate_audio requires non-empty text.")

        use_ssml = raw.lstrip().startswith("<speak")
        ssml_body = raw if use_ssml else self.add_ssml_formatting(raw)

        tts = self._texttospeech
        lang = self._language_code_for_voice(voice_name)
        synthesis_input = tts.SynthesisInput(ssml=ssml_body)

        voice = tts.VoiceSelectionParams(
            language_code=lang,
            name=voice_name or self._default_voice,
        )
        audio_config = tts.AudioConfig(
            audio_encoding=tts.AudioEncoding.LINEAR16,
            sample_rate_hertz=44100,
            speaking_rate=1.0,
        )

        logger.info(
            "Google TTS synthesize voice=%s lang=%s ssml=%s text_len=%s",
            voice_name,
            lang,
            use_ssml,
            len(raw),
        )
        try:
            response = self._client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Google TTS synthesize_speech failed")
            raise ExternalServiceError(f"Google TTS API error: {exc}") from exc

        pcm = response.audio_content
        if not pcm:
            raise ExternalServiceError("Google TTS returned empty audio content.")

        wav_bytes = self._pcm16_mono_to_wav(pcm, sample_rate=44100)
        logger.info("Google TTS generated wav_bytes=%s", len(wav_bytes))
        return wav_bytes

    @staticmethod
    def _pcm16_mono_to_wav(pcm: bytes, sample_rate: int = 44100) -> bytes:
        """Pack raw little-endian PCM16 mono samples into a WAV byte string."""
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(pcm)
        return buffer.getvalue()

    def validate_audio_quality(self, audio_bytes: bytes) -> bool:
        """Return True if ``audio_bytes`` looks like a non-empty WAV payload.

        Args:
            audio_bytes: Candidate WAV file bytes.

        Returns:
            ``False`` for empty, truncated, or clearly invalid input.
        """
        if not audio_bytes or len(audio_bytes) < _MIN_WAV_BYTES:
            logger.warning("validate_audio_quality: too few bytes (%s)", len(audio_bytes or b""))
            return False
        if not audio_bytes.startswith(b"RIFF"):
            logger.warning("validate_audio_quality: missing RIFF header")
            return False
        if audio_bytes[8:12] != b"WAVE":
            return False
        try:
            with wave.open(io.BytesIO(audio_bytes), "rb") as wf:
                if wf.getnchannels() < 1 or wf.getsampwidth() < 1 or wf.getframerate() < 1:
                    return False
                frames = wf.getnframes()
                if frames <= 0:
                    return False
        except wave.Error as exc:
            logger.warning("validate_audio_quality: wave parse error: %s", exc)
            return False
        return True


class GoogleTTSClient:
    """Lightweight credentials path helper (Stage 1 smoke scripts)."""

    def __init__(self, credentials_path: str | None = None) -> None:
        import os

        self.credentials_path = str(
            Path(
                credentials_path
                or os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "config/google-credentials.json")
            ).expanduser()
        )

    def credentials_ready(self) -> bool:
        """Return whether the credentials JSON path exists."""
        return Path(self.credentials_path).is_file()

    def default_voice(self) -> VoiceSettings:
        """Return default voice parameters for display / planning."""
        return VoiceSettings()
