# STAGE 3 QUICK START - STEP BY STEP IMPLEMENTATION GUIDE
**Timeline:** 7 days (Week 2)  
**Daily Commitment:** 1-2 hours  
**What You'll Build:** Quality gates + fact-checking + human review system  
**Success Criteria:** Combined accuracy 75-85%  

---

## 📚 DOCUMENT READING ORDER

**Before starting Stage 3, read in this order:**

1. ✅ **This document** (STAGE_3_QUICK_START.md) - 5 min
   - Overview and day-by-day plan

2. ✅ **STAGE_3_FIXES_AND_CLARIFICATIONS.md** - 10 min
   - Important fixes and clarifications
   - Configuration templates
   - Code examples

3. ✅ **STAGE_3_EXECUTION_PLAN.md** - 20 min
   - Original detailed plan
   - Specifications
   - Testing procedures

4. ✅ **STAGE_3_TO_STAGE_4_ALIGNMENT.md** (after Day 7)
   - Prepares you for Stage 4

---

## 🎯 STAGE 3 OVERVIEW

### What Gets Built:
```
Day 1-2: Fact-Check Module
  └─ Extract claims from scripts (ChatGPT)
  └─ Flag risky claims for you to verify
  └─ Corrections logged

Day 3: Human Final Review
  └─ Watch video
  └─ Quick 5-item checklist (5-10 min)
  └─ APPROVE or REJECT

Day 4: Quality Gate Validation
  └─ Implement Gate 3 (fact-check) & Gate 4 (human approval)
  └─ Define pass/fail criteria

Day 5: Agent Analysis
  └─ Review Agent decisions from Stage 2
  └─ Measure verification accuracy

Day 6: Tone Analytics
  └─ Track which tones perform best
  └─ Prepare for future optimization

Day 7: Final Analysis
  └─ Calculate combined accuracy
  └─ Make GO/NO-GO decision for Stage 4
```

### Key Points:
- 🔴 **CRITICAL:** Use ChatGPT/Claude for fact-checking (NOT DeepSeek)
- 🟡 **GATE 3:** Fact-check accuracy must be 75-85%
- 🟡 **GATE 4:** Human approval must be 80%+
- 🟢 **BOTH gates must pass** to proceed to Stage 4

---

## 📋 DAY 1-2: FACT-CHECK MODULE IMPLEMENTATION

### What You're Building:
```
Input:  Script from Stage 2
Process: Extract claims → Assess risk → You verify → Log corrections
Output: Fact-check report with flagged items
```

### Step-by-Step Instructions:

#### Step 1: Create FactChecker Class
```python
# File: src/quality/fact_checker.py

from src.api.chatgpt_client import ChatGPTClient

class FactChecker:
    def __init__(self, api_key: str):
        # CRITICAL: Use ChatGPT/Claude (same as AgentVerifier in Stage 2)
        self.agent = ChatGPTClient(api_key=api_key, model="gpt-4o-mini")
        self.risk_levels = ["safe", "caution", "risk"]
    
    def fact_check_script(self, script_id: str, script_text: str, topic: str) -> dict:
        """
        Main fact-check function
        1. Extract claims from script
        2. Assess risk of each claim
        3. Return report for human review
        """
        # Step 1: Extract all factual claims
        claims = self.extract_claims(script_text)
        
        # Step 2: Classify by risk
        flagged_claims = []
        safe_claims = []
        
        for claim in claims:
            risk = self.assess_risk(claim, topic)
            if risk != "safe":
                flagged_claims.append({
                    "claim": claim,
                    "risk": risk,
                    "needs_verification": True
                })
            else:
                safe_claims.append(claim)
        
        # Step 3: Return report
        return {
            "script_id": script_id,
            "total_claims": len(claims),
            "flagged_claims": flagged_claims,
            "safe_claims": len(safe_claims),
            "status": "awaiting_human_review"
        }
```

**See:** STAGE_3_FIXES_AND_CLARIFICATIONS.md for full implementation

