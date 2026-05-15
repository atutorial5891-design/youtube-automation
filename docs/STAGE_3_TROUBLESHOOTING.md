# STAGE 3 TROUBLESHOOTING GUIDE
**Purpose:** Quick fixes for common Stage 3 issues  
**Date:** May 15, 2026  
**Status:** Complete troubleshooting guide

---

## 🔧 BEFORE YOU TROUBLESHOOT

Run this diagnostic first:
```bash
#!/bin/bash
echo "=== STAGE 3 DIAGNOSTICS ==="

echo ""
echo "Files:"
echo "  Mock metadata: $(ls data/approved_scripts/*_metadata.json 2>/dev/null | wc -l)/5"
echo "  Mock videos: $(ls data/generated_videos/*.mp4 2>/dev/null | wc -l)/5"
echo "  Config dir: $([ -d config ] && echo '✅' || echo '❌')"
echo "  Logs dir: $([ -d logs ] && echo '✅' || echo '❌')"

echo ""
echo "Python:"
echo "  pytest: $(python3 -c "import pytest; print('✅')" 2>/dev/null || echo '❌')"
echo "  json: $(python3 -c "import json; print('✅')" 2>/dev/null || echo '❌')"
echo "  pathlib: $(python3 -c "from pathlib import Path; print('✅')" 2>/dev/null || echo '❌')"

echo ""
echo "API:"
echo "  API key file: $([ -f credentials/api_keys.txt ] && echo '✅' || echo '❌')"
```

---

## 🐛 COMMON ISSUES & SOLUTIONS

### **ISSUE 1: "ModuleNotFoundError: No module named 'src.api.chatgpt_client'"**

**Symptom:**
```
ModuleNotFoundError: No module named 'src.api.chatgpt_client'
```

**Cause:**
- Stage 2 modules not built yet
- Wrong directory structure

**Solution:**

✅ **Option A: Build Stage 2 First**
```bash
# Stage 3 depends on Stage 2 modules
# You must complete Stage 2 before Stage 3

# Check if Stage 2 files exist:
ls -lh src/api/chatgpt_client.py
ls -lh src/api/deepseek_client.py
ls -lh src/core/logger.py

# If missing, run STAGE_2_CURSOR_PROMPTS.md first
echo "Run Stage 2 implementation before Stage 3"
```

✅ **Option B: Create Stub Modules (Temporary)**
```python
# If you want to test Stage 3 structure without Stage 2:
# Create temporary stubs in src/api/

# File: src/api/chatgpt_client.py (stub)
class ChatGPTClient:
    def __init__(self, api_key, model="gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
    
    def call_api(self, prompt):
        # Stub returns mock response
        return {"choices": [{"text": "Mock response"}]}
```

---

### **ISSUE 2: "tests/test_fact_checker.py: No such file"**

**Symptom:**
```
FileNotFoundError: tests/test_fact_checker.py does not exist
```

**Cause:**
- Cursor didn't create test files
- Directory doesn't exist

**Solution:**

✅ **Create directories first:**
```bash
mkdir -p src/quality
mkdir -p src/core
mkdir -p src/analysis
mkdir -p tests
mkdir -p logs/fact_check_reports
mkdir -p logs/human_reviews
mkdir -p config
```

✅ **Verify Cursor created files:**
```bash
ls -lh src/quality/fact_checker.py
ls -lh tests/test_fact_checker.py
```

✅ **If files missing, re-run prompt:**
- Open STAGE_3_CURSOR_PROMPT_SESSION_1_DAYS_1_2.md
- Copy REQUIREMENTS 4 (test creation)
- Paste into Cursor again
- Run: `pytest tests/test_fact_checker.py -v`

---

### **ISSUE 3: "pytest: command not found"**

**Symptom:**
```
bash: pytest: command not found
```

**Cause:**
- pytest not installed

**Solution:**

✅ **Install pytest:**
```bash
pip install pytest --break-system-packages

# Verify:
pytest --version
# Should show: pytest X.X.X
```

