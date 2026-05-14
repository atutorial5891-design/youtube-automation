"""Hybrid script generation scaffold."""

from __future__ import annotations

from dataclasses import dataclass

from src.api.chatgpt_client import ChatGPTClient
from src.api.deepseek_client import DeepSeekClient


@dataclass
class ScriptBundle:
    topic: str
    outline_prompt: str
    script_prompt: str


class HybridScriptGenerator:
    """Uses DeepSeek for structure and a writing model for final script quality."""

    def __init__(
        self,
        deepseek_client: DeepSeekClient | None = None,
        writing_client: ChatGPTClient | None = None,
    ) -> None:
        self.deepseek_client = deepseek_client or DeepSeekClient()
        self.writing_client = writing_client or ChatGPTClient()

    def build_prompts(self, topic: str) -> ScriptBundle:
        outline_prompt = f"Create a research-backed outline for: {topic}"
        script_prompt = f"Write a compelling YouTube script using this outline topic: {topic}"
        return ScriptBundle(topic=topic, outline_prompt=outline_prompt, script_prompt=script_prompt)
