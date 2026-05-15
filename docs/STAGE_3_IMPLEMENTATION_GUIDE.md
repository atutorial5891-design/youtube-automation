# STAGE 3 IMPLEMENTATION GUIDE
**Status:** Ready to Execute  
**Date:** May 15, 2026  
**Duration:** 7 days (1-2 hours per day)  
**Outcome:** GO/NO-GO decision for Stage 4 (YouTube upload)

---

## 📋 QUICK START

You have 3 Cursor implementation prompts:

| Prompt | Days | Time | What You Build |
|--------|------|------|-----------------|
| **Session 1** | 1-2 | 2-3 hrs | Fact-Checker class + config + 5 reports |
| **Session 2** | 3 | 1-2 hrs | Human Reviewer class + 5 decisions |
| **Session 3** | 4-7 | 1-2 hrs/day | Quality Gates + Analysis + Final Decision |

---

## 🚀 STEP-BY-STEP EXECUTION

### BEFORE YOU START (5 minutes)

✅ **Verify mock data created:**
```bash
cd ~/projects/YouTube-Automation/
ls -lh data/approved_scripts/*_metadata.json | wc -l
# Should show: 5 files
```

✅ **Check you have all required Cursor prompts:**
- STAGE_3_CURSOR_PROMPT_SESSION_1_DAYS_1_2.md
- STAGE_3_CURSOR_PROMPT_SESSION_2_DAY_3.md
- STAGE_3_CURSOR_PROMPT_SESSION_3_DAYS_4_7.md

---

## 📅 DAY-BY-DAY EXECUTION

### **DAYS 1-2: FACT-CHECK MODULE**

**Time:** 2-3 hours total (1-1.5 hours per day)

1. Open Cursor
2. Navigate to ~/projects/YouTube-Automation/
3. Open: STAGE_3_CURSOR_PROMPT_SESSION_1_DAYS_1_2.md
4. **Copy the entire prompt block** (from "PROJECT CONTEXT" to end)
5. Paste into Cursor
6. Run: `pytest tests/test_fact_checker.py -v`
7. Verify: 5 files in logs/fact_check_reports/

**Output Expected:**
- ✅ config/fact_check_prompts.json
- ✅ src/quality/fact_checker.py
- ✅ src/core/stage3_loader.py
- ✅ tests/test_fact_checker.py
- ✅ logs/fact_check_reports/ (5 JSON files)

**Success Criteria:**
```bash
# All these should exist:
ls logs/fact_check_reports/*_fact_check.json
pytest tests/test_fact_checker.py -v  # Should pass
```

---

### **DAY 3: HUMAN FINAL REVIEW**

**Time:** 1-2 hours

1. Verify Session 1 complete (5 fact-check reports exist)
2. Open: STAGE_3_CURSOR_PROMPT_SESSION_2_DAY_3.md
3. **Copy the entire prompt block**
4. Paste into Cursor
5. Run: `pytest tests/test_final_reviewer.py -v`
6. Verify: 5 files in logs/human_reviews/

**Output Expected:**
- ✅ config/final_review_checklist.json
- ✅ src/quality/final_reviewer.py
- ✅ src/quality/review_display.py
- ✅ src/core/review_orchestrator.py
- ✅ tests/test_final_reviewer.py
- ✅ logs/human_reviews/ (5 JSON files)

**Success Criteria:**
```bash
# All these should exist:
ls logs/human_reviews/*_human_review.json
pytest tests/test_final_reviewer.py -v  # Should pass
```

---

### **DAYS 4-7: QUALITY GATES & ANALYSIS**

**Time:** 1-2 hours per day (4 days total)

1. Verify Sessions 1-2 complete
2. Open: STAGE_3_CURSOR_PROMPT_SESSION_3_DAYS_4_7.md
3. **Copy the entire prompt block**
4. Paste into Cursor
5. **Important:** This prompt is large - Cursor may split it into multiple sessions
6. Complete all requirements in order

**Days 4-7 Breakdown:**

**Day 4 - Quality Gates (1 hr):**
- Create QualityGates class
- Validate Gate 3 (fact-check 75-85%)
- Validate Gate 4 (human approval ≥80%)
- Run: `pytest tests/test_quality_gates.py -v`

**Day 5 - Agent Analysis (1 hr):**
- Create AgentAnalyzer class
- Analyze Stage 2 agent decisions
- Identify patterns
- Run: `pytest tests/test_agent_analyzer.py -v`

**Day 6 - Tone Analytics (1 hr):**
- Create ToneAnalytics class
- Track tone performance by approval rate
- Generate recommendations
- Run: `pytest tests/test_tone_analytics.py -v`

**Day 7 - Final Decision (1 hr):**
- Create FinalDecisionEngine class
- Make GO/NO-GO decision
- Generate final report
- Run: `pytest tests/test_stage3_complete.py -v`

