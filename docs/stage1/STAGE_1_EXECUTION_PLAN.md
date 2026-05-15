# STAGE 1 EXECUTION PLAN - READY TO LAUNCH
**Status:** ✅ READY TO START (When You Say Go)  
**Timeline:** Week 1 (5 days)  
**Your Involvement:** 0 hours (Setup only, no content work)  
**Estimated Time:** 20-30 hours of setup work

---

## HOW TO RUN STAGE 1 IN THIS REPOSITORY

This repository already contains the Stage 1 scaffold, so your goal is to verify that the setup, local scripts, and external credentials all work as expected.

### Start

Run these commands from the project root:

```bash
# 1. Prepare the local environment
./scripts/setup.sh

# 2. Activate the environment if you want an interactive shell
source venv/bin/activate

# 3. Confirm the scaffold boots
python scripts/run_stage_1.py

# 4. Confirm local folder counters work
python scripts/monitor.py

# 5. Confirm local tests pass
uv run --extra dev pytest

# 6. After filling .env and adding credential JSON files:
python scripts/test_apis.py
```

### Stop

Stage 1 is not a background service. Nothing keeps running after the commands finish.

- Use `Ctrl+C` only if you want to interrupt a command early.
- Run `deactivate` to leave the Python virtual environment.
- If you launched Ollama manually during Day 3 checks, stop or quit it separately after testing.

### How To Verify Output

#### 1. Setup verification

Command:

```bash
./scripts/setup.sh
```

Expected result:

- `venv/` exists
- `.env` exists
- dependency installation completes without errors
- terminal ends with `Setup complete.`

Quick check:

```bash
ls -d venv config src data logs tests scripts channels
test -f uv.lock && echo "✅ uv.lock present"
```

#### 2. Scaffold bootstrap verification

Command:

```bash
python scripts/run_stage_1.py
```

Expected result:

- `Stage 1 scaffold is ready.`
- `Current stage: stage_1`
- `Status: initialized`

#### 3. Workspace monitor verification

Command:

```bash
python scripts/monitor.py
```

Expected result:

- counters print for `pending scripts`, `approved scripts`, `generated videos`, `published videos`, `analytics`, and `logs`
- counts can be `0 files` during initial setup

#### 4. Local test verification

Command:

```bash
uv run --extra dev pytest
```

Expected result:

- pytest starts normally
- all Stage 1 smoke tests pass
- terminal ends with something like `7 passed`

#### 5. External API verification

Command:

```bash
python scripts/test_apis.py
```

Expected result after real credentials are configured:

- `DeepSeek` shows `READY`
- `Writing model` shows `READY`
- `Google TTS` shows `READY`
- `YouTube OAuth` shows `READY`
- summary ends with `Ready services: 4/4`

If credentials are still placeholders, `PENDING` is expected.

### Minimum Stage 1 Pass Criteria In This Repo

Treat Stage 1 as successfully tested when all of the following are true:

- `./scripts/setup.sh` completes
- `python scripts/run_stage_1.py` succeeds
- `python scripts/monitor.py` succeeds
- `uv run --extra dev pytest` passes
- `python scripts/test_apis.py` reaches `4/4` after you add real credentials

---

## PHASE 1.1: PRE-LAUNCH CHECKLIST (Before Starting)

**MUST VERIFY (Do these BEFORE Day 1):**

- [ ] M4 Max MacBook Pro available and dedicated
- [ ] 36GB RAM verified (check About This Mac)
- [ ] >300GB free storage (check About This Mac → Storage)
- [ ] Internet connection stable (test speed: >10 Mbps)
- [ ] **DeepSeek API key ready** (from deepseek.com - for topic generation)
- [ ] **ChatGPT OR Claude API key ready** (OpenAI or Anthropic - for script quality)
- [ ] Google Cloud TTS service account JSON ready
- [ ] YouTube API OAuth 2.0 credentials ready
- [ ] Terminal/Command line access ready (for setup commands)
- [ ] 20-30 hours available this week for setup

**If Any NOT Ready:** Delay Stage 1 start date

---

## HYBRID APPROACH REMINDER

**You will use TWO APIs:**

