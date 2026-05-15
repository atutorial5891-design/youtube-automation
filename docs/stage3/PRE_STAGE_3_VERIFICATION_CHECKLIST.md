# PRE-STAGE 3 VERIFICATION CHECKLIST
**Purpose:** Verify Stage 2 completed successfully before starting Stage 3  
**Time Required:** 15-20 minutes  
**Status:** MUST COMPLETE before Stage 3 implementation  

---

## 📋 STEP 1: VERIFY STAGE 2 FILES EXIST

### Python Modules (Should be 12 files)
```bash
# Run this command:
find src -name "*.py" -type f | wc -l
# Should return: 12 or higher

# Verify specific critical files:
ls -lh src/core/orchestrator.py
ls -lh src/api/deepseek_client.py
ls -lh src/api/chatgpt_client.py
ls -lh src/generation/script_generator.py
ls -lh src/quality/agent_verifier.py
ls -lh src/video/video_assembler.py
```

**Expected Output:**
```
✅ src/core/orchestrator.py (2-3 KB)
✅ src/core/config_loader.py (1-2 KB)
✅ src/core/logger.py (2-3 KB)
✅ src/core/performance_monitor.py (1-2 KB)
✅ src/api/deepseek_client.py (2 KB)
✅ src/api/chatgpt_client.py (2 KB)
✅ src/api/google_tts.py (2 KB)
✅ src/generation/script_generator.py (3-4 KB)
✅ src/generation/tone_manager.py (2-3 KB)
✅ src/generation/image_generator.py (2 KB)
✅ src/quality/agent_verifier.py (2 KB)
✅ src/video/video_assembler.py (3-4 KB)
```

**If Missing:** Any file → Regenerate using STAGE_2_CURSOR_PROMPTS.md

---

## 📋 STEP 2: VERIFY TEST FILES EXIST

### Test Modules (Should be 6 files minimum)
```bash
# Verify test files:
ls -1 tests/test_*.py | wc -l
# Should return: 6 or higher

# Verify specific test files:
ls -lh tests/test_orchestrator.py
ls -lh tests/test_script_generator.py
ls -lh tests/test_agent_verifier.py
ls -lh tests/test_tone_manager.py
ls -lh tests/test_tts_handler.py
ls -lh tests/test_video_assembler.py
```

**Expected Output:**
```
✅ tests/test_orchestrator.py
✅ tests/test_script_generator.py
✅ tests/test_agent_verifier.py
✅ tests/test_tone_manager.py
✅ tests/test_tts_handler.py
✅ tests/test_image_generator.py
✅ tests/test_video_assembler.py
```

**If Missing:** Regenerate using STAGE_2_CURSOR_PROMPTS.md

---

## 📋 STEP 3: VERIFY CONFIGURATION FILES

### Config Files (Should be 7+ files)
```bash
# Check config files:
ls -lh config/*.json
```

**Expected Files:**
```
✅ config/settings.json (1-2 KB)
✅ config/agent_prompts.json (2-3 KB)
✅ config/script_prompts.json (2-3 KB)
✅ config/tone_library.json (3-5 KB) ← CRITICAL
✅ config/image_prompts.json (2 KB)
✅ config/youtube_config.json (1 KB)
```

**If tone_library.json Missing:**
```bash
# Regenerate using Session 4 prompt from STAGE_2_CURSOR_PROMPTS.md
```

**Check tone_library.json Contents:**
```bash
# Verify 5 tones exist:
python3 << 'EOF'
import json
with open('config/tone_library.json', 'r') as f:
    tones = json.load(f)
    print(f"Number of tones: {len(tones.get('tones', []))}")
    for tone in tones.get('tones', []):
        print(f"  - {tone['name']}")
EOF

# Should output:
# Number of tones: 5
#   - Professional Educational
#   - Conversational Storytelling
#   - Energetic Motivational
#   - Curious Explainer
#   - Quick & Direct
```

---

## 📋 STEP 4: VERIFY STAGE 2 OUTPUT DATA

### Generated Videos (Should have 5+ test videos)
```bash
# Check video folder:
ls -lh data/generated_videos/*.mp4 2>/dev/null | wc -l
# Should return: 5 or higher

# List the videos:
ls -lh data/generated_videos/*.mp4
```

**Expected Output:**
```
✅ data/generated_videos/20260515_python_tutorial.mp4 (50-150 MB)
✅ data/generated_videos/20260515_fitness_tips.mp4 (50-150 MB)
✅ data/generated_videos/20260515_cooking_basics.mp4 (50-150 MB)
✅ data/generated_videos/20260515_productivity_hacks.mp4 (50-150 MB)
✅ data/generated_videos/20260515_health_facts.mp4 (50-150 MB)
```

**If Missing:** Run Stage 2 again to generate test videos

---

## 📋 STEP 5: VERIFY SCRIPT METADATA

