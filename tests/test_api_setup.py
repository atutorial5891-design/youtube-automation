from src.api.chatgpt_client import ChatGPTClient
from src.api.deepseek_client import DeepSeekClient


def test_deepseek_payload_uses_expected_model() -> None:
    client = DeepSeekClient(api_key="test-key", model="deepseek-chat")
    payload = client.build_payload("hello")
    assert payload["model"] == "deepseek-chat"


def test_openai_client_defaults_to_openai() -> None:
    client = ChatGPTClient()
    assert client.current_config().provider == "openai"