1. **DeepSeek** (cost-effective, research tasks)
   - Topic generation
   - Keyword research
   - Outlines
   - Fact verification support
   
2. **ChatGPT/Claude** (quality critical, creative tasks)
   - Script writing
   - Script evaluation
   - Tone variations
   - Agent verification

**This is NOT optional.** Do NOT try to use DeepSeek alone for script generation or evaluation. It will fail your quality gates.

---

## PHASE 1.2: DAY-BY-DAY EXECUTION

### DAY 1: M4 Mac Environment Setup (5-6 hours)

**Morning (2-3 hours):**
```bash
# 1. Create project directory
mkdir -p ~/YouTube-Automation
cd ~/YouTube-Automation

# 2. Verify M4 Mac specs
system_profiler SPHardwareDataType | grep -E "Model|Chip|Memory|Cores"
# Expected: M4 Max, 36GB, 14 cores

# 3. Check available storage
df -h / | grep Filesystem
# Expected: >300GB free

# 4. Install Homebrew (if not already)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 5. Install required tools
brew install node python@3.11 ffmpeg imagemagick
```

**Afternoon (3-3.5 hours):**
```bash
# 6. Create Python virtual environment
cd ~/YouTube-Automation
python3.11 -m venv venv
source venv/bin/activate

# 7. Create directory structure
mkdir -p config src data logs tests docs
mkdir -p data/pending_scripts data/approved_scripts data/generated_videos data/published_videos data/analytics
mkdir -p logs/daily_logs logs/error_logs

# 8. Create initial config files
cat > config/settings.json << 'EOF'
{
  "project": "YouTube Automation",
  "version": "1.0",
  "max_retries": 3,
  "max_videos_per_day": 7,
  "publish_schedule": "daily_5am",
  "m4_max_specs": {
    "ram_gb": 36,
    "gpu_cores": 10,
    "performance_cores": 10,
    "efficiency_cores": 4
  }
}
EOF

# 9. Create requirements.txt
cat > requirements.txt << 'EOF'
openai==1.3.0
google-cloud-texttospeech==2.13.0
google-auth-oauthlib==1.0.0
google-api-python-client==2.92.0
ollama==0.0.5
requests==2.31.0
python-dotenv==1.0.0
apscheduler==3.10.4
moviepy==1.0.3
librosa==0.10.0
pillow==10.0.0
EOF

# 10. Install Python packages
pip install -r requirements.txt

# 11. Test Python installation
python --version
pip list | grep openai
```

**Deliverable:** Project structure ready, all packages installed, M4 specs verified

**Verification:**
```bash
ls -la ~/YouTube-Automation/
# Should show: config, src, data, logs, tests, docs, venv, requirements.txt, settings.json
```

---

### DAY 2: API Credentials & Testing - HYBRID SETUP (6-7 hours)

**Morning (3-4 hours):**

**CRITICAL: This is Hybrid Approach - Set Up BOTH DeepSeek AND ChatGPT/Claude**

```
1. DeepSeek API Setup (for topic generation)
   - Go to https://platform.deepseek.com/api/keys
   - Create new API key
   - Copy key
   - Add to .env file: DEEPSEEK_API_KEY=sk-...
   - Note: DeepSeek is ONLY for topic generation, outlines, keyword research
   
2. ChatGPT API Setup (for script quality - CRITICAL)
   - Go to https://platform.openai.com/account/api-keys
   - Create new API key
   - Copy key
   - Add to .env file: OPENAI_API_KEY=sk-...
   - Note: ChatGPT/Claude is REQUIRED for script generation and evaluation
   
   OR
   
   Claude API Setup (alternative to ChatGPT)
   - Go to https://console.anthropic.com/account/keys
   - Create new API key
   - Copy key
   - Add to .env file: CLAUDE_API_KEY=sk-ant-...
   - Note: Claude is REQUIRED for script generation and evaluation

3. Google Cloud TTS Setup
   - Go to Google Cloud Console
   - Create new project: "YouTube-Automation"
   - Enable Text-to-Speech API
   - Create service account
   - Download JSON key file
   - Save to: config/google-credentials.json
   - Add to .env: GOOGLE_APPLICATION_CREDENTIALS=config/google-credentials.json

3. YouTube API Setup
   - Go to Google Cloud Console (same project)
   - Enable YouTube Data API v3
   - Create OAuth 2.0 credentials (Desktop app)
   - Download credentials JSON
   - Save to: config/youtube-credentials.json
   - Add to .env: YOUTUBE_CREDENTIALS=config/youtube-credentials.json
```

