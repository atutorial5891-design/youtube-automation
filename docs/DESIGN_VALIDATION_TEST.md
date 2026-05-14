# Design Validation Test

Use this checklist to validate Stage 1 logic before starting Stage 2.

## Tests

1. Agent verification thresholds behave as expected.
2. Retry logic stops after 3 retries.
3. Tone selection can vary between eligible tones.
4. Tone variation count stays within 2-3 outputs.

These checks are mirrored by the lightweight Python tests in `tests/`.
