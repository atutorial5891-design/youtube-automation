# STAGE 5 EXECUTION PLAN - TESTING, VALIDATION & OPTIMIZATION
**Timeline:** Week 3 (7 days)  
**Daily Commitment:** 2-3 hours  
**Human Time:** 5-10 min per video (final review x 5)  
**Estimated Total:** 15-20 hours

---

## OVERVIEW

**What Gets Done:**
1. End-to-end testing (5 complete videos)
2. Performance baseline measurement
3. Load testing (10 consecutive videos)
4. Quality metrics evaluation
5. Error handling verification
6. Agent verification accuracy assessment
7. Tone variation effectiveness assessment

---

## ⚠️ CRITICAL: API ALLOCATION IN STAGE 5

**Agent Accuracy Measurement:** **ChatGPT/Claude ONLY** ⭐

The Agent accuracy you measure in Day 5 is the accuracy of your **ChatGPT/Claude Agent verification system** from Stage 2.

- ✅ **Day 1-2:** Test with DeepSeek (topics) + ChatGPT/Claude (scripts/verification)
- ✅ **Day 3:** Load test with full pipeline (DeepSeek + ChatGPT/Claude)
- ✅ **Day 5:** **Measure ChatGPT/Claude Agent accuracy** (Gate 2 threshold: ≥80%)
- ❌ **NEVER:** Measure DeepSeek Agent accuracy (DeepSeek is not used for verification)

**Gate 2 Requirement:** Agent accuracy must be ≥80% to proceed to Stage 6.

See **API_ALLOCATION_BY_STAGE.md** for complete allocation breakdown.

---

## DAY-BY-DAY EXECUTION

### DAY 1-2: End-to-End Testing (4-5 hours)

**Objectives:**
- Run full pipeline 5 times
- Generate 5 complete test videos
- Document timing for each stage
- Identify bottlenecks

**Test Videos:**
- Video 1: Tutorial topic
- Video 2: Entertainment topic
- Video 3: Educational topic
- Video 4: Lifestyle topic
- Video 5: News topic

**For Each Video Document:**
```
- Topic generation: X min
- Script generation: X min
- Agent verification: X min (including retries if any)
- Tone selection & variation: X min
- Fact-check: X min
- TTS/Images/Video: X min
- Your final review: X min
- TOTAL: X min
```

**Success Criteria:**
- All 5 videos complete
- All timing documented
- Bottlenecks identified
- Baseline performance established

---

### DAY 3: Load Testing (3-4 hours)

**Objectives:**
- Run 10 consecutive videos (1 full day simulation)
- Monitor system resources (M4 Max)
- Verify stability
- Identify any issues under load

**Monitoring During Load Test:**
```
Activity Monitor watch:
- RAM usage (target: never exceed 30GB / 80%)
- GPU utilization (expect 70-90% during image gen)
- GPU memory: ~10-12GB peak
- CPU cores used
- Thermal: <40°C
- Any crashes or errors?
```

**Success Criteria:**
- 10 consecutive videos successful
- System stable
- No memory issues
- No thermal issues
- Ready for 5-7 videos/day production

---

### DAY 4: Quality Metrics Baseline (3-4 hours)

**Objectives:**
- Evaluate 5 test videos quality
- Establish quality scorecard
- Create baseline metrics
- Document quality standards

**Quality Evaluation (1-10 scale):**
```
- Clarity (is script easy to understand?)
- Flow (does it read naturally?)
- Engagement (does it have hooks?)
- Audio quality (clear, paced well?)
- Video quality (1080p, no glitches?)
- Overall quality score
```

**Calculate Baseline:**
```
Video 1 overall: 8.5/10
Video 2 overall: 8.0/10
Video 3 overall: 8.8/10
Video 4 overall: 7.9/10
Video 5 overall: 8.3/10
BASELINE AVERAGE: 8.3/10
```

**Success Criteria:**
- Quality baseline established
- All 5 videos meet minimum (>7/10)
- Standards documented
- Ready for production

---

### DAY 4: Integration Testing (Stage 2→4 Pipeline) (2-3 hours)

**Objectives:**
- Test complete pipeline end-to-end
- Verify Stage 2, Stage 3, and Stage 4 work together
- Confirm video generation integrates with publishing

**Integration Test (Generate → Fact-Check → Publish):**