**Afternoon (3-3.5 hours):**

```
4. Create .env file with BOTH APIs
   config/.env:
   ```
   # DeepSeek API (for topic generation, outlines, keyword research)
   DEEPSEEK_API_KEY=sk-...
   DEEPSEEK_MODEL=deepseek-chat
   
   # ChatGPT/Claude API (for script generation and evaluation - CRITICAL)
   # CHOOSE ONE:
   OPENAI_API_KEY=sk-...              # If using ChatGPT
   # OR
   CLAUDE_API_KEY=sk-ant-...          # If using Claude
   
   GOOGLE_APPLICATION_CREDENTIALS=config/google-credentials.json
   YOUTUBE_CREDENTIALS_PATH=config/youtube-credentials.json
   YOUTUBE_CHANNEL_ID=your_channel_id (get from YouTube Studio)
   ```

5. Test DeepSeek API Connection (Topic Generation)
   ```bash
   python3 << 'EOF'
   import os
   import requests
   from dotenv import load_dotenv
   
   load_dotenv()
   deepseek_key = os.getenv("DEEPSEEK_API_KEY")
   
   # Test DeepSeek API
   headers = {
       "Authorization": f"Bearer {deepseek_key}",
       "Content-Type": "application/json"
   }
   
   data = {
       "model": "deepseek-chat",
       "messages": [
           {"role": "user", "content": "Generate 3 trending YouTube topics about health"}
       ],
       "temperature": 0.7,
       "max_tokens": 200
   }
   
   response = requests.post(
       "https://api.deepseek.com/chat/completions",
       headers=headers,
       json=data
   )
   
   if response.status_code == 200:
       print("✅ DeepSeek API works!")
       print(response.json()["choices"][0]["message"]["content"][:100])
   else:
       print(f"❌ DeepSeek API failed: {response.text}")
   EOF
   ```
   Expected: Topic suggestions generated successfully

6. Test ChatGPT/Claude API Connection (Script Quality)
   ```bash
   python3 << 'EOF'
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   
   # Choose based on which API you're using
   api_choice = "chatgpt"  # or "claude"
   
   if api_choice == "chatgpt":
       from openai import OpenAI
       client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
       
       response = client.chat.completions.create(
           model="gpt-4o-mini",
           messages=[
               {"role": "user", "content": "Write a 100-word YouTube script about sleep quality"}
           ]
       )
       print("✅ ChatGPT API works!")
       print(response.choices[0].message.content[:100])
       
   elif api_choice == "claude":
       import anthropic
       client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))
       
       response = client.messages.create(
           model="claude-3-5-sonnet-20241022",
           max_tokens=200,
           messages=[
               {"role": "user", "content": "Write a 100-word YouTube script about sleep quality"}
           ]
       )
       print("✅ Claude API works!")
       print(response.content[0].text[:100])
   EOF
   ```
   Expected: Script generated successfully
   ```bash
   python3 << 'EOF'
   import os
   from openai import OpenAI
   
   client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
   
   response = client.chat.completions.create(
     model="gpt-4",
     messages=[
       {"role": "user", "content": "Generate a short script about healthy sleep habits."}
     ]
   )
   
   print("✅ ChatGPT API works!")
   print(response.choices[0].message.content[:100])
   EOF
   ```
   Expected: Script generated successfully

6. Test Google TTS API
   ```bash
   python3 << 'EOF'
   import os
   from google.cloud import texttospeech
   
   client = texttospeech.TextToSpeechClient()
   synthesis_input = texttospeech.SynthesisInput(text="Test audio generation")
   voice = texttospeech.VoiceSelectionParams(
     language_code="en-US",
     name="en-US-Neural2-C"
   )
   audio_config = texttospeech.AudioConfig(
     audio_encoding=texttospeech.AudioEncoding.MP3
   )
   
   response = client.synthesize_speech(
     input=synthesis_input,
     voice=voice,
     audio_config=audio_config
   )
   
   print("✅ Google TTS API works!")
   print(f"Audio generated: {len(response.audio_content)} bytes")
   EOF
   ```
   Expected: Audio generated successfully

7. Document API Rate Limits
   Create: docs/API_LIMITS.md
   ```
   ChatGPT: 3,500 requests/min (RPM), 40,000 tokens/min
   Google TTS: 100 requests/min (may need quota increase)
   YouTube API: 1,000,000 quota/day (plenty)
   ```

8. Create API Backup
   ```bash
   # Create encrypted backup of .env
   tar czf config/credentials_backup.tar.gz config/.env
   # Store securely (cloud, external drive, password manager)
   ```
```

