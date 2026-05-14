# STAGE 3 EXECUTION PLAN - QUALITY GATES & REVIEW SYSTEMS
**Timeline:** Week 2 (7 days)  
**Daily Commitment:** 1-2 hours (Development only)  
**Human Time on Content:** 5-10 min per video (final review)  
**Estimated Total:** 10-15 hours of coding work

---

## OVERVIEW

**What Gets Built:**
1. Agent-assisted fact-checking system
2. Human final review checklist (CRITICAL items only)
3. Quality gate validation
4. Verification failure analysis
5. Tone performance tracking

**Key Principle:**
- Agent assists, human decides
- Streamlined checklist (5-10 min per video)
- Clear approval/rejection criteria

---

## ⚠️ CRITICAL: API ALLOCATION IN STAGE 3

**Agent Verification Uses:** **ChatGPT/Claude ONLY** ⭐

All Agent-related tasks in this stage use ChatGPT/Claude:
- ✅ **Day 1-2:** Fact-check with Agent (ChatGPT/Claude)
- ✅ **Day 5:** Analyze Agent decisions (ChatGPT/Claude)
- ❌ **NEVER:** Use DeepSeek for Agent tasks (accuracy <80%, fails quality gates)

**Why:** Fact-checking accuracy directly impacts YouTube policy compliance. Quality is non-negotiable.

See **API_ALLOCATION_BY_STAGE.md** for detailed allocation by stage.

---

## WORKFLOW: How Stages 2→3 Connect

```
Stage 2 Output (Approved Script) 
    ↓
Stage 3 Day 1-2: Fact-Check
    - Agent extracts claims
    - Flags risky claims
    - You verify flagged claims
    - Log corrections if needed
    ↓
Stage 3 Day 3: Human Final Review
    - Watch video
    - Quick CRITICAL checklist (5 items, 5-10 min)
    - APPROVE or REJECT
    ↓
Stage 3 Day 7: Analysis & Gate
    - Measure combined accuracy
    - Decision: GO to Stage 4 or FIX
```

---

## DAY-BY-DAY EXECUTION

### DAY 1-2: Agent Fact-Check Integration (3-4 hours)

**Objectives:**
- Implement fact-check module that uses Agent to extract claims
- Create risk-flagging system
- Implement correction logging

**Files to Create:**
- `src/fact_checker.py` (main fact-check module)
- `config/fact_check_prompts.json` (Agent prompts)
- `logs/fact_check.log` (logging)

**Implementation Steps:**

```python
# File: src/fact_checker.py

class FactChecker:
    def __init__(self):
        self.agent = load_agent()  # Use Agent from Stage 2
        self.risk_levels = ["safe", "caution", "risk"]
    
    def fact_check_script(self, script_id, script_text, topic):
        """
        Main fact-check function
        Input: Script from Stage 2
        Output: Fact-check report with flagged claims
        """
        # Step 1: Use Agent to extract claims
        claims = self.extract_claims(script_text)
        
        # Step 2: Classify claims by risk
        flagged_claims = []
        safe_claims = []
        for claim in claims:
            risk = self.assess_risk(claim, topic)
            if risk != "safe":
                flagged_claims.append({"claim": claim, "risk": risk})
            else:
                safe_claims.append(claim)
        
        # Step 3: Log findings
        self.log_fact_check(script_id, flagged_claims, safe_claims)
        
        # Step 4: Return report (for human review)
        return {
            "script_id": script_id,
            "total_claims": len(claims),
            "flagged_claims": flagged_claims,
            "safe_claims": len(safe_claims),
            "status": "awaiting_human_review"
        }
    
    def extract_claims(self, script_text):
        """
        Use Agent to extract factual claims from script
        """
        prompt = """Extract all factual claims from this script.
        For example:
        - 'Sleep helps memory' is a claim
        - 'Studies show...' is a claim
        - 'Personal opinion about X' is NOT a factual claim
        
        Return list of claims only, one per line."""
        
        claims = self.agent.call(prompt, script_text)
        return claims.split('\n')  # Parse response
    
    def assess_risk(self, claim, topic):
        """
        Classify claim as safe, caution, or risk
        safe: General knowledge, no verification needed
        caution: Specific claims that need verification
        risk: Could cause policy violations
        """
        risk_keywords = {
            "medical": ["cure", "treat", "prevent", "disease"],
            "legal": ["law", "illegal", "license"],
            "financial": ["invest", "guarantee", "returns"],
            "health": ["dangerous", "toxic", "poison"]
        }
        
        # Check for risk keywords
        for risk_type, keywords in risk_keywords.items():
            if any(kw in claim.lower() for kw in keywords):
                return "risk"
        
        # Check for specific factual claims
        if "studies show" in claim or "research" in claim or "statistics" in claim:
            return "caution"
        
        return "safe"
    
    def log_fact_check(self, script_id, flagged, safe_count):
        """Log fact-check results"""
        log_entry = {
            "timestamp": now(),
            "script_id": script_id,
            "flagged_count": len(flagged),
            "safe_count": safe_count,
            "flagged_claims": flagged
        }
        save_to_log(log_entry)
```

