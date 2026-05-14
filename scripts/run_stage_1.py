"""Entry point for the Stage 1 scaffold."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.orchestrator import Orchestrator


def main() -> int:
    orchestrator = Orchestrator()
    state = orchestrator.bootstrap()

    print("Stage 1 scaffold is ready.")
    print(f"Current stage: {state.stage}")
    print(f"Status: {state.status}")
    print()
    print("Next steps:")
    for step in orchestrator.summarize_next_steps():
        print(f"- {step}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
