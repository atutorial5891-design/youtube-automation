from src.generation.script_generator import HybridScriptGenerator


def test_build_prompts_keeps_topic_visible() -> None:
    generator = HybridScriptGenerator()
    bundle = generator.build_prompts("sleep quality")
    assert "sleep quality" in bundle.outline_prompt
    assert "sleep quality" in bundle.script_prompt