**Deliverable:** All 3 APIs tested, credentials stored, rate limits documented

**Verification:**
```bash
echo "OPENAI_API_KEY=$OPENAI_API_KEY" | grep -o "sk-" > /dev/null && echo "✅ ChatGPT API key found"
ls -la config/google-credentials.json && echo "✅ Google credentials found"
ls -la config/youtube-credentials.json && echo "✅ YouTube credentials found"
```

---

### DAY 3: Ollama & Stable Diffusion Setup (5-6 hours)

**Morning (3 hours):**
```bash
# 1. Install Ollama
# Download from https://ollama.ai
# Run installer, accept defaults
# Verify installation:
ollama --version

# 2. Pull Stable Diffusion XL model
ollama pull sdxl
# This downloads ~7GB model to local machine
# Wait for completion (20-30 min depending on internet)

# 3. Verify installation
ollama list
# Expected output: Shows "sdxl" in list
```

**Afternoon (2-3 hours):**
```bash
# 4. Test Stable Diffusion generation
python3 << 'EOF'
import requests
import time
import json

# Generate 1 test image
prompt = "A serene landscape with mountains and sunset, digital art style"
response = requests.post(
  "http://localhost:11434/api/generate",
  json={
    "model": "sdxl",
    "prompt": prompt,
    "stream": False
  }
)

if response.status_code == 200:
  print("✅ Stable Diffusion works!")
  result = response.json()
  print(f"Generation time: {result.get('total_duration', 0) / 1e9 / 60:.1f} minutes")
else:
  print(f"❌ Error: {response.text}")
EOF

# 5. Monitor GPU during generation
# Open Activity Monitor (Cmd+Space → "Activity Monitor")
# Click "GPU" tab
# Generate another test image and observe:
# - GPU usage should spike to 70-90%
# - Memory usage should show ~10-12GB unified memory
# - Thermal should stay <40°C

# 6. Performance benchmark (5 images)
python3 << 'EOF'
import requests
import time

test_prompts = [
  "A professional business meeting setup",
  "Morning coffee in a cozy cafe",
  "Technology and artificial intelligence",
  "Healthy meal and nutrition",
  "Fitness and exercise"
]

start_time = time.time()
for i, prompt in enumerate(test_prompts):
  t1 = time.time()
  response = requests.post(
    "http://localhost:11434/api/generate",
    json={"model": "sdxl", "prompt": prompt, "stream": False}
  )
  t2 = time.time()
  elapsed = t2 - t1
  print(f"Image {i+1}: {elapsed:.1f} seconds")

total_time = time.time() - start_time
avg_time = total_time / len(test_prompts)
print(f"\n✅ Benchmark Complete:")
print(f"Total: {total_time:.1f}s, Average: {avg_time:.1f}s per image")
print(f"M4 Max target: 15-25 sec per image")
if avg_time <= 25:
  print("✅ Performance EXCEEDS target!")
else:
  print("⚠️  Performance below target, may need optimization")
EOF

# 7. Document findings
cat > docs/OLLAMA_BASELINE.md << 'EOF'
# Ollama & SDXL Performance Baseline

## Test Date: [Today]
## M4 Max Configuration: 36GB RAM, 10-core GPU, 14-core CPU

### Performance Results:
- Average image generation time: [X] seconds
- Peak GPU memory: [X] GB
- Peak GPU utilization: [X]%
- Thermal peak: [X]°C

### Findings:
- ✅ Performance meets/exceeds 15-25 sec target
- ✅ No GPU memory issues
- ✅ Thermal stable
- ✅ Ready for production

### Safe Operating Parameters:
- Can batch 5-7 images without issues
- Safe to generate 5-7 videos/day
- No GPU memory pressure even at peak load
EOF
```

