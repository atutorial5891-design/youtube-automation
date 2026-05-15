# Troubleshooting

## Common Setup Issues

### `uv` not found
Install it with `python3 -m pip install uv` and rerun `scripts/setup.sh`.

### `pip` not found after `source venv/bin/activate`
Environments created with **`uv venv`** may not place a **`pip`** executable on `PATH`. Use **`uv`** instead of bare **`pip`**:

```bash
uv pip install -e ".[dev]"
```

Or target the venv explicitly from the repo root (no activation required):

```bash
uv pip install --python ./venv/bin/python -e ".[dev]"
```

As a last resort: `python -m pip install -e ".[dev]"` if the interpreter has pip available.
Use Python `3.11+` before creating the virtual environment.

### Missing Google or YouTube credentials
Place the JSON files in `config/` and update `.env` to match the paths.

### API smoke tests fail
Check that `.env` contains real keys, the selected model names are valid, and billing is enabled where required.

### Local media dependencies missing
Install `ffmpeg`, verify `ollama` is running, and confirm the target models are available before Stage 2.
