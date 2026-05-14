# STAGE TRANSITION GATES & DEPENDENCIES
**Critical Checkpoints Between Stages**

All stages must meet their transition gate criteria before proceeding. These gates prevent broken systems from cascading downstream.

---

## GATE 1: Stage 1 → Stage 2

**Go/No-Go Decision Point: End of Stage 1, Day 5**

### Must ALL Be True To Proceed:

- ✅ Design Logic Validated
  - Agent verification thresholds tested (Test 1 passed)
  - Retry logic (max 3) verified (Test 2 passed)
  - Tone selection randomization tested (Test 3 passed)
  - Tone variation count (2-3) validated (Test 4 passed)

- ✅ All 3 APIs Tested & Working
  - ChatGPT API: Script generation works
  - Google Cloud TTS: Audio generation works
  - YouTube API: Authentication successful

- ✅ Ollama + SDXL Operational
  - Model downloaded and verified
  - Performance baseline: Average ≤25 sec per image
  - GPU memory stable (<15GB during generation)
  - Thermal management OK (<40°C sustained)

- ✅ M4 Max Hardware Verified
  - RAM: 36GB confirmed
  - GPU: 10-core confirmed
  - CPU: 14 cores total confirmed
  - Storage: >300GB free confirmed

- ✅ Project Structure Ready
  - Directory structure created
  - Python venv activated
  - All requirements.txt packages installed
  - Config files created (settings.json, API credentials)

- ✅ Documentation Complete
  - WORKFLOW.md
  - TROUBLESHOOTING.md
  - AGENT_VERIFICATION_SYSTEM.md
  - TONE_LIBRARY.md
  - OLLAMA_BASELINE.md
  - API_LIMITS.md

### If ANY Item Fails:
→ DO NOT PROCEED TO STAGE 2
→ Fix identified issue
→ Re-test
→ Retry gate decision

### Decision:
**GO to Stage 2?** YES / NO
**Signed Off By:** _________________ **Date:** _______

---

## GATE 2: Stage 2 → Stage 3

**Go/No-Go Decision Point: End of Stage 2, Day 10**

### Must ALL Be True To Proceed:

- ✅ Core Automation Complete
  - Orchestrator engine built
  - Script generation working (5 test scripts)
  - Agent verification integrated (retry logic confirmed)
  - Tone variation system working (randomization confirmed)
  - TTS, image gen, video assembly all working

- ✅ Agent Verification Accuracy ≥80%
  - Definition: At least 4 of 5 test scripts passed verification on first attempt
  - Measurement: Count scripts PASS on attempt 1
  - Log location: logs/verification_accuracy.log
  - If accuracy <80%: Return to Stage 2 Day 4, improve prompts, re-test

- ✅ Tone Variation Diversity Confirmed
  - Definition: Each of 5 test videos has a different tone selected
  - Measurement: Check tone_selection.log, verify no tone repeated
  - Expected: At least 3+ different tones selected across 5 videos
  - If diversity <80%: Check random selection logic

- ✅ End-to-End Pipeline Works
  - 5 complete test videos generated (script → video)
  - All stages logged properly
  - Zero unhandled errors in logs

- ✅ Failure Scenarios Tested
  - Failure Test 1 (Agent rejection after 3 retries): PASSED ✅
  - Failure Test 2 (GPU memory under load): PASSED ✅
  - Failure Test 3 (API error recovery): PASSED ✅
  - Failure Test 4 (Missing tone library): PASSED ✅

- ✅ Performance Baseline Documented
  - Average video time per script: 50-70 minutes
  - If outside range: Document reason (e.g., "Slower GPU expected")
  - GPU peak memory: <20GB
  - No thermal issues (sustained <40°C)

### Critical Metrics to Document:
```
Agent Verification Accuracy: ___% (must be ≥80%)
Tone Diversity Score: ___% (must be ≥80%)
Average Video Time: ___ minutes (should be 50-70)
GPU Memory Peak: ___ GB (should be <20)
Unhandled Errors: ___ (must be 0)
Failure Tests Passed: ___/4 (must be 4/4)
```

### If ANY Item Fails:
→ DO NOT PROCEED TO STAGE 3
→ Identify specific issue
→ Fix issue or improve prompts
→ Re-test affected component
→ Retry gate decision

### Decision:
**GO to Stage 3?** YES / NO
**Reason if NO:** _________________________________
**Signed Off By:** _________________ **Date:** _______

---

## GATE 3: Stage 3 → Stage 4

**Go/No-Go Decision Point: End of Stage 3, Day 7**

### Must ALL Be True To Proceed:

- ✅ Quality Gate System Working
  - Fact-check module extracts claims accurately
  - Verification flagging appropriate (risky vs safe)
  - Final review checklist completes in ≤10 min per video

- ✅ 5 Test Videos Processed End-to-End
  - All 5 videos passed through full Stage 3 workflow
  - Fact-check log created for each video
  - Human final review completed for each video
  - Approval/rejection decisions logged

- ✅ Quality Gate Pass Rate ≥75%
  - Definition: At least 4 of 5 test videos pass all gates
  - Calculation: (Videos passing fact-check AND final review) / 5
  - If <75%: Investigate which gate is failing videos