#### Step 2: Create Config File
```bash
# Run this to create fact_check_prompts.json:
python3 << 'EOF'
import json
from pathlib import Path

config = {
    "claim_extraction": {
        "prompt": """Extract all factual claims from this YouTube script.
Include: 'Studies show...', 'Depression affects 5% of population', specific statistics
Exclude: Opinions, general statements, rhetorical questions
Return as JSON list: ["claim1", "claim2", ...]"""
    },
    "risk_assessment": {
        "prompt": """Assess risk of these claims:
Medical: 'cure', 'treat', 'prevent' = RISK
Legal: 'illegal', 'law' = RISK  
Financial: 'invest', 'guarantee' = RISK
Research: 'studies show' = CAUTION
Other: SAFE
Return JSON: {"claim": "...", "risk": "safe/caution/risk"}"""
    }
}

Path("config/fact_check_prompts.json").write_text(
    json.dumps(config, indent=2)
)
print("✅ Created config/fact_check_prompts.json")
EOF
```

#### Step 3: Create Tests
```bash
# File: src/quality/test_fact_checker.py
# Tests should verify:
# - Claim extraction works
# - Risk assessment correct
# - Output format correct
# - Handles edge cases

# Run tests:
pytest src/quality/test_fact_checker.py -v
```

#### Step 4: Process 5 Test Videos
```python
# Load Stage 2 videos:
import json
from pathlib import Path

def load_stage2_scripts(video_count: int = 5):
    """Load approved scripts from Stage 2"""
    scripts = []
    approved_dir = Path("data/approved_scripts")
    
    for metadata_file in sorted(approved_dir.glob("*_metadata.json"))[:video_count]:
        with open(metadata_file) as f:
            metadata = json.load(f)
        
        # Only load if agent verification passed
        if metadata.get("agent_verification_passed"):
            scripts.append({
                "script_id": metadata.get("script_id"),
                "script": metadata.get("script"),
                "topic": metadata.get("topic")
            })
    
    return scripts

# Run fact-checking on each:
fact_checker = FactChecker(api_key="your-openai-key")

for script in load_stage2_scripts():
    report = fact_checker.fact_check_script(
        script_id=script["script_id"],
        script_text=script["script"],
        topic=script["topic"]
    )
    
    print(f"\n📋 {script['topic']}")
    print(f"   Claims found: {report['total_claims']}")
    print(f"   Flagged: {len(report['flagged_claims'])}")
    
    # YOU verify flagged claims:
    for flagged in report['flagged_claims']:
        print(f"\n   ⚠️  {flagged['claim']} ({flagged['risk']})")
        # You decide: correct? needs fix? reject?
        verification = input("   Your decision (correct/fix/reject): ")
        # Log your decision
```

#### Step 5: Log Results
```bash
# Create logs/fact_check_[date].log
# Log format:
# {
#   "script_id": "...",
#   "claims_found": 12,
#   "flagged": 3,
#   "user_corrections": [
#     {"claim": "...", "verification": "correct/fix/reject"}
#   ]
# }
```

**Success Criteria for Days 1-2:**
- ✅ FactChecker class created and working
- ✅ fact_check_prompts.json created
- ✅ Tests pass
- ✅ 5 test scripts fact-checked
- ✅ All flagged claims reviewed by you
- ✅ Corrections logged

---

## 📋 DAY 3: HUMAN FINAL REVIEW IMPLEMENTATION

### What You're Building:
```
Input:  Video from Stage 2 + Fact-check report
Process: Watch video, check 5 items, make decision
Output: APPROVE or REJECT decision + notes
```

### Step-by-Step Instructions:

#### Step 1: Create FinalReviewer Class
```python
# File: src/quality/final_reviewer.py

class FinalReviewer:
    def __init__(self):
        self.checklist_items = self.load_checklist()
    
    def display_checklist(self, video_id: str, video_path: str):
        """Show checklist for human review"""
        print(f"\n🎬 REVIEWING: {video_id}")
        print(f"📁 {video_path}\n")
        
        for item in self.checklist_items:
            print(f"{item['id']}: {item['label']}")
            print(f"   Est. time: {item['time_minutes']} min")
        
        return self.get_human_decision()
    
    def get_human_decision(self) -> dict:
        """Get human's APPROVE or REJECT decision"""
        decision = input("\nFinal decision (APPROVE/REJECT): ").upper()
        
        if decision == "APPROVE":
            return {"decision": "APPROVE", "reason": None}
        elif decision == "REJECT":
            reason = input("Rejection reason: ")
            return {"decision": "REJECT", "reason": reason}
        else:
            return self.get_human_decision()  # Retry
```