**Human Verification Procedure (Day 1-2, 3-5 min per script):**

```
For each script fact-check report:

1. Read flagged claims list
   Example: "Studies show 70% of people need 8 hours sleep"
   
2. Quick verification (use Google, trusted source, or common knowledge)
   ✅ Correct: "Yes, 70% is accurate per NIH study"
   ⚠️ Questionable: "70% seems high, I think it's closer to 60%"
   ❌ Wrong: "Actually it's variable, 6-9 hours is normal"

3. For each claim:
   ✅ Correct: Log as verified, proceed
   ⚠️ Questionable: Log concern, consider regenerating that section
   ❌ Wrong: Regenerate section or reject script

4. Log corrections
   Format: script_id, claim_id, your_correction, reason
```

**Success Criteria:**
- ✅ Claim extraction accurate (Agent finds 80%+ of actual claims)
- ✅ Risk flagging appropriate (catches policy violations)
- ✅ Human verification completes in ≤5 min per script
- ✅ Corrections logged (tracking what was fixed)
- ✅ 5 test scripts processed, all documented

**Testing (on 5 test scripts from Stage 2):**
```bash
python3 << 'EOF'
# Test 1: Claim extraction
script = "Sleep is important. Studies show 8 hours helps memory. Coffee has caffeine."
claims = extract_claims(script)
assert "Sleep is important" in claims, "Should extract general claims"
assert "Studies show 8 hours helps memory" in claims, "Should extract research claims"
print("✅ Test 1: Claim extraction working")

# Test 2: Risk flagging
medical_claim = "This supplement cures insomnia"
risk = assess_risk(medical_claim, "health")
assert risk == "risk", "Should flag medical claims"
print("✅ Test 2: Risk flagging working")

# Test 3: Full workflow
for i in range(5):
    report = fact_check_script(f"script_{i}", test_scripts[i], "health")
    assert report["status"] == "awaiting_human_review"
print("✅ Test 3: Full workflow working on 5 scripts")
EOF
```

---

### DAY 3: Human Final Review Checklist (2-3 hours)

**Objectives:**
- Create streamlined CRITICAL-only checklist
- Implement approval/rejection form
- Create decision tracking
- Set up logging

**Files to Create:**
- `src/final_reviewer.py`
- `config/final_review_checklist.json`

**Key Functions:**
```python
class FinalReviewer:
    def display_checklist(video_id)        # Show checklist
    def get_human_decision()               # APPROVE or REJECT?
    def log_decision(decision, notes)      # Track approval
    def handle_rejection(reason)           # If rejected: why?
```

**CRITICAL Checklist (5-10 min total):**
```
✅ Content: No misinformation
✅ Audio: Clear, audible, synced
✅ Video: No glitches, quality OK
✅ Metadata: Title, description accurate
✅ Guidelines: No policy violations
```

**Each check: 1-2 min max**

**Success Criteria:**
- Checklist completes in 5-10 min
- Decisions logged
- Rejection reasons clear
- Approval workflow efficient

**Testing:**
- Run on 5 test videos
- Time the process
- Verify logging

---

### DAY 4: Quality Gate Validation (2-3 hours)

**Objectives:**
- Implement multi-stage quality gates
- Create rejection handling
- Add regeneration workflows
- Track quality metrics

**Files to Create:**
- `src/quality_gate.py`

**Gate Levels:**
```
GATE 1: Agent Verification (Stage 2)
→ PASS: Continue to Gate 2
→ FAIL: Regenerate (max 3 retries)

GATE 2: Agent Fact-Check (Stage 3, Day 1-2)
→ OK: Continue to Gate 3
→ CORRECTION: Fix, regenerate audio, continue

GATE 3: Human Final Review (Stage 3, Day 3)
→ APPROVE: Proceed to YouTube upload
→ REJECT: Stop, log reason, don't publish
```

**Success Criteria:**
- All gates functioning
- Rejection paths working
- Quality metrics captured
- Clear decision log

---

### DAY 5: Agent Verification Analysis (1-2 hours)

**Objectives:**
- Analyze Agent verification decisions
- Identify patterns in failures
- Assess accuracy
- Recommend improvements

