"""Stage and content gate evaluation helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GateDecision:
    name: str
    passed: bool
    detail: str


def stage_one_gate(design_tests_passed: bool, apis_ready: bool, ollama_ready: bool) -> GateDecision:
    passed = all([design_tests_passed, apis_ready, ollama_ready])
    detail = "Ready for Stage 2" if passed else "Complete Stage 1 checks before proceeding"
    return GateDecision(name="stage_1_to_stage_2", passed=passed, detail=detail)
