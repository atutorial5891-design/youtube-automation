"""Agent verification scoring scaffold."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class VerificationResult:
    clarity: int
    flow: int
    engagement: int
    issues: list[str] = field(default_factory=list)

    @property
    def overall(self) -> float:
        return (self.clarity + self.flow + self.engagement) / 3

    @property
    def passed(self) -> bool:
        return (
            self.clarity >= 70
            and self.flow >= 75
            and self.engagement >= 70
            and not self.issues
            and self.overall >= 72
        )


class AgentVerifier:
    """Encapsulates Stage 1 verification thresholds and retry policy."""

    max_retries = 3

    def attempts_allowed(self) -> int:
        return 1 + self.max_retries

    def should_retry(self, result: VerificationResult, attempt_number: int) -> bool:
        return not result.passed and attempt_number < self.attempts_allowed()