---

### **ISSUE 4: "JSON decode error" when loading metadata**

**Symptom:**
```
json.decoder.JSONDecodeError: Expecting value: line 1 column 1
```

**Cause:**
- Mock data file corrupted
- File doesn't contain valid JSON

**Solution:**

✅ **Validate mock data:**
```bash
# Check file exists and has content
ls -lh data/approved_scripts/*_metadata.json

# Test JSON validity:
python3 << 'EOF'
import json
from pathlib import Path

for f in Path("data/approved_scripts").glob("*_metadata.json"):
    try:
        with open(f) as file:
            data = json.load(file)
        print(f"✅ {f.name}: Valid")
    except json.JSONDecodeError as e:
        print(f"❌ {f.name}: Invalid JSON: {e}")
    except Exception as e:
        print(f"❌ {f.name}: {e}")
EOF
```

✅ **Recreate mock data if corrupted:**
```bash
# Delete old files
rm -rf data/

# Recreate with generator:
# Run STAGE_2_MOCK_DATA_GENERATOR.md again
python3 << 'EOF'
# [Paste STAGE_2_MOCK_DATA_GENERATOR.md script here]
EOF
```

---

### **ISSUE 5: "test_fact_checker.py FAILED - ChatGPTClient not working"**

**Symptom:**
```
ChatGPTClient returned unexpected response format
```

**Cause:**
- Mock client not returning correct format
- Real API returned error

**Solution:**

✅ **If using real API, check credentials:**
```bash
# Verify API key exists
cat credentials/api_keys.txt | grep OPENAI

# Test API key is valid:
python3 << 'EOF'
import os
from src.api.chatgpt_client import ChatGPTClient

api_key = open("credentials/api_keys.txt").read().strip()
client = ChatGPTClient(api_key=api_key)

# Test call
response = client.call_api("Say hello")
print(f"✅ API working: {response}")
EOF
```

✅ **If using mock client, verify response format:**
```python
# Mock response must match this format:
expected_format = {
    "choices": [
        {
            "text": "response text here"
        }
    ]
}

# In your test, ensure mock returns this format
```

✅ **If API rate limited, wait and retry:**
```bash
# Error: "Rate limit exceeded"
# Solution: Wait 60 seconds and retry

sleep 60
pytest tests/test_fact_checker.py -v
```

---

### **ISSUE 6: "5 fact-check reports not created"**

**Symptom:**
```
ls logs/fact_check_reports/*.json shows fewer than 5 files
```

**Cause:**
- Script loading failed
- Report saving failed
- Some scripts skipped

**Solution:**

✅ **Check which scripts loaded:**
```bash
python3 << 'EOF'
from pathlib import Path
import json

# Count metadata files
metadata_files = list(Path("data/approved_scripts").glob("*_metadata.json"))
print(f"Metadata files: {len(metadata_files)}")

# Count fact-check reports
reports = list(Path("logs/fact_check_reports").glob("*_fact_check.json"))
print(f"Reports created: {len(reports)}")

# Find missing scripts
created_ids = {r.name.split('_')[0:4] for r in reports}
metadata_ids = {m.name.split('_')[0:4] for m in metadata_files}

missing = metadata_ids - created_ids
if missing:
    print(f"\n❌ Missing reports for:")
    for m_id in missing:
        print(f"  {'_'.join(m_id)}")
EOF
```

✅ **Re-run fact-checking for missing videos:**
```python
from src.quality.fact_checker import FactChecker
from src.core.stage3_loader import load_stage2_outputs

checker = FactChecker(api_key="your_key")
videos = load_stage2_outputs()

# Run only missing ones
for video in videos:
    script_id = video['script_id']
    report_file = f"logs/fact_check_reports/{script_id}_fact_check.json"
    
    if not Path(report_file).exists():
        print(f"Creating missing report for {script_id}...")
        report = checker.fact_check_script(
            script_id,
            video['script'],
            video['topic']
        )
        print(f"✅ Created {report_file}")
```