**Analysis Tasks:**
```
1. Review all Agent decisions from Stage 2 (5 test videos)
2. Questions:
   - Did Agent correctly identify good scripts?
   - Did Agent reject bad scripts?
   - False positives? False negatives?
3. Accuracy rate: [X]% of Agent decisions correct?
4. Refinement needed? If yes, update verification prompt
```

**Documentation:**
- Create verification accuracy report
- Document any adjustments needed
- Log for future reference

**Success Criteria:**
- Accuracy assessed
- Patterns identified
- Any improvements documented

---

### DAY 6: Tone Variation Performance Tracking (1-2 hours)

**Objectives:**
- Implement tone performance logging
- Create analytics dashboard
- Track engagement by tone
- Prepare for optimization

**Files to Create:**
- `src/tone_analytics.py`

**What to Track:**
```
For each video:
- Topic name
- Tone selected
- Variation chosen (1/2/3)
- Later: Engagement metrics (views, CTR, retention)
```

**Future Use (Stage 6+):**
- Which tones drive higher CTR?
- Which tones get more retention?
- Adjust tone selection if patterns emerge

**Success Criteria:**
- Tone logging working
- Analytics ready
- Dashboard functional

---

### DAY 7: Documentation & Testing (2-3 hours)

**Objectives:**
- Complete quality gate documentation
- Test full Stage 3 workflow
- Create user guides
- Verify everything working

**Documentation to Create:**
- QUALITY_GATES_GUIDE.md
- CHECKLIST_INSTRUCTIONS.md
- DECISION_LOG_FORMAT.md
- TROUBLESHOOTING_STAGE_3.md

**Testing Workflow:**
```
For 5 test videos:
1. Run through Agent fact-check
2. Make decisions on corrections
3. Run through human final review
4. Approve/reject
5. Verify logging

Expected: All 5 pass through gates and are approved
```

**Success Criteria:**
- Documentation complete
- Workflow tested end-to-end
- Logging verified
- Ready for Stage 4

---

## DAY 7: Final Analysis & Go/No-Go Decision (2-3 hours)

**Quality Gate Matrix Analysis:**

After processing 5 test videos through full Stage 3 workflow:

```
Video | Agent Verify | Fact-Check | Human Review | Final Status
------|--------------|------------|--------------|-------------
1     | PASS         | No issues  | APPROVE      | ✅ PASS
2     | FAIL→PASS    | 1 correction | APPROVE    | ✅ RECOVERED
3     | PASS         | 2 cautions | APPROVE      | ⚠️ VERIFIED
4     | PASS         | No issues  | REJECT       | ❌ BLOCKED
5     | PASS         | No issues  | APPROVE      | ✅ PASS

Combined Accuracy Calculation:
- Videos passing Agent: 5/5 = 100%
- Videos passing Fact-Check: 4/5 = 80%
- Videos passing Human Review: 4/5 = 80%
- Combined (all three): 4/5 = 80% ✅ (target 75-85%)
```

**Success Metrics:**
- Combined accuracy: 80% (✅ within 75-85% target)
- Fact-check coverage: 5/5 scripts processed
- Human review efficiency: 5-10 min per video ✅
- Zero policy violations detected: YES ✅

**If accuracy outside 75-85% range:**
- If <75%: Agent verification may be broken, return to Stage 2
- If >90%: Agent may be too lenient, improve verification

---

## STAGE 3 SUCCESS CHECKLIST - GO/NO-GO DECISION

**Must ALL be ✅ to proceed to Stage 4:**

- [ ] Fact-check module implemented and tested
  - [ ] Claim extraction working (Agent identifies claims)
  - [ ] Risk flagging appropriate (catches policy violations)
  - [ ] Correction procedure working (you can log corrections)

- [ ] Human final review streamlined
  - [ ] CRITICAL checklist completes in ≤10 min per video
  - [ ] Approval/rejection form working
  - [ ] Decisions logged clearly

- [ ] Quality gate analysis complete
  - [ ] Combined accuracy measured: 75-85% range ✅
  - [ ] If outside range: Issue documented and fix identified

- [ ] 5 test videos processed end-to-end
  - [ ] Stage 2 script → Stage 3 fact-check → Human review
  - [ ] All decisions logged
  - [ ] No unhandled errors

- [ ] Zero YouTube policy issues
  - [ ] No misinformation caught by fact-check
  - [ ] No copyright/trademark concerns
  - [ ] No harmful content detected

**GO TO STAGE 4?**
- If ALL boxes ✅: YES, PROCEED
- If ANY ⚠️ or ❌: NO, fix issue and re-test

**Signed off by:** _____________ **Date:** _______

---

## NEXT STAGE

When Day 7 complete and all gate criteria met:
→ Move to **STAGE 4: YouTube Integration & Publishing**