- ✅ Combined Quality Score 75-85%
  - Definition: Measure Agent + Fact-check + Human combined accuracy
  - Calculation: (Correct decisions by all 3) / 5
  - If <75%: Agent verification may need improvement
  - If >90%: Agent may be too lenient

- ✅ Tone Analytics Set Up
  - Tone selection log created
  - Tone performance metrics ready
  - Format: [video_id, topic, tone_selected, variation_number]

- ✅ Zero YouTube Policy Issues
  - No harmful language detected
  - No trademark/copyright concerns flagged
  - No misinformation found in fact-check

### Quality Gate Matrix (Example):
```
Video | Agent Verify | Fact-Check | Human Review | Status
------|--------------|------------|--------------|--------
1     | PASS         | OK         | APPROVE      | ✅ GOOD
2     | FAIL→PASS    | OK         | APPROVE      | ✅ RECOVERED
3     | PASS         | CORRECTION | APPROVE      | ⚠️ VERIFY
4     | PASS         | OK         | APPROVE      | ✅ GOOD
5     | PASS         | OK         | APPROVE      | ✅ GOOD

Pass Rate: 5/5 = 100% ✅ (exceeds 75% requirement)
```

### If ANY Item Fails:
→ DO NOT PROCEED TO STAGE 4
→ If quality <75%: Review Agent verification, may need to return to Stage 2
→ If policy issues found: Improve fact-check prompts
→ Re-test specific problem area
→ Retry gate decision

### Decision:
**GO to Stage 4?** YES / NO
**Quality Pass Rate:** ____% (must be ≥75%)
**Combined Accuracy:** ____% (should be 75-85%)
**Signed Off By:** _________________ **Date:** _______

---

## GATE 4: Stage 4 → Stage 5

**Go/No-Go Decision Point: End of Stage 4, Day 7-8**

### Must ALL Be True To Proceed:

- ✅ YouTube API Authenticated
  - OAuth2 flow completed
  - Test channel selected
  - Credentials stored securely

- ✅ Video Upload Working
  - Test upload successful
  - Video uploaded to test channel without errors
  - Metadata (title, description) correct
  - Thumbnail uploaded properly

- ✅ Metadata Generation Working
  - Titles generated properly (≤100 chars, no clickbait)
  - Descriptions generated with AI disclosure
  - Tags generated (5-7 per video, relevant)
  - All validation rules passing

- ✅ Thumbnails Generated & Valid
  - Format: 1280×720px
  - Text readable at small sizes
  - Quality validation passing
  - A/B variants created (2 per video)

- ✅ Publishing Schedule Working
  - APScheduler integration confirmed
  - Scheduling logic: 3 videos/day max
  - Time conflict detection working
  - Test schedule created for 5 videos

- ✅ Analytics API Connected
  - YouTube Analytics API responding
  - Baseline metrics collecting
  - Data refresh verified (24-48hr typical delay noted)

### If ANY Item Fails:
→ DO NOT PROCEED TO STAGE 5
→ Fix YouTube API issue
→ Retry upload with fresh credentials if needed
→ Re-test specific component
→ Retry gate decision

### Decision:
**GO to Stage 5?** YES / NO
**YouTube API Status:** Connected / Not Connected
**Test Upload Status:** Success / Failed
**Signed Off By:** _________________ **Date:** _______

---

## GATE 5: Stage 5 → Stage 6

**Go/No-Go Decision Point: End of Stage 5, Day 7**

### Must ALL Be True To Proceed:

- ✅ End-to-End Pipeline Verified
  - 5 complete test videos generated (script → final video)
  - 10-video load test completed (system stable)
  - Zero crashes, zero memory leaks

- ✅ Quality Baseline Established
  - 5 test videos reviewed manually
  - Quality scores: ≥7/10 average
  - Individual video scores: [____], [____], [____], [____], [____]
  - Average: ____/10 (must be ≥7)

- ✅ Agent Verification Accuracy Validated
  - Measurement: How many scripts passed Agent on first attempt?
  - Target: ≥80% (at least 4 of 5)
  - Actual: ____% (must be ≥80%)
  - If <80%: Return to Stage 2, improve Agent prompts

- ✅ Tone Variation Effectiveness Confirmed
  - Tone diversity: ____% (must be ≥80%)
  - No problematic tones identified
  - Variation generation (2-3 per tone) working

- ✅ Error Handling Tested
  - API timeout recovery: Tested ✓
  - GPU memory pressure: Tested ✓
  - File corruption handling: Tested ✓
  - Network interruption recovery: Tested ✓

- ✅ Performance Metrics Documented
  - Average time per video: ____ minutes (50-70 target)
  - GPU memory peak: ____ GB (<20 target)
  - CPU usage: Normal
  - Thermal management: OK (<40°C)

### Final Sign-Off Checklist:
- [ ] All 5 test videos ≥7/10 quality
- [ ] Agent accuracy ≥80%
- [ ] Tone diversity ≥80%
- [ ] Load test (10 videos) successful
- [ ] Error handling tested
- [ ] Performance documented
- [ ] Ready for soft launch