**Output Expected:**
- ✅ src/quality/quality_gates.py
- ✅ src/analysis/agent_analyzer.py
- ✅ src/analysis/tone_analytics.py
- ✅ src/analysis/final_decision.py
- ✅ src/stage3_orchestrator.py
- ✅ All test files
- ✅ logs/stage_3_final_report.json

**Success Criteria:**
```bash
# All tests pass
pytest tests/test_quality_gates.py -v
pytest tests/test_agent_analyzer.py -v
pytest tests/test_tone_analytics.py -v
pytest tests/test_stage3_complete.py -v

# Final report exists
ls -lh logs/stage_3_final_report.json
```

---

## ✅ FINAL VERIFICATION (Day 7 End)

Run this comprehensive check:

```bash
#!/bin/bash
echo "=========================================="
echo "STAGE 3 COMPLETE VERIFICATION"
echo "=========================================="

echo ""
echo "FILES CREATED:"
echo "  Session 1 (Days 1-2):"
ls -1 logs/fact_check_reports/*_fact_check.json 2>/dev/null | wc -l | xargs echo "    Fact-check reports:"
echo "    config/fact_check_prompts.json: $([ -f config/fact_check_prompts.json ] && echo '✅' || echo '❌')"

echo ""
echo "  Session 2 (Day 3):"
ls -1 logs/human_reviews/*_human_review.json 2>/dev/null | wc -l | xargs echo "    Human review files:"
echo "    config/final_review_checklist.json: $([ -f config/final_review_checklist.json ] && echo '✅' || echo '❌')"

echo ""
echo "  Session 3 (Days 4-7):"
echo "    src/quality/quality_gates.py: $([ -f src/quality/quality_gates.py ] && echo '✅' || echo '❌')"
echo "    src/analysis/agent_analyzer.py: $([ -f src/analysis/agent_analyzer.py ] && echo '✅' || echo '❌')"
echo "    src/analysis/tone_analytics.py: $([ -f src/analysis/tone_analytics.py ] && echo '✅' || echo '❌')"
echo "    src/analysis/final_decision.py: $([ -f src/analysis/final_decision.py ] && echo '✅' || echo '❌')"
echo "    logs/stage_3_final_report.json: $([ -f logs/stage_3_final_report.json ] && echo '✅' || echo '❌')"

echo ""
echo "TESTS PASSING:"
echo "    Fact-Checker: $(pytest tests/test_fact_checker.py -q 2>&1 | tail -1)"
echo "    Final Reviewer: $(pytest tests/test_final_reviewer.py -q 2>&1 | tail -1)"
echo "    Quality Gates: $(pytest tests/test_quality_gates.py -q 2>&1 | tail -1)"
echo "    Agent Analyzer: $(pytest tests/test_agent_analyzer.py -q 2>&1 | tail -1)"
echo "    Tone Analytics: $(pytest tests/test_tone_analytics.py -q 2>&1 | tail -1)"
echo "    Stage 3 Complete: $(pytest tests/test_stage3_complete.py -q 2>&1 | tail -1)"

echo ""
echo "DECISION:"
python3 << 'EOFPY'
import json
try:
    with open('logs/stage_3_final_report.json') as f:
        report = json.load(f)
    decision = report.get('decision', 'UNKNOWN')
    print(f"  Final Decision: {decision}")
    if decision in ['GO', 'GO_WITH_CAUTION']:
        print(f"  Status: ✅ READY FOR STAGE 4")
    else:
        print(f"  Status: ❌ REQUIRES REWORK")
except Exception as e:
    print(f"  ERROR: {e}")
EOFPY

echo ""
echo "=========================================="
echo "STAGE 3 VERIFICATION COMPLETE"
echo "=========================================="
```

Run and save output:
```bash
bash verify_stage_3.sh | tee stage_3_verification.log
```

---

## 🎯 EXPECTED OUTCOMES

### **If Decision = GO**
```
✅ Stage 3 PASSED
✅ All 5 videos ready for Stage 4 (YouTube upload)
✅ Proceed to Stage 4 implementation
```

**Metrics:**
- Gate 3 Accuracy: 75-85% ✅
- Gate 4 Approval Rate: ≥80% ✅
- Agent Accuracy: 80%+ ✅
- Zero policy violations ✅

### **If Decision = GO_WITH_CAUTION**
```
⚠️ Stage 3 MARGINAL
⚠️ Most videos ready, some flagged for extra review
⚠️ Can proceed with caution, but review flagged videos
```

**Action:**
- Review flagged videos manually
- Decide: proceed or regenerate

### **If Decision = NO-GO**
```
❌ Stage 3 FAILED
❌ 1+ gates did not pass
❌ MUST regenerate videos and re-run Stage 3
```

**Action:**
- Identify which gate(s) failed
- Regenerate using Stage 2
- Re-run Stage 3 from Day 1

---

## 📚 REFERENCE DOCUMENTS

