# YouTube Automation

Production-minded scaffolding for a faceless YouTube video pipeline: environment setup through multi-channel publishing over seven stages. **This file is the single project overview**—architecture, credentials, checklists, and links to deeper docs live here.

## Overview

Hybrid automation:

- **DeepSeek** — low-cost topic research, outlines, and keyword work.
- **ChatGPT** or **Claude** — script writing, verification, tone variation, and fact-checking.
- **Google Cloud TTS**, **Ollama/SDXL**, **MoviePy/FFmpeg**, and the **YouTube API** — narration, images, assembly, and publishing.

The layout supports one channel now and multiple channels later without a layout refactor.

## System requirements

- macOS (M4 Max–class machine in the original plan)
- 36 GB RAM (planning target)
- 300 GB+ free storage
- Python 3.11+
- `uv` package manager
- FFmpeg on `PATH`

Start with **[Stage 1 walkthrough with uv](#stage-1-walkthrough-with-uv)** below for copy-paste setup and test commands.

## Stage 1 walkthrough with uv

This section is the **hands-on path** for Stage 1: create a virtual environment with **uv**, install the project, run scaffold scripts, and run tests. Commands assume a Unix shell (macOS/Linux) and repository root as the current directory.

### 0. Install uv (one-time on the machine)

If `uv` is not installed yet, use one of the [official install options](https://docs.astral.sh/uv/getting-started/installation/). Examples:

```bash
# macOS/Linux (installer script)
curl -LsSf https://astral.sh/uv/install.sh | sh
# Restart the shell or follow the installer’s note so `uv` is on PATH.

# Homebrew (macOS)
brew install uv

uv --version   # should print a version (e.g. 0.4.x or newer)
```

### 1. Go to the project

```bash
cd /path/to/YouTube-Automation
# Example: cd ~/projects/YouTube-Automation
```

### 2. Create the venv and install dependencies (choose one path)

**Path A — recommended: use the bundled setup script**

`scripts/setup.sh` uses **uv** to create `venv/`, activates it, runs `uv pip install -e ".[dev]"`, seeds `.env` from `.env.example` if missing, and creates `data/` and `logs/` folders.

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

After it finishes you should see `Setup complete.` and next-step hints.

**Path B — same result, explicit uv commands**

Use this if you prefer not to run the shell script (or you are debugging install issues).

```bash
uv venv --allow-existing venv
source venv/bin/activate          # Windows (cmd): venv\Scripts\activate.bat
uv pip install -e ".[dev]"        # app + pytest, ruff, black, mypy (dev extra)
```

The setup script also creates `data/` and `logs/` subfolders. If you never run Path A, run `./scripts/setup.sh` once anyway (it is idempotent) **or** copy the `mkdir -p` block from `scripts/setup.sh` so monitors and stages have the expected paths.

If `.env` does not exist yet:

```bash
cp .env.example .env
# Edit .env with your keys, or rely on llm_gateway (see [Credentials](#credentials)).
```

### 3. Optional: llm_gateway next to this repo

If you use [llm_gateway](https://github.com/atutorial5891-design/llm_gateway) as a sibling folder `../llm_gateway`, either keep it as a sibling (auto-import) or install it into the same venv:

```bash
source venv/bin/activate
uv pip install -e ../llm_gateway
```

### 4. Run Stage 1 scaffold scripts (examples)

With the venv **activated** (`source venv/bin/activate`):

```bash
# Smoke-test the Stage 1 entrypoint (prints status / next steps)
python scripts/run_stage_1.py
# Example lines you may see:
#   Stage 1 scaffold is ready.
#   Current stage: stage_1
#   Status: initialized

# Filesystem counters for pipeline folders
python scripts/monitor.py
# Example: counts for pending scripts, approved scripts, generated videos, etc.
```

**Without** activating the venv, you can still run commands through uv (uses project metadata + `venv`):

```bash
uv run python scripts/run_stage_1.py
uv run python scripts/monitor.py
```

### 5. Run automated tests (examples)

```bash
source venv/bin/activate

# Full test suite (same as CI-style local check)
uv run --extra dev pytest

# Single file (API payload / client defaults)
uv run --extra dev pytest tests/test_api_setup.py -v

# LLM keychain resolution + masked print demo (use -s to see prints)
uv run --extra dev pytest tests/test_llm_gateway_keys.py -v
uv run --extra dev pytest tests/test_llm_gateway_keys.py::TestLLMGatewaySecretsPrintIntegration -s
```

### 6. Smoke-test external APIs (optional, needs credentials)

After `.env` and/or keychain secrets are configured:

```bash
source venv/bin/activate
python scripts/test_apis.py
```

Example outcomes:

- **All services configured:** ends with something like `Ready services: 4/4` and `All Stage 1 integrations look ready.`
- **Partial setup:** some lines show `[PENDING]` and the script exits non-zero; fill missing keys or JSON under `config/` and run again.

### 7. Stop or reset

- Scripts (`run_stage_1.py`, `monitor.py`, `test_apis.py`) exit on their own; use `Ctrl+C` only if something hangs.
- Leave the virtual environment: `deactivate`.
- Re-run setup safely after dependency changes: `./scripts/setup.sh` (reuses `venv` with `--allow-existing`).

---

## Credentials

### Environment variables (`.env`)

Use as needed (many are optional if keychain secrets exist):

| Variable | Purpose |
|----------|---------|
| `DEEPSEEK_API_KEY` | DeepSeek API (optional if `deepseek` is in keychain; see fallback below) |
| `OPENAI_API_KEY` / `CLAUDE_API_KEY` | Writing model |
| `GOOGLE_APPLICATION_CREDENTIALS` | Google Cloud |
| `GOOGLE_PROJECT_ID` | Google Cloud project |
| `YOUTUBE_CREDENTIALS_PATH` | YouTube OAuth client JSON |
| `YOUTUBE_CHANNEL_ID` | Target channel |

JSON credential files live under `config/` and are git-ignored.

### LLM API keys (llm_gateway)

Keys can be loaded from [llm_gateway](https://github.com/atutorial5891-design/llm_gateway) (macOS keychain via `keyring`, audit logs under `~/.llm_gateway/logs`). The Python API is **`SecretsManager`** in module `secrets_manager`.

**Setup (pick one):**

1. **Sibling repo:** clone `llm_gateway` as `../llm_gateway` (next to this repo). `src/utils/llm_keys.py` prepends that path if `secrets_manager` is not importable.
2. **Editable install:** `pip install -e ../llm_gateway` or `uv pip install -e ../llm_gateway` from your activated venv.

Store accounts as **`openai`** and **`deepseek`** (names are lowercased). Upstream CLI: `llm-gateway-secret`, `llm-gateway-get-secret`.

**Resolution in this repo** (`src/utils/llm_keys.py`):

- **OpenAI (writing path):** `SecretsManager.get_openai_key()` → if missing → `OPENAI_API_KEY`. Helper: `get_openai_api_key()`. Used by `ChatGPTClient.is_configured()` for OpenAI.
- **DeepSeek client path:** `get_deepseek_key()` → if missing, `get_openai_key()` **twice** (explicit retry) → `DEEPSEEK_API_KEY` → `OPENAI_API_KEY`. Helper: `get_deepseek_api_key_with_openai_fallback()`. Used by `DeepSeekClient` and `scripts/test_apis.py`.

`pyproject.toml` includes **`keyring`** (required by the gateway). The `llm-gateway-secrets` package is not on PyPI; use the sibling path or editable install above.

**Tests:** `uv run --extra dev pytest tests/test_llm_gateway_keys.py -s` — masked keychain output and fallback behavior.

**Note:** The DeepSeek **HTTP API** expects a real DeepSeek token for production. Falling back to an OpenAI-shaped secret is for convenience until a `deepseek` secret is stored.

---

## System architecture

### Design split

Cheap, high-volume analytical work is separated from quality-critical creative work.

| Layer | Role |
|-------|------|
| DeepSeek | Topics, outlines, keywords, research support |
| ChatGPT / Claude | Scripts, verification, tone, fact-checking, policy-sensitive analysis |
| Google Cloud TTS | Voice |
| Ollama / SDXL | Local images |
| MoviePy / FFmpeg | Assembly |
| YouTube API | Upload, scheduling, analytics |

### Components

- **`HybridScriptGenerator`** — DeepSeek research plus a higher-quality writing model.
- **`DeepSeekClient`** — API key from `get_deepseek_api_key_with_openai_fallback()` unless overridden.
- **`ChatGPTClient`** — OpenAI configured when `get_openai_api_key()` returns a value.
- **`AgentVerifier`** — clarity, flow, engagement, risk.
- **`ToneManager`** — tone profile and 2–3 variations.
- **`FactChecker`** — risky claims before publish.
- **`VideoAssembler`** — render plan and output.
- **`YouTubeClient`** — upload readiness and publish.
- **`Orchestrator`** — coordination, retries, gates.

### Data flow

```text
Topic idea
  -> DeepSeek topic research (key from llm_keys: deepseek, else openai / env)
  -> DeepSeek outline
  -> ChatGPT/Claude script draft
  -> Agent verification
      -> fail: retry draft up to max retries
      -> pass: continue
  -> Tone selection and variation
  -> Fact-check and risk review
  -> Google TTS narration
  -> Ollama/SDXL image prompts and generation
  -> MoviePy/FFmpeg assembly
  -> Video validation
  -> Human review
  -> YouTube upload and scheduling
  -> Analytics capture
```

### API allocation

**DeepSeek:** topic generation, outlines, keyword research, background research.

**ChatGPT/Claude:** script writing, verification, tone variation, fact-checking, policy-sensitive analysis.

Do not swap these roles; the planning docs treat that as a quality and cost regression.

### Quality gates

**Stage transitions:**

1. Stage 1 → 2: design validation and environment readiness  
2. Stage 2 → 3: agent accuracy ≥ 80%  
3. Stage 3 → 4: quality pass rate ≥ 75%  
4. Stage 4 → 5: upload flow works  
5. Stage 5 → 6: average quality ≥ 7/10  
6. Stage 6 → 7: zero strikes and sustainable workflow  

**Within the content pipeline:**

```text
Agent verification -> Fact-check -> Human final review
```

### Scalability

- Per-channel assets: `channels/<channel_name>/`.
- Shared logic: `config/` and `src/`.
- Overrides via `config_loader.py` without changing the core flow.
- Logs and analytics partitioned for multi-channel use.

### Stage 1 scope (current repo)

Scaffolding: filesystem layout, runtime settings, prompt/config templates, module boundaries, setup and smoke scripts, **LLM key resolution** via `llm_keys.py` and optional **llm_gateway**. Heavier implementation stays thin until later stages.

---

## Repository layout

| Path | Role |
|------|------|
| `src/core/` | Orchestration, config loading, logging |
| `src/utils/llm_keys.py` | LLM keys: `SecretsManager` + `.env` fallbacks |
| `src/api/` | DeepSeek, OpenAI/Claude, Google TTS, YouTube |
| `src/generation/` | Script, tone, image coordination |
| `src/quality/` | Verification, fact-checking, gates |
| `src/video/` | Assembly and output validation |
| `config/` | Prompts, templates, settings |
| `scripts/` | Setup, smoke tests, monitoring, Stage 1 helpers |
| `docs/` | Stage plans, gates, rollback, technical references |

---

## Documentation index (`docs/`)

| Document | Contents |
|----------|----------|
| `STAGE_1_EXECUTION_PLAN.md` … `STAGE_7_EXECUTION_PLAN.md` | Day-by-day execution sequence |
| `STAGE_TRANSITIONS_AND_GATES.md` | Go/no-go criteria |
| `ROLLBACK_PROCEDURES.md` | Recovery procedures |
| `API_ALLOCATION_BY_STAGE.md` | Cost and API usage by stage |
| `WORKFLOW.md` | Daily workflow |
| `TROUBLESHOOTING.md` | Common failures |
| `AGENT_VERIFICATION_SYSTEM.md` | Agent verification design |
| `TONE_LIBRARY.md` | Tone profiles |
| `DESIGN_VALIDATION_TEST.md` | Design validation |
| `API_LIMITS.md` | API limits |
| `OLLAMA_BASELINE.md` | Ollama baseline |
| `CURSOR_IMPLEMENTATION_GUIDE.md` | Cursor-oriented scaffolding notes |

---

## Stage 1 checklist

Complete before Stage 2:

- [ ] Project structure present; `scripts/setup.sh` completes successfully
- [ ] `uv venv` created `venv/` and `uv pip install -e ".[dev]"` completed (via `./scripts/setup.sh` or manual commands in the walkthrough)
- [ ] `.env` and/or llm_gateway secrets configured (see [Credentials](#credentials))
- [ ] DeepSeek verified (`python scripts/test_apis.py` or equivalent)
- [ ] OpenAI or Claude verified
- [ ] Google TTS credentials verified
- [ ] YouTube OAuth credentials verified
- [ ] Ollama + SDXL installed and tested; baseline in `docs/OLLAMA_BASELINE.md`
- [ ] Agent verification system documented and design logic validated (`docs/AGENT_VERIFICATION_SYSTEM.md`, `docs/DESIGN_VALIDATION_TEST.md`)
- [ ] Tone variation system documented (`docs/TONE_LIBRARY.md`)
- [ ] Supporting docs present as needed: `docs/WORKFLOW.md`, `docs/TROUBLESHOOTING.md`, `docs/API_LIMITS.md`; `config/settings.json` configured
- [ ] Credentials backed up securely (outside git)

## Stage 1 complete (sign-off)

When Stage 1 is finished, fill in:

- **Date completed:** _[date]_
- **Notes:** _[e.g. APIs verified, docs updated]_

Proceed to Stage 2 only when every checklist item above is done.

---

## Stage progression

1. **Stage 1** — environment, credentials, design artifacts, scaffolding  
2. **Stage 2** — orchestration, script generation, tone, media assembly  
3. **Stage 3** — quality gates, fact-checking, human review  
4. **Stage 4** — YouTube auth, uploads, scheduling, metadata  
5. **Stage 5** — integration tests, load tests, accuracy  
6. **Stage 6** — soft launch, monitored publishing  
7. **Stage 7** — production rollout, multi-channel scaling  

Follow `docs/STAGE_1_EXECUTION_PLAN.md` through `docs/STAGE_7_EXECUTION_PLAN.md` for detail.

## Cost breakdown

- Stage 1 setup/testing: ~$0  
- Pre-production through Stage 6: ~$11  
- Production target: ~$0.28 per video  
- Monthly at scale: ~$56  

Source: `docs/API_ALLOCATION_BY_STAGE.md`.

## Timeline

- Week 1: Stage 1  
- Weeks 1–2: Stage 2  
- Week 2: Stage 3  
- Weeks 2–3: Stage 4  
- Week 3: Stage 5  
- Weeks 3–4: Stage 6  
- Week 4+: Stage 7  

Target: **~47 days** (~6–7 weeks) to production readiness.

## Year 1 projection (planning targets)

- 260–365 published videos  
- 100K+ subscribers  
- 5+ channels by month 12  
- $50K–$100K total revenue in year 1  

Not guarantees—planning figures from the original business model.
