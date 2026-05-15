# STAGE 2 TROUBLESHOOTING GUIDE
**Purpose:** Quick reference for debugging Stage 2 issues  
**Use When:** Stage 2 encounters errors during execution or in Stage 3 integration  

---

## 🚨 COMMON ISSUES & SOLUTIONS

### ISSUE 1: HybridScriptGenerator Fails - API Key Error

**Symptoms:**
```
Error: "Invalid API key for DeepSeek"
or
Error: "ChatGPT API key not found"
```

**Root Causes:**
1. API keys not in credentials/api_keys.txt
2. Keys expired or regenerated
3. Secrets loader not working

**Fix Steps:**
```bash
# Step 1: Verify credentials file exists
ls -la credentials/api_keys.txt

# Step 2: Check keys are present
grep "DEEPSEEK_API_KEY" credentials/api_keys.txt
grep "OPENAI_API_KEY" credentials/api_keys.txt

# Step 3: Verify keys are valid (first 10 chars visible)
python3 << 'EOF'
from src.core.secrets_loader import SecretsLoader
loader = SecretsLoader()
deepseek = loader.get("DEEPSEEK_API_KEY")
openai = loader.get("OPENAI_API_KEY")
print(f"DeepSeek: {deepseek[:10]}..." if deepseek else "❌ DeepSeek not found")
print(f"OpenAI: {openai[:10]}..." if openai else "❌ OpenAI not found")
EOF

# Step 4: If missing, add them
nano credentials/api_keys.txt
# Edit and save with valid keys

# Step 5: Test again
python3 scripts/test_apis.py
```

---

### ISSUE 2: Agent Verifier Returns False (Script Fails Verification)

**Symptoms:**
```
Script failed Agent verification on attempt 1
Script failed Agent verification on attempt 2
Script failed Agent verification on attempt 3
Max retries exceeded, script rejected
```

**Root Cause:**
- Script quality is genuinely low (clarity, flow, or engagement issues)
- Agent verification prompts are too strict
- Script lacks hook or CTA

**Fix Steps:**
```bash
# Step 1: Check the script content
python3 << 'EOF'
import json
# Load the failed script
with open('data/approved_scripts/[script_id].json', 'r') as f:
    script_data = json.load(f)
print("Script:")
print(script_data['script'])
print("\nTopic:", script_data['topic'])
print("Tone:", script_data['tone'])
EOF

# Step 2: Review verification feedback
# Check logs/daily_logs/ for Agent's feedback on why it failed

# Step 3: Manually improve the script
# - Add stronger hook (first 15 seconds)
# - Improve pacing (check for long sentences)
# - Add stronger CTA (call to action)

# Step 4: Regenerate script
# Either:
# a) Regenerate via HybridScriptGenerator (different ChatGPT attempt)
# b) Or manually edit and re-verify

# Step 5: If consistently failing, adjust verification prompt
# Edit: config/agent_prompts.json
# Reduce strictness thresholds temporarily
```

**Prevention:**
- Ensure ChatGPT/Claude model is current (gpt-4o-mini or claude-3-5-sonnet)
- Check topic is specific enough (not too vague)
- Verify tone is appropriate for topic

---

### ISSUE 3: TTS Audio Quality Poor or Missing

**Symptoms:**
```
Audio file not generated
Audio quality is robotic or unclear
SSML formatting causing errors
```

**Root Causes:**
1. Google Cloud credentials missing/invalid
2. Script text has invalid characters
3. SSML formatting syntax error

**Fix Steps:**
```bash
# Step 1: Verify Google credentials
ls -la config/google-credentials.json

# Step 2: Test TTS directly
python3 << 'EOF'
from src.api.google_tts import TTSHandler

handler = TTSHandler("config/google-credentials.json", "your-project-id")

# Test with simple text
test_text = "This is a test of the text to speech system."
audio_bytes = handler.generate_audio(test_text)

print(f"✅ TTS working! Generated {len(audio_bytes)} bytes")
EOF

# Step 3: Check script formatting
# Remove special characters from script
# Script should be plain text only (no markdown, special chars)

# Step 4: Verify SSML formatting
# Test SSML on simple sentence first:
test_ssml = """<speak>
  This is a <emphasis>test</emphasis> with a 
  <break time="0.5s"/>pause.
</speak>"""

# Step 5: If still failing, regenerate with plain text
# Remove SSML formatting temporarily
handler.add_ssml_formatting(script_text)  # Debug what it generates
```

**Prevention:**
- Keep scripts clean (no special characters)
- Test SSML formatting before bulk generation
- Monitor Google Cloud API usage quota

