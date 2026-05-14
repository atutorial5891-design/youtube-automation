"""Image prompt planning for local generation backends."""

from __future__ import annotations

from src.core.config_loader import ConfigLoader


class ImageGenerator:
    def __init__(self, config_loader: ConfigLoader | None = None) -> None:
        self.config_loader = config_loader or ConfigLoader()
        self.templates = self.config_loader.load_json("image_prompts.json")["templates"]

    def build_prompt(self, subject: str, template_index: int = 0) -> str:
        template = self.templates[template_index % len(self.templates)]
        return template.replace("{{subject}}", subject)