**See:** STAGE_3_FIXES_AND_CLARIFICATIONS.md for full code

#### Step 2: Create Checklist Config
```bash
# Create config/final_review_checklist.json
python3 << 'EOF'
import json
from pathlib import Path

checklist = {
    "items": [
        {
            "id": "accuracy",
            "label": "✅ Content is accurate",
            "time_minutes": 2
        },
        {
            "id": "audio",
            "label": "✅ Audio is clear & synced",
            "time_minutes": 1
        },
        {
            "id": "video",
            "label": "✅ Video quality OK (no glitches)",
            "time_minutes": 2
        },
        {
            "id": "metadata",
            "label": "✅ Title & description correct",
            "time_minutes": 1
        },
        {
            "id": "guidelines",
            "label": "✅ No policy violations",
            "time_minutes": 2
        }
    ],
    "total_time_minutes": 8
}

Path("config/final_review_checklist.json").write_text(
    json.dumps(checklist, indent=2)
)
print("✅ Created config/final_review_checklist.json")
EOF
```

#### Step 3: Review 5 Test Videos
```bash
# Run this:
python3 << 'EOF'
from src.quality.final_reviewer import FinalReviewer
import json
from pathlib import Path

reviewer = FinalReviewer()
approved_count = 0
rejected_count = 0

# Load Stage 2 videos
for metadata_file in sorted(Path("data/approved_scripts").glob("*_metadata.json"))[:5]:
    with open(metadata_file) as f:
        metadata = json.load(f)
    
    video_id = metadata["script_id"]
    video_path = metadata["video_path"]
    
    # Show checklist and get decision
    decision = reviewer.display_checklist(video_id, video_path)
    
    # Log decision
    if decision["decision"] == "APPROVE":
        approved_count += 1
        print("✅ APPROVED")
    else:
        rejected_count += 1
        print(f"❌ REJECTED: {decision['reason']}")

print(f"\n📊 Results: {approved_count} approved, {rejected_count} rejected")
EOF
```

**Success Criteria for Day 3:**
- ✅ FinalReviewer class created
- ✅ final_review_checklist.json created
- ✅ 5 videos reviewed
- ✅ Decisions logged (APPROVE/REJECT)
- ✅ Rejection reasons documented
- ✅ Total review time < 60 minutes (8 min each)

---

## 📋 DAY 4: QUALITY GATE VALIDATION

### What You're Building:
```
GATE 3: Fact-check accuracy 75-85%
GATE 4: Human approval 80%+
Combined: Both gates must pass
```

### Step-by-Step Instructions:

#### Step 1: Implement QualityGate Class
```python
# File: src/quality/quality_gates.py

class QualityGates:
    GATE_3_TARGET = (0.75, 0.85)  # 75-85%
    GATE_4_TARGET = 0.80  # 80%+
    
    def __init__(self):
        self.results = {}
    
    def log_gate_3_result(self, script_id: str, passed: bool):
        """Log fact-check result"""
        if script_id not in self.results:
            self.results[script_id] = {}
        self.results[script_id]["gate_3"] = passed
    
    def log_gate_4_result(self, script_id: str, approved: bool):
        """Log human approval result"""
        if script_id not in self.results:
            self.results[script_id] = {}
        self.results[script_id]["gate_4"] = approved
    
    def calculate_accuracy(self) -> dict:
        """Calculate combined accuracy"""
        total = len(self.results)
        gate_3_pass = sum(1 for r in self.results.values() if r.get("gate_3"))
        gate_4_pass = sum(1 for r in self.results.values() if r.get("gate_4"))
        
        gate_3_accuracy = gate_3_pass / total if total else 0
        gate_4_accuracy = gate_4_pass / total if total else 0
        combined = (gate_3_pass + gate_4_pass) / (total * 2) if total else 0
        
        return {
            "gate_3_accuracy": gate_3_accuracy,
            "gate_4_accuracy": gate_4_accuracy,
            "combined_accuracy": combined,
            "gate_3_pass": gate_3_accuracy >= self.GATE_3_TARGET[0],
            "gate_4_pass": gate_4_accuracy >= self.GATE_4_TARGET
        }
```

