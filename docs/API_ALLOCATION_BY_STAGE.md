# API ALLOCATION BY STAGE
**Quick Reference: Which API Does What, Where**

---

## 🎯 CRYSTAL CLEAR ALLOCATION BY STAGE

### STAGE 1: Environment Setup
- **DeepSeek:** N/A (testing only)
- **ChatGPT/Claude:** N/A (testing only)
- **Note:** Both API keys configured and tested

---

### STAGE 2: Core Automation Infrastructure

#### DAY 1-2: Orchestrator Engine Setup
- **API Usage:** ChatGPT/Claude ONLY (Agent verification will be integrated)
- **Tasks:** Orchestrator, Agent manager setup
- **Cost:** $0 (configuration only)

#### DAY 3: Script Generation Module - HYBRID APPROACH ⭐ CRITICAL
**THIS IS WHERE COST OPTIMIZATION HAPPENS:**

| Step | API | Task | Cost | Why |
|------|-----|------|------|-----|
| Step 1 | **DeepSeek** | Generate trending topics | $0.01-0.02 | Analytical, cheap |
| Step 2 | **DeepSeek** | Create content outline | $0.02-0.03 | Structural, analytical |
| Step 3 | **ChatGPT/Claude** | Write engaging script | $0.10-0.15 | CRITICAL: Quality determines monetization |
| Step 4 | *N/A* | Metadata capture | $0 | Local processing |

**Golden Rule:** NEVER use DeepSeek for script writing (quality <7/10) and NEVER waste ChatGPT on topics.

#### DAY 4: Agent Verification Integration
- **API Usage:** **ChatGPT/Claude ONLY** ⭐ CRITICAL
- **Task:** Verify script quality with Agent
- **Cost:** ~$0.05-0.08 per script
- **Critical Gate:** ≥80% accuracy required (Gate 2)
- **Why ChatGPT/Claude:** Script quality verification determines if content passes YouTube quality standards

#### DAY 5: Tone Variation System
- **API Usage:** **ChatGPT/Claude ONLY** ⭐ CRITICAL
- **Task:** Generate 2-3 tone variations per script
- **Cost:** ~$0.08-0.12 per script
- **Why ChatGPT/Claude:** Tone nuance is subtle, requires quality language model

#### DAY 6: TTS Audio Generation
- **API Usage:** Google Cloud TTS (not DeepSeek or ChatGPT)
- **Task:** Convert script to audio
- **Cost:** ~$0.05 per script

#### DAY 7: Image Generation Integration
- **API Usage:** Ollama/SDXL (local GPU, no cost)
- **Task:** Generate visual assets
- **Cost:** $0 (local)

#### DAY 8: Video Assembly Framework
- **API Usage:** None (FFmpeg/MoviePy - local)
- **Task:** Assemble video
- **Cost:** $0

#### DAY 9: Logging & Monitoring Setup
- **API Usage:** None (local)
- **Cost:** $0

#### DAY 10: End-to-End Integration Testing
- **API Usage:** DeepSeek (topics) + ChatGPT/Claude (scripts, verification)
- **Testing Cost:** ~$0.30 per test video (5 videos = $1.50)

**STAGE 2 TOTAL COST:** ~$0.28 per video ($14/week for 50 videos)

---

### STAGE 3: Quality Gates & Review Systems

#### DAY 1-2: Agent Fact-Check Integration
- **API Usage:** **ChatGPT/Claude ONLY** ⭐ CRITICAL
- **Task:** Extract claims, flag risks using Agent
- **Cost:** ~$0.05-0.08 per script
- **Why ChatGPT/Claude:** Fact-checking accuracy directly impacts YouTube policy compliance

**IMPORTANT:** The "Agent" in fact-checking is ChatGPT/Claude's agent capability, NOT DeepSeek.

#### DAY 3: Human Final Review Checklist
- **API Usage:** None (human decision)
- **Cost:** $0
- **Time:** 5-10 min per video

#### DAY 4: Quality Gate Validation
- **API Usage:** None (orchestration only)
- **Cost:** $0

#### DAY 5: Agent Verification Analysis
- **API Usage:** None (analysis of existing logs)
- **Cost:** $0
- **Task:** Review Agent decisions from Stage 2, improve prompts if needed

