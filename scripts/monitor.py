"""Simple filesystem-based monitor for Stage 1."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def count_files(path: Path) -> int:
    return sum(1 for item in path.rglob("*") if item.is_file())


def main() -> int:
    targets = {
        "pending scripts": PROJECT_ROOT / "data" / "pending_scripts",
        "approved scripts": PROJECT_ROOT / "data" / "approved_scripts",
        "generated videos": PROJECT_ROOT / "data" / "generated_videos",
        "published videos": PROJECT_ROOT / "data" / "published_videos",
        "analytics": PROJECT_ROOT / "data" / "analytics",
        "logs": PROJECT_ROOT / "logs",
    }

    print("Workspace monitor")
    print("=================")
    for label, path in targets.items():
        print(f"{label}: {count_files(path)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