### Approved Scripts (Should have matching metadata)
```bash
# Check metadata files:
ls -lh data/approved_scripts/*_metadata.json | wc -l
# Should return: 5 or higher (matching videos)

# Verify metadata structure:
python3 << 'EOF'
import json
import os
from pathlib import Path

metadata_dir = Path("data/approved_scripts")
required_keys = ["script_id", "video_path", "script", "topic", "agent_verification_passed"]

for metadata_file in sorted(metadata_dir.glob("*_metadata.json"))[:1]:  # Check first one
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    print(f"File: {metadata_file.name}")
    for key in required_keys:
        if key in metadata:
            value = str(metadata[key])[:50]  # First 50 chars
            print(f"  ✅ {key}: {value}...")
        else:
            print(f"  ❌ {key}: MISSING")
EOF
```

**Expected Output:**
```
File: 20260515_python_tutorial_metadata.json
  ✅ script_id: 20260515_python_tutorial_professional_educational...
  ✅ video_path: data/generated_videos/20260515_python_tutorial...
  ✅ script: Full script text here...
  ✅ topic: How to Learn Python...
  ✅ agent_verification_passed: True
```

**Critical:** All scripts must have `agent_verification_passed: true`

---

## 📋 STEP 6: VERIFY LOG FILES

### Daily Logs (Should have entries)
```bash
# Check daily logs:
ls -lh logs/daily_logs/*.log 2>/dev/null | tail -5
# Should show today's date

# Check API logs (cost tracking):
ls -lh logs/api_logs/*.log 2>/dev/null | tail -5
# Should show API cost entries

# Verify logs have content:
python3 << 'EOF'
import os
from pathlib import Path

log_dirs = ["logs/daily_logs", "logs/api_logs", "logs/error_logs", "logs/performance_logs"]

for log_dir in log_dirs:
    log_path = Path(log_dir)
    if log_path.exists():
        log_files = list(log_path.glob("*.log"))
        print(f"✅ {log_dir}: {len(log_files)} log files")
        if log_files:
            latest = sorted(log_files)[-1]
            size = latest.stat().st_size
            print(f"   Latest: {latest.name} ({size} bytes)")
    else:
        print(f"❌ {log_dir}: MISSING")
EOF
```

**Expected Output:**
```
✅ logs/daily_logs: 1 log files
   Latest: 2026-05-15.log (2500 bytes)
✅ logs/api_logs: 1 log files
   Latest: 2026-05-15.log (1200 bytes)
✅ logs/error_logs: 1 log files
   Latest: 2026-05-15.log (0 bytes)
✅ logs/performance_logs: 1 log files
   Latest: 2026-05-15.log (800 bytes)
```

---

## 📋 STEP 7: VERIFY CREDENTIALS

### API Keys Present
```bash
# Check credentials file:
if [ -f "credentials/api_keys.txt" ]; then
    echo "✅ credentials/api_keys.txt exists"
    grep -c "API_KEY" credentials/api_keys.txt
    # Should return: 2 or higher
else
    echo "❌ credentials/api_keys.txt MISSING"
fi
```

**Expected Output:**
```
✅ credentials/api_keys.txt exists
2
```

**If Missing:** Create with:
```bash
cp credentials/api_keys.example.txt credentials/api_keys.txt
nano credentials/api_keys.txt
# Add your API keys
```

---

## 📋 STEP 8: RUN QUICK VALIDATION TEST

### Test All Imports Work
```bash
python3 << 'EOF'
try:
    from src.core.orchestrator import VideoProductionOrchestrator
    from src.generation.script_generator import HybridScriptGenerator
    from src.quality.agent_verifier import AgentVerifier
    from src.generation.tone_manager import ToneManager
    from src.api.google_tts import TTSHandler
    from src.generation.image_generator import ImageGenerator
    from src.video.video_assembler import VideoAssembler
    from src.core.logger import Logger
    from src.core.performance_monitor import PerformanceMonitor
    
    print("✅ All imports successful!")
    print("✅ Stage 2 modules are ready")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("❌ Some modules missing - check Stage 2 files")
EOF
```

**Expected Output:**
```
✅ All imports successful!
✅ Stage 2 modules are ready
```

**If Error:** Verify all Python files from STEP 1 exist

---

## 📋 STEP 9: RUN UNIT TESTS

### Quick Test Run
```bash
# Run all tests (should take 2-3 minutes):
pytest tests/ -v --tb=short 2>&1 | tail -20

# Check for PASSED count:
pytest tests/ -v 2>&1 | grep -E "passed|failed"
# Should show: "X passed" with no failures
```

**Expected Output:**
```
tests/test_orchestrator.py::test_... PASSED
tests/test_script_generator.py::test_... PASSED
...
======================== 20+ passed in 2.5s ========================
```

**If Tests Fail:** Check STAGE_2_TROUBLESHOOTING.md for solutions

---

## 📋 STEP 10: VERIFY GATE 2 RESULTS