#### DAY 6: Tone Variation Performance Tracking
- **API Usage:** None (analytics only)
- **Cost:** $0

#### DAY 7: Documentation & Testing
- **API Usage:** ChatGPT/Claude (test 5 videos end-to-end)
- **Testing Cost:** ~$1.50 (5 videos × $0.30)

**STAGE 3 TOTAL COST:** ~$0.10-0.13 per video ($5-6/week for 50 videos)

---

### STAGE 4: YouTube API Integration

#### All Days: YouTube Upload, Metadata, Scheduling
- **API Usage:** YouTube API (Google Cloud)
- **Other APIs:** None (DeepSeek/ChatGPT not used in Stage 4)
- **Cost:** ~$0 (free YouTube API tier is sufficient)

**Note:** No AI script generation or verification in Stage 4. Pure technical integration.

**STAGE 4 TOTAL COST:** $0 (YouTube API free tier)

---

### STAGE 5: Testing, Validation & Optimization

#### DAY 1-2: End-to-End Testing
- **API Usage:** DeepSeek (topics) + ChatGPT/Claude (scripts, verification)
- **Testing Cost:** ~$1.50 (5 videos × $0.30)

#### DAY 3: Load Testing
- **API Usage:** DeepSeek + ChatGPT/Claude
- **Testing Cost:** ~$3.00 (10 videos × $0.30)

#### DAY 4: Quality Metrics Baseline
- **API Usage:** None (evaluation only)
- **Cost:** $0
- **Task:** Establish 8.3/10 quality baseline

#### DAY 5: Agent Accuracy Measurement
- **API Usage:** None (analysis of existing Agent decisions)
- **Cost:** $0
- **Critical Gate:** ≥80% accuracy required
- **Task:** Measure ChatGPT/Claude Agent verification accuracy from Stage 2-4

**IMPORTANT:** This measures accuracy of the ChatGPT/Claude Agent verification system, NOT DeepSeek.

#### DAY 6: Quality Metrics & Tone Assessment
- **API Usage:** None (evaluation)
- **Cost:** $0

#### DAY 6: Error Handling Verification
- **API Usage:** DeepSeek + ChatGPT/Claude (simulate failures)
- **Testing Cost:** ~$0.30-1.00

#### DAY 7: Final Sign-Off
- **API Usage:** None (decision only)
- **Cost:** $0

**STAGE 5 TOTAL COST:** ~$5.00 (testing only, not production)

---

### STAGE 6: Soft Launch (6 videos over 7 days)

#### Daily Process: Generate → Verify → Publish
- **API Usage:** DeepSeek (topics) + ChatGPT/Claude (scripts, verification)
- **Production Cost:** ~$0.30 per video
- **6 videos total:** ~$1.80
- **Human Time:** 5-10 min per video × 6 = 30-60 min total

**STAGE 6 TOTAL COST:** ~$1.80

---

### STAGE 7: Production & Scaling (35-49 videos/week)

#### Daily Process: 5-7 videos/day
- **API Usage:** DeepSeek (topics) + ChatGPT/Claude (scripts, verification)
- **Weekly Cost:** ~$14.00 (50 videos × $0.28)
- **Monthly Cost:** ~$56.00
- **Human Time:** 30-90 min per day

**STAGE 7 ONGOING COST:** ~$56/month (production rate)

---

## 📊 TOTAL COST SUMMARY

| Stage | Cost | Purpose |
|-------|------|---------|
| Stage 1 | $0 | Setup (testing only) |
| Stage 2 | $1.50-2.00 | Development (test videos) |
| Stage 3 | $1.50 | QA (test videos) |
| Stage 4 | $0 | YouTube integration (technical) |
| Stage 5 | $5.00 | Validation & load testing |
| Stage 6 | $1.80 | Soft launch (6 videos) |
| **Total Before Production** | ~$11.00 | Development + Testing |
| **Stage 7 Monthly** | ~$56.00 | Production (50 videos) |

---

## ⚠️ CRITICAL API ASSIGNMENT RULES

### ✅ DeepSeek ONLY For:
- Topic generation (research-based analysis)
- Content outlines (structural planning)
- Keyword research (analytical)
- Fact verification support (research lookup - NOT final fact-check)

**Cost per use:** $0.01-0.03  
**Max waste tolerance:** $10/month  

