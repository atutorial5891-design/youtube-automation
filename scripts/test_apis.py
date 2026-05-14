"""Smoke-test external service configuration for Stage 1."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - setup dependency
    load_dotenv = None

from src.utils.llm_keys import (
    get_deepseek_api_key_with_openai_fallback,
    get_openai_api_key,
)


def status_line(name: str, ok: bool, detail: str) -> str:
    label = "READY" if ok else "PENDING"
    return f"[{label}] {name}: {detail}"


def load_environment() -> None:
    if load_dotenv is not None:
        load_dotenv(PROJECT_ROOT / ".env")


def test_deepseek() -> tuple[bool, str]:
    api_key = get_deepseek_api_key_with_openai_fallback() or ""
    if not api_key:
        return False, "missing DeepSeek key and no OpenAI fallback in keychain/.env"
    try:
        import requests

        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
                "messages": [{"role": "user", "content": "Return the word ok."}],
                "max_tokens": 8,
            },
            timeout=20,
        )
        if response.ok:
            return True, "network call succeeded"
        return False, f"HTTP {response.status_code}"
    except Exception as exc:  # pragma: no cover - live network path
        return False, str(exc)


def test_writing_model() -> tuple[bool, str]:
    openai_key = get_openai_api_key() or ""
    claude_key = os.getenv("CLAUDE_API_KEY", "")

    if openai_key:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[{"role": "user", "content": "Say ok."}],
                max_tokens=8,
            )
            text = response.choices[0].message.content or ""
            return True, f"OpenAI responded with: {text[:20]!r}"
        except Exception as exc:  # pragma: no cover - live network path
            return False, f"OpenAI error: {exc}"

    if claude_key:
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=claude_key)
            response = client.messages.create(
                model=os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-latest"),
                max_tokens=8,
                messages=[{"role": "user", "content": "Say ok."}],
            )
            text = response.content[0].text if response.content else ""
            return True, f"Claude responded with: {text[:20]!r}"
        except Exception as exc:  # pragma: no cover - live network path
            return False, f"Claude error: {exc}"

    return False, "set OPENAI_API_KEY or CLAUDE_API_KEY"


def test_google_tts() -> tuple[bool, str]:
    credentials_path = PROJECT_ROOT / os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS",
        "config/google-credentials.json",
    )
    if not credentials_path.exists():
        return False, f"missing credentials file at {credentials_path.relative_to(PROJECT_ROOT)}"
    try:
        from google.cloud import texttospeech

        client = texttospeech.TextToSpeechClient()
        response = client.synthesize_speech(
            input=texttospeech.SynthesisInput(text="Stage one test."),
            voice=texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name="en-US-Neural2-C",
            ),
            audio_config=texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
            ),
        )
        return True, f"generated {len(response.audio_content)} audio bytes"
    except Exception as exc:  # pragma: no cover - live network path
        return False, str(exc)


def test_youtube_credentials() -> tuple[bool, str]:
    credentials_path = PROJECT_ROOT / os.getenv(
        "YOUTUBE_CREDENTIALS_PATH",
        "config/youtube-credentials.json",
    )
    if not credentials_path.exists():
        return False, f"missing credentials file at {credentials_path.relative_to(PROJECT_ROOT)}"
    try:
        payload = json.loads(credentials_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, f"invalid JSON: {exc}"

    if "installed" in payload or "web" in payload:
        return True, "OAuth client file present; run interactive auth in Stage 4"
    return False, "credentials JSON is missing installed/web OAuth keys"


def main() -> int:
    load_environment()
    results = [
        ("DeepSeek", test_deepseek()),
        ("Writing model", test_writing_model()),
        ("Google TTS", test_google_tts()),
        ("YouTube OAuth", test_youtube_credentials()),
    ]

    print("Stage 1 API readiness")
    print("=====================")
    for name, (ok, detail) in results:
        print(status_line(name, ok, detail))

    ready_count = sum(1 for _, (ok, _) in results if ok)
    print()
    print(f"Ready services: {ready_count}/{len(results)}")

    if ready_count == len(results):
        print("All Stage 1 integrations look ready.")
        return 0

    print("Next steps:")
    print("- Fill any missing values in .env.")
    print("- Add credential JSON files to config/.")
    print("- Re-run this script after setup changes.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
