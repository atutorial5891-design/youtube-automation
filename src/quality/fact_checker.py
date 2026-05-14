"""Fact-check planning structures."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ClaimReview:
    claim: str
    risk_level: str
    notes: str


class FactChecker:
    def summarize_claims(self, claims: list[str]) -> list[ClaimReview]:
        return [ClaimReview(claim=claim, risk_level="caution", notes="Manual review recommended.") for claim in claims]
