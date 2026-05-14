# ROLLBACK PROCEDURES
**How to Safely Return to Previous Stages When Issues Occur**

Rollback procedures ensure you can fix problems without losing progress. All rollbacks preserve your code and documentation—only the execution timeline resets.

---

## WHEN TO ROLLBACK

Rollback immediately if:
- Agent verification accuracy drops below 70%
- Quality scores fall below 6/10
- YouTube policy strike received
- System crashes more than 2x per week
- GPU thermal exceeds 50°C
- GPU memory exceeds 30GB
- Security or privacy issue discovered
- Burnout symptoms (satisfaction <4/10)

---

## SCENARIO 1: Agent Verification Accuracy Too Low

**Situation:** End of Stage 5 testing, discovered Agent accuracy only 65% (should be ≥80%)

**Impact:** System rejecting good scripts too often, or accepting bad ones

### Rollback Procedure:

**Step 1: Stop Immediately**
```
→ Do NOT publish any Stage 6 videos
→ Do NOT proceed to production
→ Flag as QUALITY ISSUE - RETURN TO STAGE 2
```

**Step 2: Investigate Root Cause (1-2 hours)**
```bash
# Review Agent verification decisions from Stage 2 + 5
# Log file: logs/verification_decisions.log

Extract and analyze:
- Scripts that Agent rejected (FAIL) - Review these manually
  - Were they actually poor? Or did Agent reject good scripts?
  - Look for false negatives
  
- Scripts that Agent approved (PASS) - Spot check
  - Were they actually good? Or did Agent miss issues?
  - Look for false positives

Count:
- False Negatives (Agent FAIL, but you'd say PASS): ___
- False Positives (Agent PASS, but script was mediocre): ___

Pattern:
Is Agent being too strict? (many false negatives)
Is Agent being too lenient? (many false positives)
```

**Step 3: Identify Specific Problem**
```
Common issues:

❌ Agent too strict:
- Rejecting scripts for minor clarity issues
- Requiring perfection (90+/100)
- Misidentifying creative writing as poor flow

Fix: Lower thresholds in verification_thresholds.json
- OLD: clarity ≥75, flow ≥80, engagement ≥70
- NEW: clarity ≥70, flow ≥75, engagement ≥65

❌ Agent too lenient:
- Accepting scripts with obvious misspellings
- Missing poor engagement hooks
- Not flagging policy issues

Fix: Improve verification prompt in config/agent_prompts.json
- Add specific examples of FAIL cases
- Clarify what "engagement" means
- Add more detailed scoring rubric

❌ Verification prompt unclear:
- Agent not understanding what to evaluate
- Inconsistent scoring

Fix: Rewrite prompt with examples
- Show 3 PASS examples with scores
- Show 3 FAIL examples with scores
- Clarify scoring scale
```

**Step 4: Update Agent System**

If Agent is too strict:
```json
// File: config/verification_thresholds.json
{
  "old_thresholds": {
    "clarity": 75,
    "flow": 80,
    "engagement": 70,
    "overall": 72
  },
  "new_thresholds": {
    "clarity": 70,
    "flow": 75,
    "engagement": 65,
    "overall": 70
  },
  "reason": "Too many false rejections of good scripts",
  "date_changed": "2026-05-15",
  "expected_improvement": "5-10% accuracy increase"
}
```

If Agent prompt needs improvement:
```
// File: config/agent_prompts.json
OLD: "Evaluate script clarity, flow, and engagement. Score 1-100 on each."

NEW: "Evaluate this script carefully:
CLARITY (1-100): Is it easy to understand? No jargon without explanation?
  ✅ PASS example: 'Sleep helps your brain consolidate memories. When you sleep...'
  ❌ FAIL example: 'Circadian rhythms influence sleep architecture...' [too technical]

FLOW (1-100): Does it read naturally? Would you say it aloud like this?
  ✅ PASS example: 'Three things make better sleep. First... Second... Third...'
  ❌ FAIL example: 'Sleep sleep sleep. Good good good. Better better better.' [repetitive]

ENGAGEMENT (1-100): Does it hook the viewer? Would you keep watching?
  ✅ PASS example: 'Only 1% of people know this sleep hack...'
  ❌ FAIL example: 'Sleep is important.' [boring]"
```

