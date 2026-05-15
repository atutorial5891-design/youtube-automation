#!/bin/bash
set -euo pipefail

echo "YouTube Automation setup"
echo "========================"

if command -v python3.11 >/dev/null 2>&1; then
  PYTHON_BIN="python3.11"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
else
  echo "Python 3.11+ is required."
  exit 1
fi

PYTHON_VERSION=$($PYTHON_BIN -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [[ "$(printf '%s\n' "3.11" "$PYTHON_VERSION" | sort -V | head -n1)" != "3.11" ]]; then
  echo "Python 3.11+ is required."
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "Installing uv..."
  "$PYTHON_BIN" -m pip install uv
fi

echo "Creating virtual environment..."
# Reuse an existing venv so setup can be safely re-run.
uv venv --allow-existing venv
source venv/bin/activate

echo "Installing project dependencies..."
uv pip install -e ".[dev]"

if [ ! -f .env ]; then
  echo "Creating .env from template..."
  cp .env.example .env
fi

mkdir -p \
  logs/daily_logs \
  logs/error_logs \
  logs/api_logs \
  logs/performance_logs \
  data/pending_scripts \
  data/approved_scripts \
  data/generated_videos \
  data/generated_videos/images \
  data/published_videos \
  data/analytics

echo
echo "Setup complete."
echo "Next steps:"
echo "1. Update .env with your API keys."
echo "2. Run: python scripts/test_apis.py"
echo "3. Review: docs/STAGE_1_EXECUTION_PLAN.md"
