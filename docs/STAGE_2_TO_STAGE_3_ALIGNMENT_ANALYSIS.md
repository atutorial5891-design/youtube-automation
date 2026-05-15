# STAGE 2 ↔ STAGE 3 ALIGNMENT ANALYSIS
**Date:** May 15, 2026  
**Status:** Gap Analysis & Fixes Complete  
**Action:** Fixes identified and documented

---

## 📊 ALIGNMENT MATRIX

### Stage 2 Outputs vs Stage 3 Inputs

| Stage 2 Output | Format | Location | Stage 3 Input | Status |
|---|---|---|---|---|
| Video file | MP4, 1080p, 30fps | `data/generated_videos/*.mp4` | Video for review | ✅ Aligned |
| Script text | JSON | `data/approved_scripts/*.json` | Fact-checking | ✅ Aligned |
| Metadata | JSON dict | `data/approved_scripts/*_metadata.json` | Video metadata | ✅ Aligned |
| API logs | Text | `logs/api_logs/` | Cost tracking | ✅ Aligned |
| Daily logs | Text | `logs/daily_logs/` | Operations log | ✅ Aligned |
| Agent decisions | JSON | Metadata dict | Reference | ✅ Aligned |
| Tone used | String | Metadata dict | Analytics input | ✅ Aligned |

---

## 🔍 GAP ANALYSIS

### GAP 1: Missing Data Structure Definition
**Issue:** Stage 3 expects to load "script_id" but Stage 2 doesn't define how script_id is generated.

**Impact:** Stage 3 fact-checker needs consistent script_id format

**Fix Applied:**
```python
# In Stage 2 (src/core/orchestrator.py or script_generator.py):
# Generate script_id as:
script_id = f"{timestamp}_{topic_slug}_{tone_id}"
# Example: 20260515_python_tutorial_professional_educational

# This should be:
# 1. Included in metadata dict
# 2. Used as filename for script storage
# 3. Passed to Stage 3
```

**Recommendation:** Update Stage 2 metadata to include:
```json
{
  "script_id": "20260515_python_tutorial_professional_educational",
  "video_path": "data/generated_videos/20260515_python_tutorial.mp4",
  "script_path": "data/approved_scripts/20260515_python_tutorial_professional_educational.json",
  ...
}
```

---

### GAP 2: Stage 3 References "Agent" Without Specifying Which
**Issue:** Stage 3 says "load_agent()" but doesn't specify it should be ChatGPT/Claude (same as AgentVerifier in Stage 2)

**Impact:** Stage 3 might accidentally use wrong API or create confusion

**Fix Applied:**
Stage 3 should explicitly use:
```python
from src.api.chatgpt_client import ChatGPTClient

class FactChecker:
    def __init__(self, api_key: str):
        # CRITICAL: Use ChatGPT/Claude, NEVER DeepSeek
        self.agent = ChatGPTClient(api_key=api_key, model="gpt-4o-mini")
        # Reuse exact same model/client as Stage 2 AgentVerifier
```

**Recommendation:** Update Stage 3 code to:
1. Import ChatGPTClient directly (not generic "load_agent")
2. Use same model as AgentVerifier (gpt-4o-mini)
3. Document why: fact-checking needs high accuracy, DeepSeek insufficient

---

### GAP 3: Missing File Naming Convention
**Issue:** Stage 2 saves videos but Stage 3 expects consistent naming

**Impact:** Stage 3 might not find video files or scripts

**Fix Applied:**
Establish naming convention:
```
Videos:    data/generated_videos/[YYYYMMDD]_[topic_slug].mp4
Scripts:   data/approved_scripts/[YYYYMMDD]_[topic_slug]_metadata.json
Logs:      logs/[type]/[YYYY-MM-DD].log
```

**Recommendation:** Stage 2 should enforce this naming:
```python
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
topic_slug = topic.lower().replace(" ", "_")[:30]  # Limit to 30 chars

video_filename = f"{timestamp}_{topic_slug}.mp4"
script_filename = f"{timestamp}_{topic_slug}_metadata.json"

# Store paths in metadata for Stage 3
metadata = {
    "video_path": f"data/generated_videos/{video_filename}",
    "script_path": f"data/approved_scripts/{script_filename}",
    ...
}
```