```python
python3 << 'EOF'
from src.orchestrator import VideoProductionOrchestrator
from src.fact_checker import FactChecker
from src.youtube_uploader import YouTubeUploader

# Step 1: Generate video (Stage 2)
orchestrator = VideoProductionOrchestrator()
result = orchestrator.run_pipeline(topic="Test: Sleep Quality")
if not result["success"]:
    print("❌ Generation failed")
    exit(1)

# Step 2: Fact-check (Stage 3)
fact_checker = FactChecker()
fc_result = fact_checker.fact_check_script(
    script_id="test_1",
    script_text=result["script"],
    topic="health"
)
print(f"Flagged claims: {len(fc_result['flagged_claims'])}")

# Step 3: Publish (Stage 4)
uploader = YouTubeUploader()
upload_result = uploader.upload_video(
    video_file_path=result["video_file"],
    metadata=result["metadata"]
)
if not upload_result["success"]:
    print(f"❌ Upload failed: {upload_result['error']}")
    exit(1)

print(f"✅ Integration test passed: Video {upload_result['video_id']} published")
EOF
```

**Success Criteria:**
- ✅ Generation works
- ✅ Fact-check works
- ✅ Publishing works
- ✅ Full pipeline operational

---

### DAY 5: Agent Accuracy Measurement (2-3 hours)

**Objectives:**
- Measure Agent verification accuracy
- Calculate percentage of scripts passing first attempt
- Ensure ≥80% before proceeding

**Agent Accuracy Measurement Procedure:**

```python
def measure_agent_accuracy():
    """
    How many scripts pass Agent verification on FIRST attempt?
    Target: ≥80% (at least 4 of 5 pass on attempt 1)
    """
    
    verification_log = read_log("logs/agent_verification.log")
    
    test_cases = [
        {"video": 1, "topic": "Sleep", "passed_on_attempt": 1},  # ✅
        {"video": 2, "topic": "Coffee", "passed_on_attempt": 1},  # ✅
        {"video": 3, "topic": "Exercise", "passed_on_attempt": 2},  # ⚠️
        {"video": 4, "topic": "Meal Prep", "passed_on_attempt": 1},  # ✅
        {"video": 5, "topic": "Stress", "passed_on_attempt": 1},  # ✅
    ]
    
    passed_first_attempt = sum(1 for t in test_cases if t["passed_on_attempt"] == 1)
    total = len(test_cases)
    accuracy = (passed_first_attempt / total) * 100
    
    print(f"Agent Accuracy: {accuracy}% ({passed_first_attempt}/{total} passed on first attempt)")
    
    if accuracy >= 80:
        print("✅ Meets threshold (≥80%)")
    else:
        print("❌ Below threshold (<80%)")
        print("Action: Return to Stage 2, improve Agent verification prompts")
    
    return accuracy >= 80
```

**Example Report:**

```
Video 1: PASS on attempt 1 ✅
Video 2: PASS on attempt 1 ✅
Video 3: FAIL on attempt 1 → PASS on attempt 2 ⚠️
Video 4: PASS on attempt 1 ✅
Video 5: PASS on attempt 1 ✅

Agent Accuracy: 4/5 = 80% ✅ (meets ≥80% threshold)
```

**Success Criteria:**
- ✅ Accuracy ≥80% (at least 4 of 5 pass on first attempt)
- If <80%: Document why and return to Stage 2 to improve prompts

---

### DAY 6: Quality Metrics & Tone Assessment (3-4 hours)

**Quality Evaluation (1-10 scale):**
```
Video 1: Clarity 8.5, Flow 8.8, Engagement 8.4, Audio 8.3, Video 8.6, Overall 8.5
Video 2: Clarity 7.9, Flow 7.8, Engagement 7.9, Audio 7.9, Video 8.0, Overall 7.9
Video 3: Clarity 8.8, Flow 8.9, Engagement 8.7, Audio 8.8, Video 9.0, Overall 8.8
Video 4: Clarity 7.8, Flow 7.9, Engagement 7.8, Audio 7.9, Video 8.0, Overall 7.9
Video 5: Clarity 8.3, Flow 8.2, Engagement 8.3, Audio 8.2, Video 8.3, Overall 8.3

BASELINE AVERAGE: 8.3/10 ✅ (meets ≥7/10 threshold)
```