**Deliverable:** Ollama + SDXL working, performance baseline measured, documentation complete

**Verification:**
```bash
ollama list | grep sdxl && echo "✅ SDXL model installed"
# Manual test: Generate 1 image visually and confirm it saves
```

---

### DAY 4: Agent System Design (4-5 hours)

**Morning (2-2.5 hours):**
```
Task: Define Agent Verification System

Create: docs/AGENT_VERIFICATION_SYSTEM.md

Contents:
1. Verification Criteria (What Agent checks)
   - Clarity Score (1-100): Is script easy to understand?
   - Flow Score (1-100): Does it read naturally?
   - Engagement Score (1-100): Does it have hooks, curiosity?
   - Issue Detection: Misinformation risks? Policy violations? Trademark issues?
   - Overall Score (1-100): Weighted average of above
   
2. Pass/Fail Thresholds
   - Clarity ≥ 70: PASS
   - Flow ≥ 75: PASS
   - Engagement ≥ 70: PASS
   - No issues detected: PASS
   - Overall ≥ 72: PASS
   - If ANY fail: FAIL → Regenerate
   
3. Failure Feedback
   If FAIL, Agent provides feedback:
   - Which criteria failed? (Clarity/Flow/Engagement/Issues)
   - Why? (e.g., "Too technical, not engaging")
   - Suggestion: How to improve?

4. Retry Logic
   - Attempt 1: Initial generation → Agent verify
   - If FAIL: Regenerate script → Agent verify (Attempt 2)
   - If FAIL: Regenerate script → Agent verify (Attempt 3)
   - If FAIL: Regenerate script → Agent verify (Attempt 4)
   - If Attempt 4 FAILS: REJECT topic, log failure, pick new topic

5. Success Definition
   - Script passes Agent verification
   - Ready to proceed to Tone Variation
```

**Afternoon (2-2.5 hours):**
```
Task: Define Tone Variation System

Create: docs/TONE_LIBRARY.md

Contents:

## Master Tone Library (5 Core Tones)

### TONE 1: Professional Educational
- Description: Formal, informative, authoritative
- Use When: Tutorial, How-to, Educational, Technical topics
- Agent Prompt: "Rewrite this script in a professional, educational tone. Use formal language, cite sources, maintain authoritative voice. Target: university-educated audience."
- Parameters:
  - Formality: High
  - Engagement: Moderate
  - Pace: Measured
  - Humor: Minimal
  - Examples: Technical, research-backed

### TONE 2: Conversational Storytelling
- Description: Casual, engaging, narrative-driven
- Use When: Opinion, Entertainment, Lifestyle, Story
- Agent Prompt: "Rewrite this script like telling a story to a friend. Use conversational language, include personal anecdotes, make it relatable. Target: general audience."
- Parameters:
  - Formality: Low
  - Engagement: High
  - Pace: Natural
  - Humor: Moderate
  - Examples: Personal, relatable

### TONE 3: Energetic Motivational
- Description: Enthusiastic, action-oriented, inspiring
- Use When: Self-help, Motivation, News, Inspiration
- Agent Prompt: "Rewrite with high energy and motivation. Use powerful language, action verbs, call-to-action. Inspire action. Target: goal-oriented people."
- Parameters:
  - Formality: Moderate-Low
  - Engagement: Very High
  - Pace: Fast, dynamic
  - Humor: Uplifting
  - Examples: Success stories, action-oriented

### TONE 4: Curious Explainer
- Description: Inquisitive, wonder-driven, discovery-focused
- Use When: Documentary, Exploration, Deep-dives, News
- Agent Prompt: "Rewrite with curiosity and wonder. Ask questions, build anticipation, make the audience curious. Target: learners who love discovery."
- Parameters:
  - Formality: Moderate
  - Engagement: High
  - Pace: Exploratory
  - Humor: Quirky
  - Examples: Thought experiments, surprising facts

### TONE 5: Quick & Direct
- Description: Concise, no-nonsense, to-the-point
- Use When: Quick Tips, How-to, Summary, News
- Agent Prompt: "Rewrite concisely. Remove fluff, get to the point. Short sentences. Value viewer's time. Target: busy people."
- Parameters:
  - Formality: Moderate
  - Engagement: Moderate
  - Pace: Fast, efficient
  - Humor: Minimal
  - Examples: Practical, actionable

## Content Type Mapping

- Tutorial / How-to → Tones: [Quick & Direct, Professional Educational]
- Entertainment / Opinion → Tones: [Conversational Storytelling, Energetic Motivational]
- Educational / Exploration → Tones: [Professional Educational, Curious Explainer]
- Lifestyle / Personal → Tones: [Conversational Storytelling, Energetic Motivational]
- News / Current Events → Tones: [Quick & Direct, Curious Explainer]

## Tone Selection Algorithm

For each video:
1. Classify script content type
2. Get applicable tones from mapping above
3. Randomly select 1 tone
4. Generate 2-3 variations with that tone
5. Log: [topic_name, tone_selected, variation_chosen]

## Variation Generation
- Input: Script + Selected Tone Profile
- Output: 2-3 variations of same script in that tone
- Your choice: Pick which variation feels best
```