**Step 5: Re-test with New Settings (2-3 hours)**
```bash
# Test Agent with improved settings
# Use 5 NEW scripts (different from Stage 2 testing)

python3 << 'EOF'
# Generate 5 test scripts
test_topics = [
  "Morning exercise routines",
  "Healthy snacking tips", 
  "Productivity hacks",
  "Meditation benefits",
  "Nutrition basics"
]

# Run through Agent verification with new thresholds
results = []
for topic in test_topics:
  script = generate_script(topic)
  result = verify_with_new_settings(script)
  results.append(result)
  print(f"{topic}: {result}")

# Calculate new accuracy
correct_decisions = sum(1 for r in results if evaluate_manually(r))
new_accuracy = (correct_decisions / len(results)) * 100
print(f"\nNew Accuracy: {new_accuracy}%")

if new_accuracy >= 80:
  print("✅ Accuracy improved to target")
else:
  print("⚠️ Accuracy still below target, may need further adjustment")
EOF
```

**Step 6: Measure Improvement**
```
Before: 65% accuracy (4/5 wrong decisions too often)
After:  83% accuracy (improved thresholds working)
↳ YES → PROCEED: Can now retry Stage 5

Before: 65% accuracy
After:  72% accuracy (improved but still <80%)
↳ NO → More work needed: Try different approach (see below)
```

**Step 7: If Still Below 80%**
```
Try alternative approaches:

A. Request improvement from Agent:
   - Update prompt with more specific guidance
   - Provide more examples
   - Ask Agent to explain reasoning

B. Add human pre-filter:
   - Have human do quick 1-min scan before Agent
   - Filter out obviously bad scripts before Agent sees them

C. Use ensemble approach:
   - Have 2 different Agent prompts verify
   - Take agreement as result

D. Improve script generation:
   - Problem may not be Agent, but script quality
   - Return to Stage 2, improve ChatGPT prompts
```

**Step 8: Document Changes**
```
File: docs/ROLLBACK_LOG.md

---
ROLLBACK #1: Agent Accuracy Too Low
Date: 2026-05-15
Issue: Only 65% accuracy in Stage 5, need ≥80%
Root Cause: Agent thresholds too strict (rejecting 35% of good scripts)
Fix Applied: Lowered thresholds (clarity 75→70, flow 80→75, engagement 70→65)
Result: Accuracy improved to 83%
Action: Return to Stage 5, re-test with new settings
Status: ✅ RESOLVED, proceeding to Stage 5
---
```

**Step 9: Retry Stage 5 Go/No-Go**
```
With improved Agent accuracy (≥80%):
→ Proceed with Stage 5 end-to-end testing
→ Use new Agent settings throughout
→ At end of Stage 5, retry gate decision
→ If still ≥80%: GO TO STAGE 6
```

---

## SCENARIO 2: Quality Drops Below 7/10 During Stage 6

**Situation:** During soft launch, human reviews show quality average = 6.2/10

**Impact:** Videos below acceptable quality standard

### Rollback Procedure:

**Step 1: Stop Publishing**
```
→ Do NOT publish remaining videos from queue
→ Pause Stage 6 soft launch
→ Investigate what changed
```

**Step 2: Analyze Quality Drop (1-2 hours)**
```bash
# Compare Stage 5 quality vs Stage 6 quality

# Stage 5 baseline: 8.1/10 average
# Stage 6 actual: 6.2/10 average
# Drop: 1.9 points (big!)

# Question: What changed between Stage 5 and Stage 6?
# Possibilities:

1. Script quality decreased
   - Check: ChatGPT generating lower quality scripts?
   - Look for: More generic, less engaging topics

2. Tone variation problems
   - Check: Tone selection still random?
   - Look for: Repeated tones, poor matches to topics

3. Image generation degraded
   - Check: SDXL generating lower quality images?
   - Look for: Blurry, low contrast, repetitive images

4. Audio quality issues
   - Check: TTS voice quality?
   - Look for: Robotic, unclear pronunciation

5. Video assembly problems
   - Check: Transitions, pacing, effects?
   - Look for: Jarring cuts, bad timing, distracting effects

6. Human fatigue
   - Check: Are you reviewing more carefully now?
   - Look for: Earlier you rated 8/10, now 6/10, same content?
   - This = you're more critical, not content worse
```

**Step 3: Pinpoint Exact Issue**
```bash
# Pull logs to identify when quality dropped

# Check the 5+ videos published in Stage 6
# For each video:
# - Script quality score
# - Image diversity score
# - Audio quality score
# - Tone match score
# - Your final review feedback

# Example:
Video | Topic      | Script | Images | Audio | Tone | Final | Notes
------|-----------|--------|--------|-------|------|-------|--------
1     | Sleep     | 8.2    | 7.8    | 8.1   | 8.0  | 8.0   | ✅ Good
2     | Coffee    | 7.1    | 7.5    | 7.8   | 7.2  | 7.4   | Decent
3     | Exercise  | 5.8    | 6.2    | 7.9   | 6.5  | 6.2   | ⚠️ Script weak
4     | Meal      | 6.1    | 6.8    | 8.0   | 6.8  | 6.6   | ⚠️ Images bad
5     | Stress    | 7.0    | 5.2    | 7.5   | 7.1  | 6.2   | ⚠️ Images weak

Pattern: Images declining (7.8 → 5.2)
Or: Script quality declining (8.2 → 5.8)
```