#### Step 2: Test on 5 Videos
```bash
# Run gates on your 5 test videos
python3 << 'EOF'
from src.quality.quality_gates import QualityGates

gates = QualityGates()

# Populate from your fact-check and human review results
results = {
    "video_1": {"gate_3": True, "gate_4": True},   # Passed both
    "video_2": {"gate_3": True, "gate_4": True},
    "video_3": {"gate_3": True, "gate_4": False},  # Rejected by human
    "video_4": {"gate_3": True, "gate_4": True},
    "video_5": {"gate_3": True, "gate_4": True},
}

gates.results = results
accuracy = gates.calculate_accuracy()

print(f"Gate 3 Accuracy: {accuracy['gate_3_accuracy']:.1%}")
print(f"Gate 4 Approval: {accuracy['gate_4_accuracy']:.1%}")
print(f"Combined: {accuracy['combined_accuracy']:.1%}")
print(f"\nGate 3 Pass? {accuracy['gate_3_pass']} (need 75-85%)")
print(f"Gate 4 Pass? {accuracy['gate_4_pass']} (need 80%+)")
EOF
```

**Success Criteria for Day 4:**
- ✅ QualityGate class implemented
- ✅ Both gates evaluated on 5 videos
- ✅ Accuracy calculated
- ✅ Results logged

---

## 📋 DAY 5: AGENT VERIFICATION ANALYSIS

### What You're Doing:
```
Review how well Agent (from Stage 2) did at verification
Measure: Did it correctly identify good/bad scripts?
Goal: Understand accuracy for future improvements
```

### Step-by-Step Instructions:

```bash
# Analyze Agent decisions:
python3 << 'EOF'
import json
from pathlib import Path

approved_dir = Path("data/approved_scripts")
agent_decisions = []

for metadata_file in approved_dir.glob("*_metadata.json"):
    with open(metadata_file) as f:
        metadata = json.load(f)
    
    agent_decisions.append({
        "script_id": metadata["script_id"],
        "agent_result": metadata.get("agent_verification_passed"),
        "topic": metadata.get("topic")
    })

total = len(agent_decisions)
passed = sum(1 for d in agent_decisions if d["agent_result"])
accuracy = (passed / total) * 100 if total else 0

print(f"Agent Verification Analysis:")
print(f"  Total scripts: {total}")
print(f"  Passed: {passed}")
print(f"  Agent Accuracy: {accuracy:.1f}%")

if accuracy >= 80:
    print(f"✅ Agent verification is working well")
else:
    print(f"⚠️ Agent accuracy < 80%, may need prompt adjustment")
EOF
```

**Success Criteria for Day 5:**
- ✅ Agent accuracy measured
- ✅ Findings documented
- ✅ No action needed unless accuracy < 70%

---

## 📋 DAY 6: TONE ANALYTICS

### What You're Doing:
```
Track which tones were used and performance
Prepare data for future optimization
```

### Step-by-Step Instructions:

```bash
# Log tone performance:
python3 << 'EOF'
import json
from pathlib import Path
from collections import defaultdict

approved_dir = Path("data/approved_scripts")
tone_stats = defaultdict(lambda: {"count": 0, "passed_review": 0})

for metadata_file in approved_dir.glob("*_metadata.json"):
    with open(metadata_file) as f:
        metadata = json.load(f)
    
    tone = metadata.get("tone_used", "unknown")
    tone_stats[tone]["count"] += 1
    
    # Check if passed human review (you'll log this)
    # For now, assume all that got to Day 3 are tracked

print("Tone Performance:")
for tone, stats in tone_stats.items():
    print(f"  {tone}: {stats['count']} videos")

# Save for Stage 6 optimization
Path("data/tone_analytics.json").write_text(
    json.dumps(dict(tone_stats), indent=2)
)
print("\n✅ Tone analytics saved to data/tone_analytics.json")
EOF
```

**Success Criteria for Day 6:**
- ✅ Tone usage tracked
- ✅ Analytics data saved
- ✅ Ready for future optimization

---

## 📋 DAY 7: FINAL ANALYSIS & GO/NO-GO DECISION