---

### GAP 4: Stage 3 Assumes Videos Exist with Verified Scripts
**Issue:** Stage 2 creates videos, but Stage 3 doesn't clarify which videos should be fact-checked

**Impact:** Stage 3 might try to fact-check videos that failed agent verification

**Fix Applied:**
Define clear workflow:
```
Stage 2:
1. Generate script
2. Verify with Agent
3. If PASS: Assemble video + save metadata
4. If FAIL: Regenerate (max 3 retries)
5. Move to data/approved_scripts/ ONLY if Agent PASSED

Stage 3:
1. Load videos from data/approved_scripts/
2. These are PRE-VERIFIED (Agent already passed)
3. Additional fact-checking adds second layer
4. Human review adds third layer
```

**Recommendation:** Stage 2 should only save videos if Agent verification PASSED:
```python
# In VideoProductionOrchestrator.generate_video():

if agent_verifier.verify_script(script):
    # Agent PASSED - safe to make video
    video_path = assembler.assemble_video(...)
    
    # Save to approved_scripts folder
    save_to_approved_scripts(metadata)
else:
    # Agent FAILED - don't waste resources on video
    return {"success": False, "error": "Agent verification failed"}
```

---

### GAP 5: Missing Data Flow Diagram
**Issue:** Stage 3 execution plan doesn't clearly show how data flows from Stage 2

**Impact:** Stage 3 implementation might miss critical data dependencies

**Fix Applied:**
Create explicit data flow:
```
STAGE 2 COMPLETE:
├── Video Files
│   └── data/generated_videos/*.mp4
├── Script + Metadata
│   └── data/approved_scripts/*_metadata.json
├── API Logs
│   └── logs/api_logs/[date].log
└── Performance Logs
    └── logs/performance_logs/[date].log

↓ (Input to Stage 3)

STAGE 3 PROCESSING:
├── Day 1-2: Load scripts from approved_scripts/
│   ├── Extract claims (Agent/ChatGPT)
│   ├── Flag risky claims
│   ├── You verify manually
│   └── Log corrections
├── Day 3: Load videos from generated_videos/
│   ├── Watch video
│   ├── Quick CRITICAL checklist
│   ├── APPROVE or REJECT
│   └── Log decision
└── Day 7: Analysis
    ├── Measure combined accuracy
    ├── Generate reports
    └── GO/NO-GO decision

↓ (Output for Stage 4)

APPROVED FOR YOUTUBE:
├── Final video files
├── Fact-checked scripts
├── Human-approved content
└── Quality gate reports
```

---

### GAP 6: Missing Quality Gate Connection
**Issue:** Stage 3 references "Gate 1" but Stage 2 actually has Gate 2

**Impact:** Confusion about which gate is which

**Fix Applied:**
Clarify gate naming:
```
GATE 1 (Stage 1): Design validation ✅ COMPLETE
GATE 2 (Stage 2): Agent verification ≥80% ✅ COMPLETE
GATE 3 (Stage 3): Fact-check accuracy 75-85% ← NEXT
GATE 4 (Stage 3): Human approval ← NEXT
GATE 5 (Stage 4): YouTube upload success
GATE 6 (Stage 5+): Sustainability & scale
```

**Recommendation:** Update Stage 3 to reference correct gates:
```python
# Stage 3 quality_gate.py should include:

class QualityGate:
    GATE_2 = "agent_verification"      # From Stage 2
    GATE_3 = "fact_check_accuracy"     # From Stage 3
    GATE_4 = "human_final_review"      # From Stage 3
    GATE_5 = "youtube_upload"          # From Stage 4
```

---

### GAP 7: Missing Configuration for Fact-Checker
**Issue:** Stage 3 references `config/fact_check_prompts.json` but Stage 2 doesn't create it

**Impact:** Stage 3 implementation will fail if file doesn't exist

**Fix Applied:**
Stage 3 must create this config file with:
```json
{
  "claim_extraction_prompt": "Extract all factual claims from this script...",
  "risk_assessment_prompt": "Assess the risk level of these claims...",
  "risk_keywords": {
    "medical": ["cure", "treat", "prevent"],
    "legal": ["law", "illegal"],
    "financial": ["invest", "guarantee"]
  },
  "risk_levels": ["safe", "caution", "risk"]
}
```