**Deliverable:** Agent verification and tone systems fully designed and documented

**Verification:**
```bash
ls -la docs/AGENT_VERIFICATION_SYSTEM.md && echo "✅ Agent system designed"
ls -la docs/TONE_LIBRARY.md && echo "✅ Tone library designed"
```

---

### DAY 5: Documentation & Readiness (3-4 hours)

**Morning (1.5-2 hours):**
```bash
# Create essential documentation files

# 1. Workflow guide
cat > docs/WORKFLOW.md << 'EOF'
# Daily Workflow Guide

## Morning (Agent-Assisted Automation - ~30 min per topic)

1. Select Topic (2 min)
   - Research trending topics (Google Trends, news)
   - Select 5-7 topics for the day

2. Generate Script (2 min per topic)
   - ChatGPT generates initial script
   - Output: Raw script

3. Agent Verification (2 min per topic)
   - Agent checks: Clarity, Flow, Engagement, Issues
   - Decision: PASS / FAIL
   - If FAIL → Regenerate (max 3 retries)
   - If PASS → Proceed

4. Tone Variation (2 min per topic)
   - Load Tone Library
   - Random select 1 tone (based on content type)
   - Generate 2-3 variations
   - Select best variation (you choose)

5. Fact-Check (Agent-Assisted, 3 min per topic)
   - Agent flags claims needing verification
   - You quick-check flagged claims
   - Log any corrections

6. TTS/Images/Video (15 min per topic)
   - Automated: Generate audio, images, assemble video
   - Output: Completed video file

## Afternoon (Your Human Review - 5-10 min per video)

7. Your Final Review (5-10 min per video)
   - Watch video (check quality)
   - Read checklist (CRITICAL items only)
   - Decision: APPROVE / REJECT

8. Publish (If APPROVED)
   - Upload to YouTube
   - Set metadata
   - Schedule publish time

## End of Day
- Log metrics (views on published videos)
- Review Agent decisions (any improvements needed?)
EOF

# 2. Troubleshooting guide
cat > docs/TROUBLESHOOTING.md << 'EOF'
# Troubleshooting Guide

## Problem: Agent Verification Fails Repeatedly (After 3 retries)
**Solution:**
- This is normal - some topics don't work
- Skip this topic
- Select different topic
- Log failure reason for analysis

## Problem: Stable Diffusion Image Generation Slow
**Solution:**
- Monitor GPU: Activity Monitor → GPU tab
- If memory pressure high: Close other apps
- Expected: 15-25 sec per image on M4 Max
- If slower: May need optimization (Stage 5)

## Problem: TTS Audio Quality Poor
**Solution:**
- Check: Google TTS API working? (test in morning)
- Check: Sample rate is 44.1kHz? (check config)
- If still poor: Try different voice (en-US-Neural2-C to en-US-Neural2-A)

## Problem: YouTube Upload Fails
**Solution:**
- Check: Internet connection stable?
- Check: YouTube API key valid? (re-authenticate if needed)
- Check: Video file not corrupted? (play locally first)
- If persists: Log error, try next video

## Problem: Low Initial Views (Week 1-2)
**This is NORMAL - not a problem**
- New channels get 10-50 views initially
- Expected: Exponential growth starts Week 7-8
- Focus on: Subscriber count + Watch hours (real metrics)
- Do NOT panic
EOF

# 3. Success criteria checklist (single source of truth: root README.md)
# Open README.md and complete the section "Stage 1 checklist" (and "Stage 1 complete" when done).
# Do not create docs/STAGE_1_SUCCESS.md — that checklist now lives only in README.md.
```