### What You're Doing:
```
Calculate final accuracy scores
Decide: GO to Stage 4 or FIX issues?
```

### Step-by-Step Instructions:

```bash
# Final analysis:
python3 << 'EOF'
import json
from src.quality.quality_gates import QualityGates

# Load all your results from Days 1-6
gates = QualityGates()

# Populate results from your logging:
results = {
    # From fact_check logs + human review logs
}

accuracy = gates.calculate_accuracy()

print("=" * 50)
print("STAGE 3 FINAL RESULTS")
print("=" * 50)
print(f"Gate 3 (Fact-check): {accuracy['gate_3_accuracy']:.1%} (need 75-85%)")
print(f"Gate 4 (Human review): {accuracy['gate_4_accuracy']:.1%} (need 80%+)")
print(f"Combined: {accuracy['combined_accuracy']:.1%}")
print()

# Decision logic:
gate_3_ok = 0.75 <= accuracy['gate_3_accuracy'] <= 0.85
gate_4_ok = accuracy['gate_4_accuracy'] >= 0.80

if gate_3_ok and gate_4_ok:
    print("✅ ✅ GO TO STAGE 4")
    decision = "GO"
else:
    print("❌ NO-GO - FIX ISSUES")
    if not gate_3_ok:
        print(f"   - Gate 3 outside range: {accuracy['gate_3_accuracy']:.1%}")
    if not gate_4_ok:
        print(f"   - Gate 4 below threshold: {accuracy['gate_4_accuracy']:.1%}")
    decision = "NO-GO"

print()
print(f"DECISION: {decision}")
print("=" * 50)

# Save decision to file
with open("data/stage_3_decision.json", "w") as f:
    json.dump({
        "decision": decision,
        "accuracy": accuracy
    }, f, indent=2)
EOF
```

### If NO-GO:
```
1. Identify which gate failed
2. Review STAGE_3_FIXES_AND_CLARIFICATIONS.md
3. Adjust fact-check prompts or human review criteria
4. Regenerate 5 new test videos
5. Rerun Days 1-7
6. Until both gates pass
```

**Success Criteria for Day 7:**
- ✅ Final accuracy calculated
- ✅ Both gates meet targets
- ✅ GO decision made
- ✅ Results documented

---

## 📊 STAGE 3 SUCCESS CHECKLIST

Must all be ✅ to proceed to Stage 4:

**Days 1-2 (Fact-Check):**
- [ ] FactChecker class implemented
- [ ] fact_check_prompts.json created
- [ ] 5 scripts fact-checked
- [ ] Flagged claims verified by you
- [ ] Corrections logged

**Day 3 (Human Review):**
- [ ] FinalReviewer class implemented
- [ ] final_review_checklist.json created
- [ ] 5 videos reviewed (≤10 min each)
- [ ] APPROVE/REJECT decisions made
- [ ] Rejection reasons documented

**Day 4 (Quality Gates):**
- [ ] QualityGate class implemented
- [ ] Gate 3 accuracy measured
- [ ] Gate 4 approval measured
- [ ] Combined accuracy calculated

**Day 5-6 (Analysis):**
- [ ] Agent accuracy analyzed
- [ ] Tone analytics tracked
- [ ] Findings documented

**Day 7 (Final Decision):**
- [ ] Combined accuracy 75-85% ✅
- [ ] Human approval 80%+ ✅
- [ ] GO decision confirmed
- [ ] Ready for Stage 4

---

## 🚀 READY FOR STAGE 3?

### Before You Start:
1. ✅ Run PRE_STAGE_3_VERIFICATION_CHECKLIST.md
2. ✅ All checks passed?
3. ✅ Read STAGE_3_FIXES_AND_CLARIFICATIONS.md
4. ✅ Understand the fixes and clarifications

### Then:
1. Follow this Day-1-7 guide
2. Implement each component
3. Test as you go
4. On Day 7, make GO/NO-GO decision

### Key Reminders:
- 🔴 Use ChatGPT/Claude for fact-checking (NOT DeepSeek)
- 🟡 Gate 3 target: 75-85% (NOT 80%+ like Gate 2)
- 🟡 Gate 4 target: 80%+
- 🟢 BOTH must pass to go to Stage 4

---

**You're ready! Start Stage 3! 🚀**