**Step 4: Fix Identified Issue**

If **Script Quality Declining**:
```bash
# Return to Stage 2, improve script generation

# Check: Is ChatGPT API having issues?
# Check: Are topics getting less interesting?
# Check: Is Agent verification still catching poor scripts?

Fix options:
A. Improve ChatGPT prompts (more specific, better examples)
B. Return to Stage 2 Day 3, revise script_prompts.json
C. Add human pre-filtering (you spot-check scripts before image gen)
D. Check Agent accuracy (maybe it's approving bad scripts now)
```

If **Image Quality Declining**:
```bash
# Check: Is SDXL still working properly?

# Test:
python3 << 'EOF'
# Generate 5 test images
prompts = ["landscape", "city", "abstract", "nature", "urban"]
for prompt in prompts:
  img = generate_image(prompt)
  # Visual inspection: Are they good quality?
  # Are they sharp, well-lit, interesting?

# If poor: Ollama may need restart
# If OK: Problem is prompt selection, not SDXL
EOF

# Fix options:
A. Restart Ollama (sometimes helps)
B. Improve image prompts (config/image_prompts.json)
C. Reduce image count requirement
D. Return to Stage 2 Day 7, revisit image generation
```

If **Audio Quality Issues**:
```bash
# Check: Is Google TTS still working well?

# Test:
python3 << 'EOF'
# Generate test audio
script = "This is a test. Clarity should be excellent."
audio = generate_audio(script, voice="en-US-Neural2-C")
# Listen: Is it natural? Clear? Proper pacing?

# If poor: May be voice selection
# Try different voice: en-US-Neural2-A, en-US-Neural2-B
EOF

# Fix options:
A. Switch TTS voice (different neural voice)
B. Add SSML formatting improvements
C. Check: Are scripts too long/short? (affects pacing)
```

If **Tone Not Matching Content**:
```bash
# Check: Is tone selection still random?

# Review tone_selection.log for last 10 videos:
# - Are tones appropriate for topics?
# - Is randomization working? (no obvious pattern?)

# Fix options:
A. Improve content type classification
B. Refine tone → content mapping
C. Return to Stage 2 Day 5, revisit tone_manager.py
```

**Step 5: Implement Fix**
```
Example: If image quality declining

Old image prompts: "A landscape, photorealistic"
New image prompts: "Professional high-quality photography of [topic], sharp focus, well-lit, vibrant colors, 4K"

Reason: More specific = better images
```

**Step 6: Re-test with 5 New Videos (2-3 hours)**
```bash
# Generate 5 new videos with fix applied

# Check: Did quality improve?
# Measure: Average quality score
# Target: ≥7/10

Before fix: 6.2/10
After fix:  7.3/10
↳ YES → Quality improved, can resume Stage 6

Before fix: 6.2/10
After fix:  6.8/10
↳ PARTIAL → Better but not enough, try additional fixes
```

**Step 7: Document Rollback**
```
File: docs/ROLLBACK_LOG.md

---
ROLLBACK #2: Quality Drop in Stage 6
Date: 2026-05-20
Issue: Stage 6 quality 6.2/10 (below 7/10 minimum)
Root Cause: Image generation quality degraded
Fix Applied: Improved image prompts in config/image_prompts.json
Result: Quality improved to 7.4/10
Action: Resume Stage 6 with updated image prompts
Status: ✅ RESOLVED, resuming soft launch
---
```

**Step 8: Resume Stage 6**
```
→ Continue soft launch with fixed process
→ Publish remaining videos
→ Monitor quality continues ≥7/10
→ At end of soft launch, retry gate decision
```

---

## SCENARIO 3: YouTube Policy Strike Received

**Situation:** Video 2 in Stage 6 gets copyright strike from music

**Impact:** Content violates policy, production method broken

### Rollback Procedure:

**Step 1: Stop Publishing Immediately**
```
→ PAUSE all publishing
→ Flag CRITICAL POLICY ISSUE
→ Do NOT publish videos with same problem
```

**Step 2: Investigate Violation (1-2 hours)**
```
Questions:
1. What policy was violated?
   - Copyright (music, images, clips)
   - Misinformation (fact-check failure)
   - Harmful content (content policy)
   - Trademark (brand names used inappropriately)

2. When did system fail?
   - Stage 2 (script generation): Did Agent verify for copyright?
   - Stage 3 (fact-check): Did fact-check miss this?
   - Stage 4 (publishing): Wrong metadata?

3. How did we miss this?
   - Logs: What did Agent/fact-check say?
   - Were they skipped? Wrong configuration?
```

