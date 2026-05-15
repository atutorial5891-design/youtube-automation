"""Tests for :class:`TTSHandler` in ``src.api.google_tts``."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.api.google_tts import TTSHandler
from src.utils.exceptions import ExternalServiceError, ValidationError


@pytest.fixture
def fake_credentials(tmp_path: Path) -> Path:
    path = tmp_path / "fake-sa.json"
    path.write_text('{"type": "service_account"}', encoding="utf-8")
    return path


@pytest.fixture
def patched_google_clients(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Avoid real Google auth; return a controllable TTS client."""
    mock_client = MagicMock()
    response = MagicMock()
    response.audio_content = b"\x00\x01" * 8000
    mock_client.synthesize_speech.return_value = response

    import google.cloud.texttospeech as tts_mod

    monkeypatch.setattr(tts_mod, "TextToSpeechClient", MagicMock(return_value=mock_client))
    monkeypatch.setattr(
        "google.oauth2.service_account.Credentials.from_service_account_file",
        lambda _path: MagicMock(),
    )
    return mock_client


def test_tts_handler_init(fake_credentials: Path, patched_google_clients: MagicMock) -> None:
    handler = TTSHandler(str(fake_credentials), "test-project")
    assert handler.project_id == "test-project"
    patched_google_clients.synthesize_speech.assert_not_called()


def test_generate_audio_returns_bytes(
    fake_credentials: Path, patched_google_clients: MagicMock
) -> None:
    handler = TTSHandler(str(fake_credentials), "p")
    audio = handler.generate_audio("Hello from the test suite.")
    assert isinstance(audio, (bytes, bytearray))
    assert audio.startswith(b"RIFF")
    patched_google_clients.synthesize_speech.assert_called_once()


def test_add_ssml_formatting_returns_string(
    fake_credentials: Path, patched_google_clients: MagicMock
) -> None:
    handler = TTSHandler(str(fake_credentials), "p")
    ssml = handler.add_ssml_formatting("Line one.\n\nLine two.")
    assert isinstance(ssml, str)
    assert ssml.startswith("<speak")
    assert "</speak>" in ssml


def test_add_ssml_inserts_line_breaks_inside_paragraph(
    fake_credentials: Path, patched_google_clients: MagicMock,
) -> None:
    handler = TTSHandler(str(fake_credentials), "p")
    ssml = handler.add_ssml_formatting("Line a\nLine b")
    assert "break time" in ssml


def test_generate_audio_output_passes_quality_check(
    fake_credentials: Path, patched_google_clients: MagicMock
) -> None:
    handler = TTSHandler(str(fake_credentials), "p")
    audio = handler.generate_audio("Short clip.")
    assert handler.validate_audio_quality(audio) is True


def test_validate_audio_quality(fake_credentials: Path, patched_google_clients: MagicMock) -> None:
    handler = TTSHandler(str(fake_credentials), "p")
    pcm = b"\x00\x00" * 2000
    wav = TTSHandler._pcm16_mono_to_wav(pcm, sample_rate=44100)
    assert handler.validate_audio_quality(wav) is True
    assert handler.validate_audio_quality(b"") is False
    assert handler.validate_audio_quality(b"not-wav") is False


def test_error_handling_invalid_credentials(tmp_path: Path) -> None:
    missing = tmp_path / "nope.json"
    with pytest.raises(ValidationError) as exc:
        TTSHandler(str(missing), "pid")
    assert "not found" in str(exc.value).lower()


def test_error_handling_empty_text(
    fake_credentials: Path, patched_google_clients: MagicMock
) -> None:
    handler = TTSHandler(str(fake_credentials), "p")
    with pytest.raises(ValidationError):
        handler.generate_audio("   ")


def test_generate_audio_api_error(
    fake_credentials: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_client = MagicMock()
    mock_client.synthesize_speech.side_effect = RuntimeError("quota")

    import google.cloud.texttospeech as tts_mod

    monkeypatch.setattr(tts_mod, "TextToSpeechClient", MagicMock(return_value=mock_client))
    monkeypatch.setattr(
        "google.oauth2.service_account.Credentials.from_service_account_file",
        lambda _path: MagicMock(),
    )
    handler = TTSHandler(str(fake_credentials), "p")
    with pytest.raises(ExternalServiceError):
        handler.generate_audio("Some narration text.")
