from src.quality.agent_verifier import AgentVerifier, VerificationResult


def test_verification_pass_thresholds() -> None:
    result = VerificationResult(clarity=75, flow=80, engagement=78)
    assert result.passed is True


def test_retry_limit_is_three_retries() -> None:
    verifier = AgentVerifier()
    failed = VerificationResult(clarity=60, flow=60, engagement=60, issues=["weak hook"])
    assert verifier.should_retry(failed, attempt_number=1) is True
    assert verifier.should_retry(failed, attempt_number=4) is False
