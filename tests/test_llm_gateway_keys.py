"""Tests for llm_gateway-backed API key resolution (``SecretsManager``)."""

from __future__ import annotations

import src.utils.llm_keys as lk


class TestLLMGatewaySecretsResolution:
    def test_deepseek_missing_uses_second_openai_keychain_read(self, monkeypatch) -> None:
        monkeypatch.setattr(
            lk.SecretsManager,
            "get_deepseek_key",
            staticmethod(lambda masked=False, context=None: None),
        )
        calls: list[int] = []

        def openai_side(masked=False, context=None):
            calls.append(1)
            return "sk-second-read" if len(calls) >= 2 else None

        monkeypatch.setattr(
            lk.SecretsManager,
            "get_openai_key",
            staticmethod(openai_side),
        )
        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        assert lk.get_deepseek_api_key_with_openai_fallback() == "sk-second-read"
        assert len(calls) == 2

    def test_deepseek_present_skips_openai(self, monkeypatch) -> None:
        o_calls: list[int] = []

        def openai_side(masked=False, context=None):
            o_calls.append(1)
            return "sk-openai"

        monkeypatch.setattr(
            lk.SecretsManager,
            "get_deepseek_key",
            staticmethod(lambda masked=False, context=None: "sk-deepseek"),
        )
        monkeypatch.setattr(
            lk.SecretsManager,
            "get_openai_key",
            staticmethod(openai_side),
        )
        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        assert lk.get_deepseek_api_key_with_openai_fallback() == "sk-deepseek"
        assert o_calls == []

    def test_deepseek_chain_env_openai_after_empty_keychain(self, monkeypatch) -> None:
        monkeypatch.setattr(
            lk.SecretsManager,
            "get_deepseek_key",
            staticmethod(lambda masked=False, context=None: None),
        )
        monkeypatch.setattr(
            lk.SecretsManager,
            "get_openai_key",
            staticmethod(lambda masked=False, context=None: None),
        )
        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
        monkeypatch.setenv("OPENAI_API_KEY", "sk-from-env")
        assert lk.get_deepseek_api_key_with_openai_fallback() == "sk-from-env"


class TestLLMGatewaySecretsPrintIntegration:
    """Run with ``pytest -s`` to see masked values from the local keychain."""

    def test_print_openai_and_deepseek_masked(self, capsys) -> None:
        openai_m = lk.SecretsManager.get_openai_key(masked=True)
        deepseek_m = lk.SecretsManager.get_deepseek_key(masked=True)
        effective = lk.get_deepseek_api_key_with_openai_fallback()
        print("openai (masked):", openai_m)
        print("deepseek (masked):", deepseek_m)
        if effective:
            print("effective DeepSeek-path key length:", len(effective))
        else:
            print("effective DeepSeek-path key: <none>")
        out = capsys.readouterr().out
        assert "openai (masked):" in out
        assert "deepseek (masked):" in out