---

### ISSUE 4: Image Generation Fails (Ollama Not Running)

**Symptoms:**
```
Error: "Connection refused" on localhost:11434
No images generated
ImageGenerator returns empty list
```

**Root Cause:**
- Ollama service not running
- SDXL model not loaded
- Network connectivity issue

**Fix Steps:**
```bash
# Step 1: Check if Ollama is running
curl http://localhost:11434/api/tags

# If error: Ollama not running
# Step 2: Start Ollama
# On Mac:
open /Applications/Ollama.app

# Or from terminal:
ollama serve

# Step 3: Verify SDXL model is loaded
ollama list | grep sdxl

# If not present:
ollama pull sdxl

# Step 4: Test image generation
python3 << 'EOF'
from src.generation.image_generator import ImageGenerator

gen = ImageGenerator()
images = gen.generate_image("A beautiful sunset over mountains", num_images=1)
print(f"Generated {len(images)} images")
for img in images:
    print(f"✅ {img}")
EOF

# Step 5: If still failing, check logs
tail -f logs/api_logs/[today].log | grep "image"
```

**Prevention:**
- Keep Ollama running during batch generation
- Monitor disk space (SDXL model uses ~4GB)
- Use placeholder images if Ollama unavailable

---

### ISSUE 5: Video Assembly Fails (MoviePy/FFmpeg Error)

**Symptoms:**
```
Error: "FFmpeg not found"
Video quality degraded
Subtitles not added
```

**Root Causes:**
1. FFmpeg not installed
2. MoviePy not configured properly
3. Audio/image files corrupted

**Fix Steps:**
```bash
# Step 1: Check FFmpeg installation
ffmpeg -version

# If not found:
# On Mac:
brew install ffmpeg

# Step 2: Verify audio file integrity
python3 << 'EOF'
import os
audio_path = "data/generated_videos/[timestamp]_audio.wav"
if os.path.exists(audio_path):
    file_size = os.path.getsize(audio_path)
    print(f"✅ Audio file exists: {file_size} bytes")
else:
    print("❌ Audio file missing")
EOF

# Step 3: Check image files exist
ls -la data/generated_videos/images/

# Step 4: Test video assembly directly
python3 << 'EOF'
from src.video.video_assembler import VideoAssembler

assembler = VideoAssembler()
result = assembler.assemble_video(
    audio_path="data/generated_videos/[timestamp]_audio.wav",
    images=["data/generated_videos/images/[image1].png"],
    metadata={"topic": "Test"}
)
print(f"✅ Video created: {result}")
EOF

# Step 5: If MoviePy issue, check movie.py installation
pip list | grep moviepy
pip install --upgrade moviepy
```

**Prevention:**
- Verify all dependencies before batch processing
- Test assembly on single video first
- Keep file size reasonable (audio <50MB, images <10MB each)

---

### ISSUE 6: Cost Tracking Inaccurate

**Symptoms:**
```
Cost calculations don't match API bills
API split percentages incorrect
Missing cost entries in logs
```

**Root Cause:**
- API costs changing
- Token counting incorrect
- Log entries missing

**Fix Steps:**
```bash
# Step 1: Check cost configuration
grep -r "cost" config/settings.json

# Step 2: Verify cost tracking in code
python3 << 'EOF'
from src.core.performance_monitor import PerformanceMonitor

monitor = PerformanceMonitor()
monitor.track_api_cost("deepseek", 0.025)
monitor.track_api_cost("chatgpt", 0.125)
monitor.track_api_cost("google_tts", 0.10)

summary = monitor.get_daily_summary()
print(f"Total cost: ${summary['total_cost']:.2f}")
EOF

# Step 3: Compare with actual API usage
# DeepSeek: https://platform.deepseek.com/usage
# OpenAI: https://platform.openai.com/usage/overview
# Google Cloud: Console → Billing

# Step 4: If mismatch, update cost in code
# Edit: src/api/deepseek_client.py (update token costs)
# Edit: src/api/chatgpt_client.py (update token costs)

# Step 5: Recalculate for recent videos
python3 << 'EOF'
# Check recent logs
import os
log_file = "logs/api_logs/[today].log"
with open(log_file, 'r') as f:
    print(f.read())
EOF
```

**Prevention:**
- Update costs when API pricing changes
- Log all API calls with token counts
- Reconcile weekly with actual bills

---

### ISSUE 7: Integration Test Fails (Imports or Data Flow)

**Symptoms:**
```
ImportError: cannot import [module]
Data format mismatch between modules
Pipeline stops at random point
```