---

### **ISSUE 7: "Human review files not created"**

**Symptom:**
```
Only 2-3 human review files instead of 5
```

**Cause:**
- FinalReviewer.review_video() failed
- Approval status not recorded

**Solution:**

✅ **Check which reviews created:**
```bash
ls -lh logs/human_reviews/*_human_review.json
# Count should be 5
```

✅ **Re-run human reviews:**
```python
from src.quality.final_reviewer import FinalReviewer
from pathlib import Path
import json

reviewer = FinalReviewer()

# Find missing reviews
fact_check_dir = Path("logs/fact_check_reports")
review_dir = Path("logs/human_reviews")

for report_file in fact_check_dir.glob("*_fact_check.json"):
    script_id = report_file.stem.replace("_fact_check", "")
    review_file = review_dir / f"{script_id}_human_review.json"
    
    if not review_file.exists():
        print(f"Creating missing review for {script_id}...")
        
        # Load fact-check report
        with open(report_file) as f:
            fact_check = json.load(f)
        
        # Create review
        review = reviewer.review_video(script_id, None, fact_check)
        
        # Save review
        with open(review_file, 'w') as f:
            json.dump(review, f, indent=2)
        
        print(f"✅ Created {review_file}")
```

---

### **ISSUE 8: "Quality gates validation failed"**

**Symptom:**
```
Gate 3 accuracy 72% (below 75% threshold)
Gate 4 approval 75% (below 80% threshold)
```

**Cause:**
- Too many videos flagged as risky
- Too many videos rejected by human

**Solution:**

✅ **Check accuracy scores:**
```bash
python3 << 'EOF'
import json
from pathlib import Path

# Gate 3: Fact-check accuracy
fact_checks = list(Path("logs/fact_check_reports").glob("*.json"))
risk_count = 0

for f in fact_checks:
    with open(f) as file:
        data = json.load(file)
    risk = data.get("claims_risk", 0)
    if risk > 0:
        risk_count += 1
        print(f"{f.name}: {risk} risk items")

print(f"\nTotal with risk items: {risk_count}/5")
print(f"Accuracy: {(5 - risk_count)/5:.0%}")

# Gate 4: Human approval
reviews = list(Path("logs/human_reviews").glob("*.json"))
approved = 0

for f in reviews:
    with open(f) as file:
        data = json.load(file)
    if data.get("approval_status") == "APPROVED":
        approved += 1

print(f"\nApproved: {approved}/5")
print(f"Approval rate: {approved/5:.0%}")
EOF
```

✅ **If accuracy below threshold:**
- Fact-check was too strict
- Check risk keywords in STAGE_3_FIXES_AND_CLARIFICATIONS.md
- Re-run with adjusted prompts

✅ **If approval below threshold:**
- Videos have genuine quality issues
- Regenerate videos from Stage 2
- Re-run Stage 3

---

### **ISSUE 9: "Stage 3 final report not generated"**

**Symptom:**
```
logs/stage_3_final_report.json does not exist
```

**Cause:**
- FinalDecisionEngine.make_go_nogo_decision() not called
- Tests passed but report not saved

**Solution:**

✅ **Check if Stage3Orchestrator ran:**
```bash
python3 << 'EOF'
from src.stage3_orchestrator import Stage3Orchestrator

orchestrator = Stage3Orchestrator(api_key="your_key")

# Run complete pipeline
result = orchestrator.run_stage_3_complete()

# Verify report created
import json
with open('logs/stage_3_final_report.json') as f:
    report = json.load(f)

print(f"✅ Report created: {report['decision']}")
EOF
```