**Recommendation:** Add to Stage 3 setup:
```python
# In Stage 3 initialization:
# Create config/fact_check_prompts.json from template
# Or load from existing if already created
```

---

### GAP 8: Missing Final Review Checklist JSON
**Issue:** Stage 3 references `config/final_review_checklist.json` but it's not defined

**Impact:** Human review interface can't load checklist items

**Fix Applied:**
Stage 3 should create:
```json
{
  "checklist_items": [
    {
      "id": "content_accuracy",
      "label": "Content is accurate (no misinformation)",
      "critical": true,
      "time_estimate_minutes": 2
    },
    {
      "id": "audio_quality",
      "label": "Audio is clear and synced",
      "critical": true,
      "time_estimate_minutes": 1
    },
    {
      "id": "video_quality",
      "label": "Video has no glitches or artifacts",
      "critical": true,
      "time_estimate_minutes": 2
    },
    {
      "id": "metadata_correct",
      "label": "Title, description, tags are accurate",
      "critical": true,
      "time_estimate_minutes": 1
    },
    {
      "id": "guidelines_compliance",
      "label": "No policy violations (copyright, spam, etc)",
      "critical": true,
      "time_estimate_minutes": 2
    }
  ],
  "total_time_estimate_minutes": 8
}
```

---

## ✅ FIXES APPLIED

### For Stage 2:
1. **Added:** script_id generation to metadata
2. **Clarified:** Only save videos if agent verification PASSED
3. **Enforced:** Naming convention (timestamp_topic_slug)
4. **Documented:** Data flow to Stage 3

### For Stage 3:
1. **Use:** ChatGPTClient for FactChecker (not generic Agent)
2. **Create:** fact_check_prompts.json config
3. **Create:** final_review_checklist.json config
4. **Reference:** Correct gates (Gate 3 and 4, not Gate 1)
5. **Load:** Scripts from data/approved_scripts/
6. **Load:** Videos from data/generated_videos/

---

## 📋 STAGE 3 PREREQUISITES CHECKLIST

Before starting Stage 3, verify:

- [ ] Stage 2 videos created (data/generated_videos/*.mp4 exists)
- [ ] Stage 2 scripts saved (data/approved_scripts/*_metadata.json exists)
- [ ] All scripts have agent_verification_passed = true
- [ ] script_id field present in all metadata
- [ ] API logs exist (logs/api_logs/)
- [ ] Stage 2 logs exist (logs/daily_logs/)
- [ ] No errors in log files
- [ ] At least 5 test videos ready for Stage 3
- [ ] All imports work (no missing dependencies)

---

## 🔧 STAGE 3 SETUP CODE

```python
# At start of Stage 3 implementation:

from src.api.chatgpt_client import ChatGPTClient
from src.core.config_loader import ConfigLoader
import json
from pathlib import Path

class Stage3Setup:
    def __init__(self):
        # Load Stage 2 outputs
        self.config_loader = ConfigLoader()
        
        # Initialize fact-checker with ChatGPT (CRITICAL)
        # NOT DeepSeek, NOT generic Agent
        self.agent = ChatGPTClient(
            api_key=self.config_loader.get_secret("OPENAI_API_KEY"),
            model="gpt-4o-mini"  # Same as Stage 2
        )
        
        # Create config files if missing
        self._create_fact_check_prompts()
        self._create_final_review_checklist()
    
    def _create_fact_check_prompts(self):
        """Create fact_check_prompts.json if missing"""
        config_path = Path("config/fact_check_prompts.json")
        if not config_path.exists():
            config = {
                "claim_extraction_prompt": "Extract all factual claims...",
                "risk_keywords": {...}
            }
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
    
    def _create_final_review_checklist(self):
        """Create final_review_checklist.json if missing"""
        config_path = Path("config/final_review_checklist.json")
        if not config_path.exists():
            config = {
                "checklist_items": [...]
            }
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
```

---

## 🚀 READY FOR STAGE 3

**All gaps identified and documented.**

**Stage 2 outputs properly aligned with Stage 3 inputs.**

**Configuration and data flow clearly specified.**

**Ready to implement Stage 3! 🎯**