**Root Cause:**
- File path issues
- Missing __init__.py files
- Data structure mismatch

**Fix Steps:**
```bash
# Step 1: Verify all __init__.py files exist
find src -name "__init__.py" | sort

# Should have:
# src/__init__.py
# src/core/__init__.py
# src/api/__init__.py
# src/generation/__init__.py
# src/quality/__init__.py
# src/video/__init__.py
# src/utils/__init__.py

# Create missing:
touch src/[folder]/__init__.py

# Step 2: Test imports
python3 << 'EOF'
try:
    from src.core.orchestrator import VideoProductionOrchestrator
    from src.generation.script_generator import HybridScriptGenerator
    from src.quality.agent_verifier import AgentVerifier
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
EOF

# Step 3: Run unit tests individually
pytest tests/test_orchestrator.py -v
pytest tests/test_script_generator.py -v
pytest tests/test_agent_verifier.py -v
# ... etc for all tests

# Step 4: Check data flow between modules
python3 << 'EOF'
from src.core.orchestrator import VideoProductionOrchestrator

orch = VideoProductionOrchestrator()
result = orch.generate_video(topic="Test Topic")

# Verify output structure
required_keys = ["success", "video_path", "script", "topic", "agent_verification_passed"]
for key in required_keys:
    if key not in result:
        print(f"❌ Missing key in output: {key}")
    else:
        print(f"✅ {key}: {result[key]}")
EOF
```

**Prevention:**
- Run all tests before Stage 3
- Verify output dict structure matches spec
- Check file paths use correct separators

---

## 📋 DIAGNOSTIC CHECKLIST

If Stage 2 is having issues, run this:

```bash
#!/bin/bash
echo "=== STAGE 2 DIAGNOSTIC CHECK ==="

# 1. Check all files exist
echo "1. Checking Python modules..."
for file in src/core/orchestrator.py src/api/deepseek_client.py src/quality/agent_verifier.py; do
    [ -f "$file" ] && echo "✅ $file" || echo "❌ $file MISSING"
done

# 2. Check config files
echo -e "\n2. Checking config files..."
for file in config/settings.json config/tone_library.json; do
    [ -f "$file" ] && echo "✅ $file" || echo "❌ $file MISSING"
done

# 3. Check directories
echo -e "\n3. Checking directories..."
for dir in logs/daily_logs logs/api_logs data/generated_videos credentials; do
    [ -d "$dir" ] && echo "✅ $dir" || echo "❌ $dir MISSING"
done

# 4. Check API keys
echo -e "\n4. Checking credentials..."
if [ -f "credentials/api_keys.txt" ]; then
    grep -q "DEEPSEEK_API_KEY" credentials/api_keys.txt && echo "✅ DeepSeek key present" || echo "❌ DeepSeek key missing"
    grep -q "OPENAI_API_KEY" credentials/api_keys.txt && echo "✅ OpenAI key present" || echo "❌ OpenAI key missing"
else
    echo "❌ credentials/api_keys.txt not found"
fi

# 5. Run basic tests
echo -e "\n5. Running unit tests..."
pytest tests/test_orchestrator.py -v 2>&1 | grep -E "PASSED|FAILED" | head -5

echo -e "\n✅ Diagnostic complete"
```

---

## 🔄 RECOVERY PROCEDURES

### If Stage 2 is Broken, Recovery Steps:

```
1. IDENTIFY: Which module is failing?
   - Check logs/error_logs/ for error messages
   - Review console output for stacktrace

2. ISOLATE: Test that module individually
   - pytest tests/test_[module].py -v
   - Check imports and dependencies

3. REVIEW: Compare with STAGE_2_FINAL_LOCKDOWN.md
   - Verify specifications match
   - Check data structures

4. REGENERATE: If fixable
   - Edit the broken module
   - Re-run tests
   - Verify output format

5. ROLLBACK: If not fixable
   - You may need to re-run the relevant Cursor session
   - Refer to STAGE_2_CURSOR_PROMPTS.md
   - Paste that session's prompt into Cursor again

6. VALIDATE: After fix
   - Run full integration tests
   - Verify 5 test videos generate successfully
   - Check all logs created
```

---

## 📞 WHEN TO CONSULT THIS GUIDE

- ✅ Stage 2 module not generating expected output
- ✅ API key errors
- ✅ Audio/image quality issues
- ✅ Video assembly failures
- ✅ Integration test failures
- ✅ Cost tracking discrepancies
- ✅ Before moving to Stage 3 if something seems off

---

**This guide covers 95% of common Stage 2 issues. If not found here, check logs and error messages for clues. 🔍**