### ✅ ChatGPT/Claude ONLY For:
- Script generation (creative writing - **CRITICAL**)
- Script evaluation (Agent verification - **CRITICAL**)
- Tone variations (nuanced style - **CRITICAL**)
- Fact-checking (policy compliance - **CRITICAL**)
- Agent accuracy assessment (quality measurement - **CRITICAL**)

**Cost per use:** $0.05-0.15  
**Why:** These determine monetization success - quality is NON-NEGOTIABLE

### ❌ NEVER Use DeepSeek For:
- ❌ Script writing (quality <7/10 = fails gates)
- ❌ Script evaluation (accuracy <80% = fails Gate 2)
- ❌ Tone variations (misses nuance)
- ❌ Agent verification (fails quality threshold)

### ❌ NEVER Use ChatGPT For:
- ❌ Topic generation (wasteful, DeepSeek sufficient)
- ❌ Outlines (wasteful, DeepSeek sufficient)
- ❌ Keyword research (wasteful, DeepSeek sufficient)

**Why this matters:**
- ChatGPT on trivial tasks = $500/year waste
- DeepSeek on critical tasks = Project fails (quality <7/10)
- Correct allocation = Optimal quality ($56/month) + success

---

## 🔑 KEY PRINCIPLE

**"DeepSeek for Volume & Research, ChatGPT/Claude for Quality & Verification"**

Think of it like:
- **DeepSeek** = Researcher (finds what to talk about)
- **ChatGPT/Claude** = Screenwriter (makes it compelling & verifies quality)

You need BOTH:
- Only researcher = boring content (fails)
- Only screenwriter = no ideas (fails)
- Both working together = success ✅

---

## 📋 WHEN IN DOUBT

**Question:** Which API should I use for [task]?

**Answer Formula:**
1. Is it creative writing or quality-critical? → **ChatGPT/Claude**
2. Is it analytical/research/topic work? → **DeepSeek**
3. Is it YouTube API/publishing/infrastructure? → **Neither (use YouTube API/Ollama/local tools)**

---

## 🔄 API DEPENDENCY MAP

```
┌─────────────────────────────────────────────┐
│ Stage 2: Script Generation (DAY 3)         │
│                                             │
│ DeepSeek (Topic)                           │
│    ↓                                       │
│ DeepSeek (Outline)                         │
│    ↓                                       │
│ ChatGPT/Claude (Script) ⭐ CRITICAL        │
│    ↓                                       │
├─────────────────────────────────────────────┤
│ Stage 2: Verification (DAY 4)              │
│                                             │
│ ChatGPT/Claude (Agent Verify) ⭐ CRITICAL  │
│    ├─ PASS → Continue                     │
│    └─ FAIL → Regenerate (max 3 tries)     │
│                                             │
├─────────────────────────────────────────────┤
│ Stage 2: Tone (DAY 5)                      │
│                                             │
│ ChatGPT/Claude (Tone Variations) ⭐        │
│    ↓ 2-3 variations                       │
│    ↓                                       │
├─────────────────────────────────────────────┤
│ Stage 3: Fact-Check (DAY 1-2)              │
│                                             │
│ ChatGPT/Claude (Fact-Check) ⭐             │
│    ├─ Safe → Continue                     │
│    ├─ Caution → Human verify              │
│    └─ Risk → Flag for human               │
│                                             │
├─────────────────────────────────────────────┤
│ Stage 5: Agent Accuracy (DAY 5)            │
│                                             │
│ Measure ChatGPT/Claude Accuracy ⭐         │
│    ├─ ≥80% → Ready for Stage 6            │
│    └─ <80% → Return to Stage 2            │
│                                             │
└─────────────────────────────────────────────┘
```

---

## ✅ SETUP CHECKLIST

Before starting ANY stage:

- [ ] DeepSeek API key ready (from deepseek.com) - for topics
- [ ] ChatGPT API key ready (from openai.com) OR Claude API key ready (from anthropic.com) - for scripts/verification
- [ ] Both APIs configured in config files
- [ ] Both tested with sample calls
- [ ] Cost monitoring set up for both APIs
- [ ] This allocation document bookmarked for reference

---

This document is your single source of truth for API allocation. Refer to it whenever making decisions about which API to use for a task.