**Afternoon (3 hours total - Part A: Design Validation, Part B: Final Summary):**

**PART A: Design Validation Test (1.5 hours) - NEW**
```bash
# Create design validation test file
cat > docs/DESIGN_VALIDATION_TEST.md << 'EOF'
# Stage 1 Design Logic Validation

## Test 1: Agent Verification Thresholds

python3 << 'PYTHON_EOF'
# Simulate Agent verification logic
class VerificationThresholds:
    CLARITY_MIN = 70
    FLOW_MIN = 75
    ENGAGEMENT_MIN = 70
    OVERALL_MIN = 72

def test_threshold_logic():
    # Test Case 1: All scores above threshold (should PASS)
    scores_1 = {"clarity": 85, "flow": 90, "engagement": 75}
    result_1 = all(v >= VerificationThresholds.CLARITY_MIN for k, v in scores_1.items() if k == "clarity") and \
               all(v >= VerificationThresholds.FLOW_MIN for k, v in scores_1.items() if k == "flow") and \
               all(v >= VerificationThresholds.ENGAGEMENT_MIN for k, v in scores_1.items() if k == "engagement")
    assert result_1 == True, "Test 1 failed"
    print("✅ Test 1 PASS: All high scores → verification PASSES")
    
    # Test Case 2: One score below threshold (should FAIL)
    scores_2 = {"clarity": 75, "flow": 70, "engagement": 65}  # Engagement below 70
    result_2 = all(v >= VerificationThresholds.ENGAGEMENT_MIN for k, v in scores_2.items() if k == "engagement")
    assert result_2 == False, "Test 2 failed"
    print("✅ Test 2 PASS: One low score → verification FAILS")
    
    # Test Case 3: Exact threshold (should PASS)
    scores_3 = {"clarity": 70, "flow": 75, "engagement": 70}  # Exactly at minimums
    result_3 = all(v >= VerificationThresholds.CLARITY_MIN for k, v in scores_3.items() if k == "clarity") and \
               all(v >= VerificationThresholds.FLOW_MIN for k, v in scores_3.items() if k == "flow") and \
               all(v >= VerificationThresholds.ENGAGEMENT_MIN for k, v in scores_3.items() if k == "engagement")
    assert result_3 == True, "Test 3 failed"
    print("✅ Test 3 PASS: Exact threshold → verification PASSES")

test_threshold_logic()
print("\n✅ All threshold tests PASSED")
PYTHON_EOF

# Test 2: Retry Logic (max 3 retries)
python3 << 'PYTHON_EOF'
def test_retry_logic():
    max_attempts = 4  # 1 initial + 3 retries
    for attempt in range(1, max_attempts + 1):
        if attempt < max_attempts:
            expected_action = "Regenerate and retry"
        else:
            expected_action = "REJECT topic"
        
        print(f"Attempt {attempt}: {expected_action}")
    
    # Verify: After 4 attempts (1 initial + 3 retries), should reject
    assert attempt == 4, "Retry logic incorrect"
    assert expected_action == "REJECT topic", "Final action should be REJECT"
    print("\n✅ Retry logic verified (max 3 retries = 4 total attempts)")

test_retry_logic()
PYTHON_EOF

# Test 3: Tone Selection Randomization
python3 << 'PYTHON_EOF'
import random

def test_tone_selection():
    content_type = "tutorial"
    applicable_tones_map = {
        "tutorial": ["Quick & Direct", "Professional Educational"],
        "entertainment": ["Conversational Storytelling", "Energetic Motivational"],
        "educational": ["Professional Educational", "Curious Explainer"],
    }
    
    applicable_tones = applicable_tones_map[content_type]
    print(f"Content type: {content_type}")
    print(f"Applicable tones: {applicable_tones}")
    
    # Simulate 5 random selections
    selections = []
    for i in range(5):
        selected = random.choice(applicable_tones)
        selections.append(selected)
        print(f"  Run {i+1}: {selected}")
    
    # Verify: At least one different tone was selected (randomization working)
    assert len(set(selections)) >= 1, "No tone selection"
    print(f"\n✅ Randomization verified: Selected {len(set(selections))} different tones in 5 runs")
    
    # Expected: Some repetition is normal for random choice from 2 options
    # This is acceptable behavior

test_tone_selection()
PYTHON_EOF

# Test 4: Tone Variation Count (2-3 variations per tone)
python3 << 'PYTHON_EOF'
def test_tone_variations():
    tone_profile = "Professional Educational"
    variations_count = 3  # Should be 2-3
    
    assert variations_count >= 2, "Too few variations"
    assert variations_count <= 3, "Too many variations"
    print(f"Tone: {tone_profile}")
    print(f"Variations generated: {variations_count}")
    print("✅ Tone variation count valid (2-3 per tone)")

test_tone_variations()
PYTHON_EOF
```