**Use these if you hit issues:**

| Problem | Document |
|---------|----------|
| Need to understand prompt | STAGE_3_FIXES_AND_CLARIFICATIONS.md |
| Tests failing | STAGE_2_TROUBLESHOOTING.md |
| Can't load Stage 2 data | STAGE_2_TO_STAGE_3_ALIGNMENT_ANALYSIS.md |
| Verification checklist | PRE_STAGE_3_VERIFICATION_CHECKLIST.md |

---

## 🔍 HOW EACH PROMPT WORKS

### **Session 1 Prompt (Days 1-2)**
- **Input:** Mock videos in data/approved_scripts/
- **Process:** Extract claims → Assess risk → Generate reports
- **Output:** 5 fact-check reports
- **API Calls:** ChatGPT (for accuracy, not DeepSeek)
- **Cost:** ~$0.08-0.12 per video (total ~$0.50)

### **Session 2 Prompt (Day 3)**
- **Input:** 5 fact-check reports
- **Process:** Display 5-item checklist → Record decisions → Log reviews
- **Output:** 5 human review decisions
- **API Calls:** None (manual review)
- **Cost:** $0 (human time only)

### **Session 3 Prompt (Days 4-7)**
- **Input:** All reports + reviews from Sessions 1-2
- **Process:** Validate gates → Analyze patterns → Make decision
- **Output:** Final report + GO/NO-GO decision
- **API Calls:** ChatGPT for analysis (optional)
- **Cost:** ~$0.02-0.05 (total)

---

## ⚠️ COMMON PITFALLS & SOLUTIONS

### **Pitfall 1: Cursor prompt too long**
**Solution:** Copy in chunks if needed. The prompt is split logically:
- Days 4-7 can be done as separate sessions if needed

### **Pitfall 2: Tests fail due to missing imports**
**Solution:** Ensure src/ directories exist:
```bash
mkdir -p src/analysis
mkdir -p logs/fact_check_reports
mkdir -p logs/human_reviews
```

### **Pitfall 3: API key errors**
**Solution:** Verify credentials/api_keys.txt exists:
```bash
cat credentials/api_keys.txt | grep OPENAI
# Should show your ChatGPT API key
```

### **Pitfall 4: No decision report generated**
**Solution:** Run orchestrator explicitly:
```python
from src.stage3_orchestrator import Stage3Orchestrator
orchestrator = Stage3Orchestrator(api_key=your_key)
result = orchestrator.run_stage_3_complete()
```

---

## 📞 WHEN TO USE EACH PROMPT

**Use Session 1 (Days 1-2) when:**
- ✅ Mock data created
- ✅ You want to implement fact-checking
- ❌ Don't use if Session 1 already done

**Use Session 2 (Day 3) when:**
- ✅ Session 1 complete (5 fact-check reports exist)
- ✅ You want to implement human review
- ❌ Don't use if Session 2 already done

**Use Session 3 (Days 4-7) when:**
- ✅ Sessions 1-2 complete (all reports + reviews exist)
- ✅ You want to implement gates, analysis, decision
- ❌ Don't use if Session 3 already done

---

## 🎯 SUCCESS CHECKLIST

**End of Stage 3, check these:**

- [ ] All 3 Cursor sessions completed
- [ ] 5 fact-check reports generated
- [ ] 5 human review decisions generated
- [ ] All quality gates validated
- [ ] Agent analysis completed
- [ ] Tone analytics completed
- [ ] Final report generated
- [ ] All tests passing (6 test suites)
- [ ] Decision is GO or GO_WITH_CAUTION
- [ ] logs/stage_3_final_report.json exists

If all ✅, you're ready for Stage 4!

---

## 🚀 NEXT: STAGE 4

Once Stage 3 PASSES with GO decision:

1. Review Stage 3 final report
2. Document any findings
3. Prepare Stage 4 implementation (YouTube upload)
4. Use Stage 4 Cursor prompts

---

## 📝 NOTES

**Why 3 sessions?**
- Session 1: Fact-checking (complex, needs ChatGPT)
- Session 2: Human review (simpler, manual decisions)
- Session 3: Analysis & decision (complex logic, multiple modules)

**Token Management:**
- Each prompt sized for typical Cursor context
- If Session 3 too large, split into two Cursor sessions:
  - Session 3a: Days 4-5 (Gates + Agent)
  - Session 3b: Days 6-7 (Analytics + Decision)

**Testing Strategy:**
- Each session has dedicated tests
- All tests use mock APIs (no real API calls)
- Tests validate logic without external dependencies
- Can run any test anytime to verify correctness

---

## ✅ YOU'RE READY!

**Timeline:**
- Days 1-2: 2-3 hours
- Day 3: 1-2 hours  
- Days 4-7: 1-2 hours per day

**Total: ~7-10 hours of work over 7 days**

Next action: **Start with Session 1 prompt!** 🚀