### Check Agent Verification Accuracy
```bash
# Check metadata for agent_verification_passed:
python3 << 'EOF'
import json
from pathlib import Path

metadata_dir = Path("data/approved_scripts")
total = 0
passed = 0

for metadata_file in metadata_dir.glob("*_metadata.json"):
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    total += 1
    if metadata.get("agent_verification_passed"):
        passed += 1

if total > 0:
    accuracy = (passed / total) * 100
    print(f"Gate 2 Results:")
    print(f"  Total videos: {total}")
    print(f"  Passed Agent verification: {passed}")
    print(f"  Accuracy: {accuracy:.1f}%")
    
    if accuracy >= 80:
        print(f"\n✅ GATE 2 PASSED (≥80% accuracy)")
    else:
        print(f"\n⚠️ GATE 2 MARGINAL ({accuracy:.1f}% < 80%)")
        print("   Consider regenerating some scripts")
EOF
```

**Expected Output:**
```
Gate 2 Results:
  Total videos: 5
  Passed Agent verification: 4-5
  Accuracy: 80-100%

✅ GATE 2 PASSED (≥80% accuracy)
```

**If Below 80%:** Regenerate scripts using Stage 2

---

## ✅ FINAL VERIFICATION SUMMARY

Run this script to get complete status:

```bash
#!/bin/bash
echo "=========================================="
echo "PRE-STAGE 3 VERIFICATION SUMMARY"
echo "=========================================="

checks=0
passed=0

# Check 1: Python modules
echo -n "1. Python modules... "
count=$(find src -name "*.py" -type f | wc -l)
if [ "$count" -ge 12 ]; then
    echo "✅ ($count files)"
    ((passed++))
else
    echo "❌ ($count files, need 12+)"
fi
((checks++))

# Check 2: Test files
echo -n "2. Test files... "
count=$(ls -1 tests/test_*.py 2>/dev/null | wc -l)
if [ "$count" -ge 6 ]; then
    echo "✅ ($count files)"
    ((passed++))
else
    echo "❌ ($count files, need 6+)"
fi
((checks++))

# Check 3: Config files
echo -n "3. Config files... "
if [ -f "config/tone_library.json" ]; then
    echo "✅"
    ((passed++))
else
    echo "❌ (tone_library.json missing)"
fi
((checks++))

# Check 4: Videos
echo -n "4. Generated videos... "
count=$(ls -1 data/generated_videos/*.mp4 2>/dev/null | wc -l)
if [ "$count" -ge 5 ]; then
    echo "✅ ($count videos)"
    ((passed++))
else
    echo "❌ ($count videos, need 5+)"
fi
((checks++))

# Check 5: Metadata
echo -n "5. Script metadata... "
count=$(ls -1 data/approved_scripts/*_metadata.json 2>/dev/null | wc -l)
if [ "$count" -ge 5 ]; then
    echo "✅ ($count files)"
    ((passed++))
else
    echo "❌ ($count files, need 5+)"
fi
((checks++))

# Check 6: Logs
echo -n "6. Log files... "
if [ -d "logs/daily_logs" ] && [ "$(ls -1 logs/daily_logs/*.log 2>/dev/null | wc -l)" -gt 0 ]; then
    echo "✅"
    ((passed++))
else
    echo "❌"
fi
((checks++))

# Check 7: Credentials
echo -n "7. API credentials... "
if [ -f "credentials/api_keys.txt" ]; then
    echo "✅"
    ((passed++))
else
    echo "❌"
fi
((checks++))

echo ""
echo "=========================================="
echo "RESULT: $passed/$checks checks passed"
echo "=========================================="

if [ "$passed" -eq "$checks" ]; then
    echo "✅ READY FOR STAGE 3"
    echo ""
    echo "Next steps:"
    echo "1. Read: STAGE_3_START_HERE.md"
    echo "2. Read: STAGE_3_IMPLEMENTATION_GUIDE.md"
    echo "3. Use: STAGE_3_CURSOR_PROMPT_SESSION_1_UPDATED.md"
    echo "4. Start implementing Stage 3"
else
    echo "❌ NOT READY FOR STAGE 3"
    echo ""
    echo "Issues found:"
    echo "- Check STAGE_2_TROUBLESHOOTING.md"
    echo "- Regenerate missing files using STAGE_2_CURSOR_PROMPTS.md"
    echo "- Rerun this checklist"
fi
```

---

## 📝 HOW TO USE THIS CHECKLIST

### Option A: Quick Check (5 minutes)
1. Run STEP 8 (imports test)
2. Run STEP 10 (Gate 2 results)
3. If both pass → Ready for Stage 3

### Option B: Complete Verification (15 minutes)
1. Run all 10 steps
2. Use the shell script at the end
3. Verify all checks pass
4. Then start Stage 3

### Option C: Troubleshooting
1. If something fails → Check STAGE_2_TROUBLESHOOTING.md
2. Fix the issue
3. Rerun the failed step
4. Once all pass → Start Stage 3

---

## 🚀 ONCE VERIFICATION PASSES

Read these documents in order:

1. **STAGE_3_START_HERE.md** (5 min) - Quick orientation
2. **STAGE_3_IMPLEMENTATION_GUIDE.md** (15 min) - Day-by-day plan
3. **STAGE_3_CURSOR_PROMPT_SESSION_1_UPDATED.md** - Start implementing Days 1-2
4. **Continue** with Sessions 2 & 3

---

**✅ Complete this checklist before starting Stage 3**