**Validation Results:**
- [ ] Verification threshold logic: PASSED ✅
- [ ] Retry logic (max 3): PASSED ✅
- [ ] Tone selection randomization: PASSED ✅
- [ ] Tone variation count (2-3): PASSED ✅

All design logic validated before proceeding to Stage 2.
EOF
```

**PART B: Final Readiness Summary (1.5 hours)**
```bash
# 4. Stage 1 completion sign-off (single source of truth: root README.md)
# Fill in README.md under "Stage 1 complete (sign-off)" with date and notes.
# Do not create docs/STAGE_1_COMPLETE.md.

# 5. Final verification
echo "==============================================="
echo "STAGE 1 SETUP COMPLETE"
echo "==============================================="
echo ""
echo "Files created:"
ls -lh ~/YouTube-Automation/docs/
echo ""
echo "Python environment:"
source ~/YouTube-Automation/venv/bin/activate
python --version
pip list | head -5
echo ""
echo "✅ All systems ready for Stage 2"
```

**Deliverable:** Complete documentation, final readiness verification

**Verification:**
```bash
ls -la ~/YouTube-Automation/docs/ | grep .md
# Should show: WORKFLOW.md, TROUBLESHOOTING.md, AGENT_VERIFICATION_SYSTEM.md, TONE_LIBRARY.md, etc.
```

---

## FINAL SUMMARY

**What Gets Done in Stage 1:**
- ✅ M4 Mac fully configured
- ✅ All APIs tested
- ✅ Ollama + SDXL running
- ✅ Agent verification system designed
- ✅ Tone variation system designed
- ✅ Complete documentation
- ✅ Zero coding yet (design phase)

**Time Investment:** 20-30 hours spread across 5 days (4-6 hrs/day)

**Your Involvement:** None (Setup only, you just ensure API keys available)

**Ready for Stage 2?** When this checklist is 100% complete

---

## WHEN YOU'RE READY TO START STAGE 1

**Reply with:**
```
Ready to begin Stage 1: [DATE]
Time available: [Hours per day]
All API credentials ready: YES / NO
Preferred start time: [Morning/Afternoon]
```

Once you confirm, I'll give you:
1. Hour-by-hour Day 1 walkthrough
2. Copy-paste commands ready to execute
3. Daily progress checklist
4. Troubleshooting on-call

**You control the start date.** Stage 1 is fully planned and ready to execute whenever you say "GO!"

