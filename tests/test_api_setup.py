from src.api.chatgpt_client import ChatGPTClient
from src.api.deepseek_client import DeepSeekClient


def test_deepseek_payload_uses_expected_model() -> None:
    client = DeepSeekClient(api_key="test-key", model="deepseek-chat")
    payload = client.build_payload("hello", max_tokens=300)
    assert payload["model"] == "deepseek-chat"
    assert payload["messages"][-1]["content"] == "hello"


def test_openai_client_defaults_to_openai() -> None:
    client = ChatGPTClient("test-openai-key", model="gpt-4o-mini", provider="openai")
    assert client.current_config()["provider"] == "openai"
    assert client.model == "gpt-4o-mini"