**Tone Variation Assessment:**
- Video 1 tone: Professional Educational ✅
- Video 2 tone: Quick & Direct ✅
- Video 3 tone: Energetic Motivational ✅
- Video 4 tone: Conversational Storytelling ✅
- Video 5 tone: Curious Explainer ✅

Diversity: 5 different tones across 5 videos ✅ (100% diversity)

**Success Criteria:**
- Quality baseline: ≥7/10 average
- All videos >7/10 individually
- Tone diversity: Each video has different tone
- No problematic tones

---

### DAY 6: Error Handling Verification (2-3 hours)

**Objectives:**
- Simulate failures (API errors, network issues, corrupted files)
- Verify recovery mechanisms
- Test all error paths
- Document recovery procedures

**Simulate Failures:**
```
1. ChatGPT API error
   → Should: Retry with backoff, timeout gracefully
   → Verify: Error logged, not stuck

2. Google TTS failure
   → Should: Log error, flag for retry
   → Verify: Script doesn't hang

3. Ollama crash
   → Should: Detect, restart if possible
   → Verify: Graceful failure

4. YouTube upload failure
   → Should: Resume capability, retry logic
   → Verify: No data loss

5. Corrupted video file
   → Should: Detect, alert, skip
   → Verify: Pipeline continues with next video
```

**Success Criteria:**
- All error paths tested
- Recovery working correctly
- Errors logged properly
- Pipeline resilient

---

### DAY 7: Final Sign-Off & Go/No-Go Decision (2-3 hours)

**Objectives:**
- Complete all verification tasks
- Create final report
- Go/no-go decision for Stage 6

**Final Checklist:**
```
✅ 5 complete test videos successful
✅ Load test (10 videos) successful
✅ Quality baseline established (avg 8.3/10)
✅ Agent verification accurate (80%+)
✅ Tone variation working
✅ Error handling verified
✅ Performance baseline: 50-70 min/video
✅ Your human review: 5-10 min/video
✅ Daily capability: 5-7 videos/day sustainable

All criteria met? → GO TO STAGE 6
Any criteria missing? → FIX, then GO TO STAGE 6
```

**Create Stage 5 Completion Report:**
- Performance baseline
- Quality baseline
- Accuracy metrics
- Load test results
- Recommendations

**Success Criteria:**
- Final report complete
- Go/no-go clear
- Ready for soft launch

---

### DAY 7: Final Sign-Off & Go/No-Go Decision (2-3 hours)

**Stage 5 SUCCESS CHECKLIST - GO/NO-GO DECISION**

**Must ALL be ✅ to proceed to Stage 6:**

- [ ] **Integration Testing Complete**
  - [ ] Stage 2 → Stage 3 → Stage 4 pipeline works
  - [ ] Video generates successfully
  - [ ] Fact-check completes
  - [ ] Publishing to YouTube succeeds

- [ ] **Agent Accuracy ≥80%**
  - [ ] Accuracy measured explicitly
  - [ ] At least 4 of 5 scripts passed on first attempt
  - [ ] Accuracy percentage: _____% (must be ≥80%)
  - [ ] If <80%: Return to Stage 2, improve prompts, re-test

- [ ] **Quality Baseline ≥7/10**
  - [ ] 5 test videos evaluated
  - [ ] Average quality: _____/10 (must be ≥7)
  - [ ] All individual videos >7/10
  - [ ] If <7/10: Investigate cause and improve

- [ ] **Performance Baseline Documented**
  - [ ] Average video time: _____ min (target 50-70)
  - [ ] GPU peak memory: _____ GB (<20 target)
  - [ ] Load test (10 videos): Successful
  - [ ] System stable, no crashes

- [ ] **Tone Variation Working**
  - [ ] Each of 5 videos has different tone
  - [ ] Tone diversity: ____% (should be ≥80%)
  - [ ] No problematic tone combinations

- [ ] **Error Handling Verified**
  - [ ] All 5 error scenarios tested
  - [ ] Recovery working correctly
  - [ ] Errors logged properly

**GO TO STAGE 6?**
- If ALL boxes ✅: YES, PROCEED  
- If ANY ⚠️ or ❌: NO, FIX and retry

**Signed off by:** _____________ **Date:** _______

---

## NEXT STAGE

→ Move to **STAGE 6: Soft Launch & Iteration**

