# STAGE 3 EXECUTION PLAN - FIXES & CLARIFICATIONS
**Date:** May 15, 2026  
**Purpose:** Align Stage 3 with Stage 2 outputs and close all gaps  
**Status:** Review complete, fixes documented

---

## 📋 CHANGES REQUIRED FOR STAGE 3

### FIX 1: Specify API Client for Fact-Checker

**Current (Stage 3 Original):**
```python
class FactChecker:
    def __init__(self):
        self.agent = load_agent()  # Vague - which agent?
```

**Fixed Version:**
```python
from src.api.chatgpt_client import ChatGPTClient

class FactChecker:
    def __init__(self, api_key: str):
        # CRITICAL: Use ChatGPT/Claude for fact-checking
        # NEVER use DeepSeek (insufficient accuracy)
        # Use exact same model as Stage 2 AgentVerifier
        self.agent = ChatGPTClient(api_key=api_key, model="gpt-4o-mini")
        self.risk_levels = ["safe", "caution", "risk"]
```

**Why:** 
- Consistency with Stage 2 AgentVerifier
- ChatGPT/Claude has necessary accuracy for fact-checking
- DeepSeek lacks accuracy for policy compliance
- Prevents accidental API waste

---

### FIX 2: Add Configuration File Creation

**Current (Stage 3 Original):**
Assumes `config/fact_check_prompts.json` exists (it doesn't)

**Fixed Version:**
```python
# In Stage 3 setup, add:

def setup_stage_3_configs():
    """Create missing config files for Stage 3"""
    import json
    from pathlib import Path
    
    # Create fact_check_prompts.json
    fact_check_config = {
        "claim_extraction": {
            "prompt": """Extract all factual claims from this YouTube script.
            
Include claims like:
- 'Studies show 8 hours of sleep is optimal'
- 'Depression affects 5% of population'
- 'Meditation reduces stress'

Do NOT include:
- Opinions ('I think...')
- General statements ('Sleep is important')
- Rhetorical questions

Return as JSON list: ["claim1", "claim2", ...]""",
            "model": "gpt-4o-mini"
        },
        "risk_assessment": {
            "prompt": """Assess the risk level for these claims:

Medical/Health: Any 'cure', 'treat', 'prevent', 'dangerous', 'toxic' = RISK
Legal: 'Illegal', 'law', 'license' = RISK
Financial: 'Invest', 'guarantee', 'returns' = RISK
Research: 'Studies show', 'research', 'statistics' = CAUTION (needs verification)
Otherwise: SAFE

Return JSON: {"claim": "...", "risk": "safe/caution/risk"}""",
            "model": "gpt-4o-mini"
        },
        "risk_keywords": {
            "medical": ["cure", "treat", "prevent", "disease", "dangerous", "toxic", "poison"],
            "legal": ["illegal", "law", "license", "regulation"],
            "financial": ["invest", "guarantee", "returns", "profit"],
            "research": ["studies show", "research", "statistics", "study"]
        }
    }
    
    config_path = Path("config/fact_check_prompts.json")
    if not config_path.exists():
        with open(config_path, 'w') as f:
            json.dump(fact_check_config, f, indent=2)
        print(f"✅ Created {config_path}")
    
    # Create final_review_checklist.json
    checklist_config = {
        "title": "Final Content Review Checklist",
        "description": "5-item critical checklist for human approval",
        "time_estimate_minutes": 8,
        "items": [
            {
                "id": "accuracy",
                "label": "✅ Content is accurate (no misinformation)",
                "description": "Facts match fact-checker findings, no major claims contradicted",
                "critical": True,
                "time_minutes": 2
            },
            {
                "id": "audio_quality",
                "label": "✅ Audio is clear, audible, and synced",
                "description": "No gaps, distortion, or sync issues with video",
                "critical": True,
                "time_minutes": 1
            },
            {
                "id": "video_quality",
                "label": "✅ Video quality is acceptable (no glitches)",
                "description": "1080p, no freezes, transitions smooth, subtitles correct",
                "critical": True,
                "time_minutes": 2
            },
            {
                "id": "metadata",
                "label": "✅ Metadata is accurate (title, description, tags)",
                "description": "Title matches content, description is useful, tags are relevant",
                "critical": True,
                "time_minutes": 1
            },
            {
                "id": "guidelines",
                "label": "✅ No policy violations (copyright, harassment, etc)",
                "description": "No copyright/trademark issues, no banned content, no spam",
                "critical": True,
                "time_minutes": 2
            }
        ]
    }
    
    checklist_path = Path("config/final_review_checklist.json")
    if not checklist_path.exists():
        with open(checklist_path, 'w') as f:
            json.dump(checklist_config, f, indent=2)
        print(f"✅ Created {checklist_path}")

# Call at Stage 3 start:
setup_stage_3_configs()
```

---

### FIX 3: Clarify Gate Numbering

**Current (Stage 3 Original):**
```
GATE 1: Agent Verification (Stage 2)
GATE 2: Agent Fact-Check (Stage 3)
GATE 3: Human Final Review (Stage 3)
```

**Should Be:**
```
GATE 2: Agent Verification (Stage 2) ← Already completed
GATE 3: Fact-Check Accuracy (Stage 3) ← New requirement
GATE 4: Human Final Approval (Stage 3) ← New requirement
GATE 5: YouTube Upload Success (Stage 4)
GATE 6: Sustainability Metrics (Stage 5+)
```

**Update in Code:**
```python
class QualityGates:
    GATE_2 = {
        "name": "Agent Verification",
        "stage": 2,
        "status": "PASSED",
        "requirement": "Script passes Agent verification (≥80% accuracy)",
        "completed": True
    }
    
    GATE_3 = {
        "name": "Fact-Check Accuracy",
        "stage": 3,
        "status": "IN_PROGRESS",
        "requirement": "Combined accuracy 75-85% on fact-checking",
        "completed": False
    }
    
    GATE_4 = {
        "name": "Human Final Approval",
        "stage": 3,
        "status": "IN_PROGRESS",
        "requirement": "Human reviews and approves 80%+ of videos",
        "completed": False
    }
```

---

### FIX 4: Define Data Loading from Stage 2

**Current (Stage 3 Original):**
```python
def fact_check_script(self, script_id, script_text, topic):
    # Doesn't show where script_id comes from
```

**Fixed Version:**
```python
def load_stage2_outputs(video_count: int = 5):
    """Load videos and scripts from Stage 2"""
    import json
    from pathlib import Path
    
    approved_scripts_dir = Path("data/approved_scripts")
    videos = []
    
    # Find all approved scripts (those that passed Agent verification)
    for metadata_file in sorted(approved_scripts_dir.glob("*_metadata.json"))[:video_count]:
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        # Only load if agent verification passed
        if metadata.get("agent_verification_passed"):
            videos.append({
                "script_id": metadata.get("script_id"),
                "video_path": metadata.get("video_path"),
                "script": metadata.get("script"),
                "topic": metadata.get("topic"),
                "tone": metadata.get("tone_used"),
                "metadata": metadata
            })
    
    return videos

# Usage in Day 1-2:
stage2_videos = load_stage2_outputs(video_count=5)
for video in stage2_videos:
    script_id = video["script_id"]
    script_text = video["script"]
    topic = video["topic"]
    
    # Now fact-check this video
    fact_check_report = fact_checker.fact_check_script(script_id, script_text, topic)
```

---

### FIX 5: Add Explicit API Cost Allocation

**Add to Stage 3 documentation:**
```
API ALLOCATION IN STAGE 3:

- Fact-Checking: ChatGPT/Claude (claim extraction + risk assessment)
  Cost per script: ~$0.08-0.12
  
- Human Review: Manual work (no API cost)
  Time: 5-10 minutes per video
  
- Tone Analytics: Query existing logs (no API cost)
  
- Analysis: ChatGPT for accuracy assessment (optional)
  Cost: ~$0.02-0.05

Total cost per Stage 3 video: ~$0.08-0.17
(Much lower than Stage 2 due to no generation work)
```

---

### FIX 6: Define Success Metrics Clearly

**Add to Day 7 Analysis:**
```python
class Stage3Metrics:
    def __init__(self):
        self.metrics = {
            "gate_3_accuracy": {
                "target": "75-85%",
                "calculation": "videos_passing_fact_check / total_videos",
                "pass_threshold": 0.75,
                "fail_threshold": 0.85,
                "acceptable_range": (0.75, 0.85)
            },
            "gate_4_approval": {
                "target": "80%+",
                "calculation": "videos_approved_by_human / total_videos",
                "pass_threshold": 0.80
            },
            "human_review_efficiency": {
                "target": "5-10 minutes per video",
                "tracking": "log_review_time(video_id, start_time, end_time)"
            },
            "zero_policy_violations": {
                "requirement": "No copyright, harassment, banned content detected",
                "tracking": "manual_review + fact_checker_assessment"
            }
        }
    
    def calculate_combined_accuracy(self, results):
        """
        Results format:
        {
            "video_1": {"gate_3": "pass", "gate_4": "approve"},
            "video_2": {"gate_3": "pass", "gate_4": "reject"},
            ...
        }
        """
        total = len(results)
        gate_3_pass = sum(1 for v in results.values() if v.get("gate_3") == "pass")
        gate_4_approve = sum(1 for v in results.values() if v.get("gate_4") == "approve")
        
        gate_3_accuracy = gate_3_pass / total if total > 0 else 0
        gate_4_approval = gate_4_approve / total if total > 0 else 0
        combined = (gate_3_pass + gate_4_approve) / (total * 2) if total > 0 else 0
        
        return {
            "gate_3_accuracy": f"{gate_3_accuracy:.1%}",
            "gate_4_approval": f"{gate_4_approval:.1%}",
            "combined_accuracy": f"{combined:.1%}"
        }
```

---

### FIX 7: Add Error Recovery Procedures

**Add to Stage 3:**
```python
def handle_fact_check_failure(script_id: str, flagged_claims: list):
    """
    If fact-check finds misinformation, define recovery:
    
    Option 1: Minor issue (1 claim)
    - Note correction
    - Continue to human review
    - Human decides if acceptable
    
    Option 2: Major issue (2+ claims or policy violation)
    - Log issue
    - REJECT this script
    - Move to next script
    - Track for analysis
    
    Option 3: Recoverable (flagged as caution, not risk)
    - You verify claim manually
    - If correct: approve and continue
    - If incorrect: reject
    """
    
    if len(flagged_claims) >= 2:
        return "REJECT"  # Major issue
    elif any(claim["risk"] == "risk" for claim in flagged_claims):
        return "REJECT"  # Policy violation risk
    else:
        return "REVIEW"  # Minor - human decides

def handle_human_rejection(video_id: str, rejection_reason: str):
    """
    If human rejects a video, define path:
    
    Reasons:
    - Audio quality: Regenerate audio, re-verify
    - Content mismatch: Regenerate script, restart
    - Policy concern: Mark for analysis, don't publish
    - Technical issue: Fix and retry
    """
    log_rejection(video_id, rejection_reason)
    
    if "audio" in rejection_reason:
        # Could regenerate just audio (TTS re-run)
        return "regenerate_audio"
    elif "content" in rejection_reason:
        # Need to start over from Stage 2
        return "restart_from_stage_2"
    else:
        # Mark for review, move on
        return "flag_for_review"
```

---

## 📝 UPDATED STAGE 3 SEQUENCE

### Day 1-2: Fact-Check Integration ✅ READY

1. ✅ Create FactChecker class (uses ChatGPTClient)
2. ✅ Create fact_check_prompts.json config
3. ✅ Load scripts from data/approved_scripts/
4. ✅ Extract claims and assess risk
5. ✅ Human verification of flagged claims
6. ✅ Log results

### Day 3: Human Final Review ✅ READY

1. ✅ Create FinalReviewer class
2. ✅ Create final_review_checklist.json config
3. ✅ Display checklist UI
4. ✅ Record human decisions
5. ✅ Log approvals/rejections

### Day 4: Quality Gate Validation ✅ READY

1. ✅ Implement QualityGate class
2. ✅ Reference GATE 3 (fact-check) and GATE 4 (human approval)
3. ✅ Define pass/fail thresholds
4. ✅ Track metrics

### Day 5: Agent Accuracy Analysis ✅ READY

1. ✅ Use ChatGPT to assess Agent decisions from Stage 2
2. ✅ Measure accuracy of Agent verification
3. ✅ Document patterns
4. ✅ Recommend adjustments if needed

### Day 6: Tone Performance Tracking ✅ READY

1. ✅ Implement ToneAnalytics class
2. ✅ Log tone selection
3. ✅ Prepare for future optimization

### Day 7: Analysis & Go/No-Go ✅ READY

1. ✅ Calculate combined accuracy (Gate 3 + Gate 4)
2. ✅ Verify metrics meet targets
3. ✅ Make GO/NO-GO decision
4. ✅ Document findings

---

## 🎯 READY FOR STAGE 3 IMPLEMENTATION

All gaps identified and fixes documented.

Use this document as supplement to STAGE_3_EXECUTION_PLAN.md.

When implementing Stage 3 Cursor prompts, incorporate these fixes.

---

## ✅ SIGN-OFF CHECKLIST

- [x] Stage 2 outputs identified
- [x] Stage 2→3 data flow mapped
- [x] All gaps documented
- [x] All fixes specified
- [x] Configuration templates created
- [x] Code examples provided
- [x] Error recovery procedures defined
- [x] Success metrics clarified
- [x] API allocation updated
- [x] Quality gates renumbered

**Status: READY FOR STAGE 3 IMPLEMENTATION 🚀**

