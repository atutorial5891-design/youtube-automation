# Troubleshooting

## Common Setup Issues

### `uv` not found
Install it with `python3 -m pip install uv` and rerun `scripts/setup.sh`.

### Python version too old
Use Python `3.11+` before creating the virtual environment.

### Missing Google or YouTube credentials
Place the JSON files in `config/` and update `.env` to match the paths.

### API smoke tests fail
Check that `.env` contains real keys, the selected model names are valid, and billing is enabled where required.

### Local media dependencies missing
Install `ffmpeg`, verify `ollama` is running, and confirm the target models are available before Stage 2.