✅ **Manually generate report:**
```python
from src.analysis.final_decision import FinalDecisionEngine
import json

engine = FinalDecisionEngine()

# Load all previous results
with open('logs/gate_3_results.json') as f:
    gate_3 = json.load(f)

with open('logs/agent_analysis.json') as f:
    agent_analysis = json.load(f)

with open('logs/tone_performance.json') as f:
    tone_perf = json.load(f)

# Make decision
decision = engine.make_go_nogo_decision(gate_3, agent_analysis, tone_perf)

# Save report
report_path = engine.generate_final_report(decision)
print(f"✅ Report saved: {report_path}")
```

---

### **ISSUE 10: "Test passes but no files created"**

**Symptom:**
```
pytest shows PASSED but files don't exist
```

**Cause:**
- Mock tests passing but not executing real code
- Cursor created tests but not implementation

**Solution:**

✅ **Check test vs. implementation:**
```bash
# If test exists but implementation missing:
test -f src/quality/fact_checker.py
# If shows: No such file, implementation is missing

# Check what's in src/quality:
ls -la src/quality/
```

✅ **Re-run Cursor with full prompt:**
- Don't just copy REQUIREMENT 4 (tests)
- Copy REQUIREMENTS 1-3 (implementation)
- Then REQUIREMENT 4 (tests)
- Cursor needs full context

---

## 🚨 EMERGENCY RECOVERY

### **If everything breaks, start fresh:**

```bash
#!/bin/bash

echo "=== STAGE 3 EMERGENCY RESET ==="

# 1. Keep Stage 2
echo "Keeping Stage 2 files..."
# Don't delete: src/, config/, credentials/

# 2. Delete Stage 3 work
echo "Deleting Stage 3 outputs..."
rm -rf logs/fact_check_reports/
rm -rf logs/human_reviews/
rm -rf src/quality/
rm -rf src/analysis/
rm -rf src/core/stage3_loader.py
rm -f logs/stage_3_final_report.json
rm -f logs/stage_3_quality_metrics.json
rm -f tests/test_fact_checker.py
rm -f tests/test_final_reviewer.py
rm -f tests/test_quality_gates.py
rm -f tests/test_agent_analyzer.py
rm -f tests/test_tone_analytics.py
rm -f tests/test_stage3_complete.py

# 3. Re-create mock data
echo "Recreating mock data..."
python3 << 'EOF'
# [Paste STAGE_2_MOCK_DATA_GENERATOR.md script]
EOF

# 4. Start over
echo "✅ Stage 3 reset complete"
echo "Start from Day 1 with STAGE_3_CURSOR_PROMPT_SESSION_1_DAYS_1_2.md"
```

---

## 📞 IF YOU'RE STUCK

**Checklist before asking for help:**

- [ ] Read error message carefully (first 2 lines usually have the clue)
- [ ] Search this troubleshooting guide for exact error message
- [ ] Run diagnostics (see top of this file)
- [ ] Check file existence (ls command)
- [ ] Verify Stage 2 completed (do Stage 3 depend on it)
- [ ] Check Python version (python3 --version)
- [ ] Check Python packages (pip list | grep pytest)

**If still stuck:**

1. Document exact error message
2. Share output of diagnostics script
3. Share which Day/Session you're on
4. Check if this is reported in KNOWN_ISSUES.md

---

## ✅ COMMON SUCCESS INDICATORS

**Day 1-2 looks good if:**
- ✅ pytest tests/test_fact_checker.py -v shows ALL PASS
- ✅ logs/fact_check_reports/ has 5 JSON files
- ✅ Each JSON has claims_safe, claims_caution, claims_risk

**Day 3 looks good if:**
- ✅ pytest tests/test_final_reviewer.py -v shows ALL PASS
- ✅ logs/human_reviews/ has 5 JSON files
- ✅ approval_status is either "APPROVED" or "REJECTED"

**Days 4-7 look good if:**
- ✅ All 6 test files pass (pytest tests/ -v)
- ✅ logs/stage_3_final_report.json exists
- ✅ decision is "GO" or "GO_WITH_CAUTION"

---

*Troubleshooting Date: May 15, 2026*  
*Status: Complete coverage*  
*All common issues documented*