### If ANY Item Fails:
→ DO NOT PROCEED TO STAGE 6
→ If quality <7/10: Improve script generation or tone selection
→ If Agent accuracy <80%: Return to Stage 2, fix verification prompts
→ Fix identified issue
→ Re-test
→ Retry gate decision

### Decision:
**GO to Stage 6?** YES / NO
**Quality Average:** ____/10 (must be ≥7)
**Agent Accuracy:** ____% (must be ≥80%)
**Signed Off By:** _________________ **Date:** _______

---

## GATE 6: Stage 6 → Stage 7

**Go/No-Go Decision Point: End of Stage 6, Day 7**

### Must ALL Be True To Proceed:

- ✅ Soft Launch Complete
  - 6 videos published successfully (no errors)
  - Zero technical issues during publishing
  - All videos visible on channel

- ✅ YouTube Policy Compliance
  - Zero YouTube strikes received
  - Zero copyright claims (or addressed if any)
  - Zero policy warnings

- ✅ Sustainability Confirmed
  - 5-10 min human review per video: Achievable? YES / NO
  - Daily workflow sustainable? YES / NO
  - No signs of fatigue: YES / NO

- ✅ Initial Audience Feedback
  - Positive feedback: __________
  - Negative feedback: __________
  - Overall tone: Positive / Neutral / Negative
  - Any policy concerns from audience? NO / YES

- ✅ Agent & Tone Systems Performing
  - Agent verification still accurate? YES / NO
  - Tone variation still working? YES / NO
  - No unexpected failures? YES / NO

- ✅ Quality Maintained
  - Published videos ≥7/10 average? YES / NO
  - No quality degradation? YES / NO

### Soft Launch Metrics:
```
Videos Published: 6
YouTube Strikes: 0
Human Review Time: ___ min/video (target 5-10)
Agent Accuracy During Soft Launch: ___% (should be ≥80%)
Tone Diversity: ____% (should be ≥80%)
Average Quality Score: ____/10 (should be ≥7)
Burnout Risk: LOW / MEDIUM / HIGH
```

### If ANY Item Fails:
→ DO NOT PROCEED TO STAGE 7 (PRODUCTION)
→ If YouTube strikes: Investigate cause, improve fact-checking
→ If quality dropped: Debug content generation
→ If Agent failing: May need to return to Stage 2
→ Fix issue
→ Publish 2-3 more videos and re-test
→ Retry gate decision

### Decision:
**GO to Stage 7 (Production)?** YES / NO
**Reason if NO:** _________________________________
**Signed Off By:** _________________ **Date:** _______

---

## MID-STAGE ROLLBACK CRITERIA

At ANY point during ANY stage, if these occur, **STOP immediately and rollback**:

### Critical Rollback Triggers:

1. **Agent Accuracy Below 70%**
   - Action: Rollback to Stage 2, improve Agent prompts
   - Reason: Too many poor scripts getting approved

2. **Quality Score Below 6/10**
   - Action: Rollback to Stage 2 or 3, investigate cause
   - Reason: Content quality unacceptable

3. **YouTube Strike Received**
   - Action: Rollback to Stage 3 (Fact-Check), investigate policy violation
   - Reason: System creating policy-breaking content

4. **System Crashes >2x per week**
   - Action: Rollback to Stage 2, debug crashes
   - Reason: System unstable for production

5. **GPU Thermal >50°C Sustained**
   - Action: Rollback to Stage 1, check GPU settings
   - Reason: Hardware safety issue

6. **GPU Memory Exceeds 30GB**
   - Action: Rollback to Stage 2, optimize memory usage
   - Reason: Memory leak or overflow risk

7. **Burnout Symptoms (Score <4/10)**
   - Action: Rollback Stage 7 pace, take break
   - Reason: Human sustainability critical

---

## SUMMARY TABLE

| Gate | From | To | Key Metric | Threshold | Decision |
|------|------|----|----|-----------|----------|
| 1 | Stage 1 | Stage 2 | Design validation tests | 4/4 passed | GO if all 4 pass |
| 2 | Stage 2 | Stage 3 | Agent accuracy | ≥80% | GO if ≥80% |
| 3 | Stage 3 | Stage 4 | Quality pass rate | ≥75% | GO if ≥75% |
| 4 | Stage 4 | Stage 5 | Upload test | Success | GO if succeeds |
| 5 | Stage 5 | Stage 6 | Quality baseline | ≥7/10 avg | GO if ≥7/10 |
| 6 | Stage 6 | Stage 7 | YouTube strikes | 0 | GO if 0 strikes |

---

## IF YOU GET STUCK AT A GATE

**Question: What if I'm at Gate 3 and accuracy is only 70%?**

Answer:
1. Stop Stage 3
2. Go back to Stage 2
3. Review Agent verification prompts
4. Identify why accuracy is low (too strict? too lenient?)
5. Update prompts
6. Re-test with 5 new scripts
7. Measure accuracy again
8. When ≥80%: Retry Gate 3

**Never force through a gate without meeting criteria.** The gates exist to catch problems early before they compound downstream.