**Step 3: If Copyright Music Strike**
```
Root cause: Music library using copyrighted music

Solution:
1. Remove copyrighted music immediately
2. Update to royalty-free music library
3. Return to Stage 2, update music selection (config/music_library.json)
4. All music must be Creative Commons or purchased license

Example fix:
OLD: Using copyrighted background music
NEW: Using royalty-free music from Epidemic Sound or YouTube Audio Library

Affected videos: Remove from channel, file counter-notice if applicable
```

**Step 4: If Misinformation Strike**
```
Root cause: Agent fact-check missing false claim

Solution:
1. Identify specific false claim in video
2. Return to Stage 3, improve fact-check system
   - Agent prompts need to be more careful
   - Add human review of flagged claims
3. Update Agent verification to catch misinformation
4. Audit all previously published videos for same issue

Updated process:
Stage 2: Agent verification checks for misinformation
Stage 3: Fact-check extracts and verifies all claims
Stage 3: Human verifies flagged claims (not automated)
```

**Step 5: If Harmful Content Strike**
```
Root cause: Script contains harmful advice

Solution:
1. Add explicit content policy checking to Agent
2. Return to Stage 2, improve script generation prompts
   - Explicitly exclude harmful content types
   - Add guardrails to ChatGPT prompts
3. Add human review for sensitive topics

Example:
Stage 2: ChatGPT prompt includes "Do not include medical advice without disclaimer"
Stage 3: Human reviews any health/medical claims before publishing
```

**Step 6: Update System to Prevent Recurrence**

Example for misinformation:
```
# File: config/agent_prompts.json
# Add specific check for fact accuracy

"fact_check_prompt": "Before approving this script, verify:
- No medical advice without disclaimer
- No legal advice
- No financial advice without qualification
- All facts are current and accurate
- No misleading statistics

If ANY of above, mark FAIL and request revision."
```

**Step 7: Audit All Published Videos**
```bash
# Check ALL previously published videos for same issue

for video in all_published_videos:
  # Download transcript
  transcript = get_transcript(video)
  
  # Check: Does it have same issue?
  if has_copyrighted_music(video):
    print(f"⚠️ {video} - has copyright music")
  
  if has_misinformation(transcript):
    print(f"⚠️ {video} - contains false claims")

# Take action:
# - Remove videos with strikes
# - File counter-notices if applicable
# - Update metadata/remove claims
```

**Step 8: Re-test System**
```
With improved safeguards:
→ Return to Stage 2/3
→ Generate 5+ new videos with updated checks
→ Have them reviewed carefully before publishing
→ No policy issues? ✅ Can resume

If issues recur:
→ Further strengthen fact-check
→ Consider human legal review before publishing
```

**Step 9: Document Rollback**
```
File: docs/ROLLBACK_LOG.md

---
ROLLBACK #3: Copyright Strike in Stage 6
Date: 2026-05-22
Issue: Video 2 copyright strike (background music)
Root Cause: Music selection using copyrighted track
Fix Applied: Updated music library to royalty-free only
Action: Return to Stage 2, remove strike from YouTube
Status: Reviewing all published videos for same issue
---
```

---

## GENERAL ROLLBACK CHECKLIST

For ANY rollback:

- [ ] Stop publishing immediately
- [ ] Document issue in ROLLBACK_LOG.md
- [ ] Identify root cause (which stage failed?)
- [ ] Fix the identified issue
- [ ] Re-test with 3-5 new items
- [ ] Verify fix worked (metrics improved)
- [ ] Return to appropriate stage
- [ ] Retry go/no-go decision at that stage
- [ ] Proceed only if gate criteria met

---

## ROLLBACK LOG TEMPLATE

Keep a running log of all rollbacks:

```markdown
# Rollback History

---
## ROLLBACK #1: [Title]
**Date:** [date]
**Issue:** [What went wrong?]
**Root Cause:** [Why did it happen?]
**Stage:** [Which stage was affected?]
**Severity:** [Critical / High / Medium / Low]
**Fix Applied:** [What did you change?]
**Re-test Result:** [Did it work?]
**Status:** [✅ Resolved / ⏳ In Progress / ❌ Unresolved]

---
## ROLLBACK #2: [Title]
[same format]
```

Use this to track patterns:
- Same issue recurring? Improve the fix
- Multiple issues in one stage? That stage needs more work
- Most issues in Stage X? Focus effort there
