# STAGE 2 - READY-TO-USE CURSOR PROMPTS
**Status:** Complete and tested prompts  
**Total Prompts:** 6 sessions  
**Focus:** Stage 2 ONLY (no other stages)  
**Gate:** Verify Agent accuracy ≥80%

---

## 📋 CURSOR SESSION 1: ORCHESTRATOR ENGINE & CONFIG LOADER

**Copy and paste this entire prompt into Cursor:**

```
I'm building an automated YouTube video generation system. This is Stage 2 of 7.

PROJECT CONTEXT:
- Root folder: ~/projects/YouTube-Automation/
- Documentation: docs/STAGE_2_EXECUTION_PLAN.md
- All API keys ready and tested
- Folder structure created with venv activated

TASK: Create the Orchestrator Engine and Config Loader

FILES TO CREATE:
1. src/core/orchestrator.py
2. src/core/config_loader.py
3. tests/test_orchestrator.py

SPECIFICATIONS FOR src/core/orchestrator.py:

Class: VideoProductionOrchestrator
Purpose: Main workflow coordinator for video generation pipeline

Methods:
  __init__(self, config_path: str)
    - Load configuration from config_loader
    - Initialize all clients (placeholders for now)
    - Setup logging
    - Initialize state tracking

  generate_video(self, topic: str = None, category: str = "general") -> dict
    - Main orchestration method
    - Workflow: Topic Gen → Script Gen → Agent Verify → Tone Variation → TTS → Images → Video Assembly
    - Error handling with logging
    - Return dict with video metadata

  run_pipeline(self) -> dict
    - Run complete end-to-end pipeline with default topic
    - For testing purposes
    - Return success/failure status

Input/Output:
  - Input: topic (str), category (str)
  - Output: dict with keys {
      "success": bool,
      "video_path": str,
      "script": str,
      "topic": str,
      "tone_used": str,
      "agent_verification_passed": bool,
      "timestamp": str,
      "duration_seconds": float
    }

Error Handling:
  - Try/except for each major step
  - Log all errors
  - Return error details in output dict
  - Never crash, always return dict

Logging:
  - Use logging module
  - Log level: INFO (default), DEBUG (verbose)
  - Log all major steps and decisions
  - Include timestamps

SPECIFICATIONS FOR src/core/config_loader.py:

Class: ConfigLoader
Purpose: Load and validate configuration from config/ folder

Methods:
  __init__(self, config_dir: str = "config")
    - Load config/settings.json
    - Load config/agent_prompts.json
    - Load config/script_prompts.json
    - Validate all configs exist
    - Raise error if missing

  get_setting(self, key: str, default=None) -> Any
    - Get a specific setting
    - Return default if not found

  get_agent_prompts(self) -> dict
  get_script_prompts(self) -> dict

Requirements:
  - Validate JSON files exist
  - Validate JSON is valid
  - Provide clear error messages
  - Type hints on all methods
  - Docstrings for all methods
  - No external dependencies beyond json

SPECIFICATIONS FOR tests/test_orchestrator.py:

Unit Tests:
  - test_orchestrator_init (verify initialization works)
  - test_config_loader_init (verify config loading)
  - test_orchestrator_has_required_methods (verify all methods exist)
  - test_config_loader_returns_dict (verify config is dict)
  - test_error_handling_missing_config (verify error handling)
  - test_orchestrator_run_pipeline_returns_dict (verify output format)

Mocking:
  - Use unittest.mock for external dependencies
  - Mock any file I/O
  - Mock any API calls

Code Requirements:
  - Type hints on all methods
  - Comprehensive docstrings
  - PEP 8 compliant
  - Error messages are clear and actionable
  - Logging at key points
  - No hardcoded values
  - Configuration-driven

INTEGRATION POINTS:
  - Must accept config from config/ folder
  - Must have placeholders for: DeepSeek client, ChatGPT client, Agent verifier, Tone manager, TTS, Image generator, Video assembler
  - Must return standardized output dict
  - Must log all operations

OUTPUT CHECKLIST:
After generating, verify:
  ✅ src/core/orchestrator.py created with VideoProductionOrchestrator class
  ✅ src/core/config_loader.py created with ConfigLoader class
  ✅ tests/test_orchestrator.py created with all unit tests
  ✅ All methods have type hints
  ✅ All methods have docstrings
  ✅ Error handling implemented
  ✅ Logging implemented
  ✅ Unit tests runnable with: pytest tests/test_orchestrator.py -v
```

---

## 📋 CURSOR SESSION 2: HYBRID SCRIPT GENERATOR ⭐ CRITICAL

**Copy and paste this entire prompt into Cursor:**

```
I'm building an automated YouTube video generation system. This is Stage 2, Session 2.

PROJECT CONTEXT:
- Root folder: ~/projects/YouTube-Automation/
- Documentation: docs/API_ALLOCATION_BY_STAGE.md, docs/STAGE_2_EXECUTION_PLAN.md
- DeepSeek API key ready
- ChatGPT/Claude API key ready
- Both APIs tested and working

TASK: Create HybridScriptGenerator (DeepSeek + ChatGPT/Claude)

FILES TO CREATE:
1. src/api/deepseek_client.py
2. src/api/chatgpt_client.py
3. src/generation/script_generator.py (HybridScriptGenerator class)
4. tests/test_script_generator.py

CRITICAL ALLOCATION RULES (From docs/API_ALLOCATION_BY_STAGE.md):
- DeepSeek ONLY for: Topic generation ($0.01-0.02), Outline creation ($0.02-0.03)
- ChatGPT/Claude ONLY for: Script writing ($0.10-0.15)
- NEVER use DeepSeek for script writing (quality <7/10)
- NEVER waste ChatGPT on topics (cost wasteful)

SPECIFICATIONS FOR src/api/deepseek_client.py:

Class: DeepSeekClient
Purpose: Topic generation and outline creation using DeepSeek API

Methods:
  __init__(self, api_key: str)
    - Initialize with API key from .env
    - Setup base URL and headers
    - Setup error handling

  generate_topic(self, category: str = "general", trendy: bool = True) -> str
    - Generate trending YouTube topic
    - Input: category (health, tech, lifestyle, finance, etc.)
    - Output: Single topic string
    - Cost: ~$0.01-0.02
    - Error handling: Return None if fails, log error

  create_outline(self, topic: str, content_type: str = "short") -> str
    - Create content outline for topic
    - Input: topic (from generate_topic), content_type
    - Output: Structured outline string
    - Cost: ~$0.02-0.03
    - Error handling: Return None if fails, log error

Requirements:
  - Use requests library for API calls
  - Handle API errors gracefully
  - Include retry logic (max 2 retries)
  - Log all API calls and responses
  - Type hints on all methods
  - Docstrings on all methods

SPECIFICATIONS FOR src/api/chatgpt_client.py:

Class: ChatGPTClient (or ClaudeClient if using Claude)
Purpose: Script generation using ChatGPT/Claude API

Methods:
  __init__(self, api_key: str, model: str = "gpt-4o-mini")
    - Initialize with API key from .env
    - Setup OpenAI/Anthropic client
    - Setup model configuration

  write_script(self, topic: str, outline: str = None, style: str = "youtube_faceless") -> str
    - Generate engaging YouTube script
    - Input: topic, outline (optional), style
    - Output: Complete script text (2-3 minutes read time)
    - Cost: ~$0.10-0.15
    - CRITICAL: This is quality-critical for monetization
    - Error handling: Raise error if fails (don't retry here - orchestrator handles)

Requirements:
  - Use official OpenAI or Anthropic SDK
  - HIGH QUALITY SCRIPTS (must be engaging, clear, flowing)
  - Include: Hook (first 15 seconds), Body, CTA (Call to Action)
  - Natural pacing and transitions
  - Type hints on all methods
  - Docstrings on all methods

SPECIFICATIONS FOR src/generation/script_generator.py:

Class: HybridScriptGenerator
Purpose: Combine DeepSeek (cheap) + ChatGPT/Claude (quality) into one workflow

Methods:
  __init__(self, deepseek_key: str, chatgpt_key: str, chatgpt_model: str = "gpt-4o-mini")
    - Initialize both clients
    - Setup state tracking
    - Setup logging

  generate_script(self, category: str = "general") -> dict
    - Step 1: DeepSeek generates topic (~$0.01-0.02)
    - Step 2: DeepSeek creates outline (~$0.02-0.03)
    - Step 3: ChatGPT/Claude writes script (~$0.10-0.15)
    - Step 4: Capture metadata
    - Return complete script object

    Input: category (str)
    Output: dict with keys {
      "topic": str,
      "outline": str,
      "script": str,
      "category": str,
      "api_cost": float,
      "api_split": {
        "deepseek": float,
        "chatgpt": float
      },
      "timestamp": str,
      "model_versions": {
        "deepseek_model": str,
        "chatgpt_model": str
      }
    }

Cost Tracking:
  - Track total cost: DeepSeek cost + ChatGPT cost
  - Return cost breakdown in output
  - Log costs for monitoring

Error Handling:
  - DeepSeek error: Log and retry once
  - ChatGPT error: Raise and let orchestrator handle retry
  - Invalid input: Validate before API calls
  - Return informative error messages

SPECIFICATIONS FOR tests/test_script_generator.py:

Unit Tests:
  - test_deepseek_init (verify initialization)
  - test_chatgpt_init (verify initialization)
  - test_generate_topic (mock API call, verify output is string)
  - test_create_outline (mock API call, verify output is string)
  - test_write_script (mock API call, verify output is string)
  - test_hybrid_script_generator_init (verify full initialization)
  - test_generate_script_returns_dict (verify correct output format)
  - test_api_split_in_output (verify cost tracking works)
  - test_error_handling_deepseek (verify retry logic)
  - test_error_handling_chatgpt (verify error propagation)

Mocking:
  - Mock DeepSeek API calls
  - Mock ChatGPT API calls
  - Mock .env file reading
  - Verify correct API calls are made
  - Verify costs are calculated

Code Requirements:
  - Type hints on all methods
  - Comprehensive docstrings
  - PEP 8 compliant
  - Clear error messages
  - Logging at key points
  - Cost tracking and logging
  - No hardcoded API keys

OUTPUT CHECKLIST:
After generating, verify:
  ✅ src/api/deepseek_client.py created
  ✅ src/api/chatgpt_client.py created
  ✅ src/generation/script_generator.py created with HybridScriptGenerator
  ✅ tests/test_script_generator.py created with all unit tests
  ✅ DeepSeek only does topic + outline (NOT script)
  ✅ ChatGPT only does script writing
  ✅ Cost tracking implemented
  ✅ Error handling for both APIs
  ✅ All unit tests runnable with: pytest tests/test_script_generator.py -v
  ✅ Output dict has all required keys
```

---

## 📋 CURSOR SESSION 3: AGENT VERIFICATION SYSTEM

**Copy and paste this prompt into Cursor:**

```
I'm building an automated YouTube video generation system. This is Stage 2, Session 3.

TASK: Create Agent Verification System (Quality Gate - CRITICAL)

FILES TO CREATE:
1. src/quality/agent_verifier.py
2. tests/test_agent_verifier.py

CRITICAL REQUIREMENT:
- Agent must pass ≥80% of scripts on FIRST attempt
- Max 3 retries per script (fails after 3)
- This is Gate 2 - must pass before Stage 3

SPECIFICATIONS FOR src/quality/agent_verifier.py:

Class: AgentVerifier
Purpose: Verify script quality using ChatGPT/Claude Agent

Methods:
  __init__(self, chatgpt_key: str, model: str = "gpt-4o-mini")
    - Initialize ChatGPT/Claude client
    - Setup verification prompts from config/agent_prompts.json

  verify_script(self, script: str, topic: str = None) -> dict
    - Verify if script meets quality standards
    - Check: Clarity (8/10+), Flow (8/10+), Engagement (7/10+), Issues (0 critical)
    - Uses Agent to evaluate script
    
    Input: script (str), topic (optional)
    Output: dict {
      "result": "PASS" or "FAIL",
      "scores": {
        "clarity": int (0-100),
        "flow": int (0-100),
        "engagement": int (0-100),
        "issues_count": int
      },
      "feedback": str,
      "suggestion": str,
      "attempt": int,
      "timestamp": str
    }

Verification Logic:
  - Call ChatGPT/Claude with verification prompt
  - Parse response for scores and feedback
  - Return standardized dict
  - No retries here (orchestrator handles retries)

SPECIFICATIONS FOR tests/test_agent_verifier.py:

Unit Tests:
  - test_agent_verifier_init
  - test_verify_script_returns_dict
  - test_verify_script_result_is_pass_or_fail
  - test_verify_script_has_all_keys
  - test_verify_script_scores_are_integers
  - test_verify_script_with_high_quality_script (mock → PASS)
  - test_verify_script_with_low_quality_script (mock → FAIL)

Mocking:
  - Mock ChatGPT API responses
  - Test PASS scenario
  - Test FAIL scenario
  - Verify output format

CODE REQUIREMENTS:
  - Type hints on all methods
  - Docstrings on all methods
  - PEP 8 compliant
  - Clear error handling
  - Logging all verifications
  - Timestamp tracking

OUTPUT CHECKLIST:
After generating, verify:
  ✅ src/quality/agent_verifier.py created
  ✅ tests/test_agent_verifier.py created
  ✅ Verification returns PASS/FAIL
  ✅ Scores are tracked (clarity, flow, engagement, issues)
  ✅ Feedback and suggestions provided
  ✅ All unit tests pass
```

---

## 📋 CURSOR SESSION 4: TONE VARIATION SYSTEM

**Copy and paste this prompt into Cursor:**

```
I'm building an automated YouTube video generation system. This is Stage 2, Session 4.

TASK: Create Tone Variation System

FILES TO CREATE:
1. src/generation/tone_manager.py
2. config/tone_library.json
3. tests/test_tone_manager.py

SPECIFICATIONS FOR config/tone_library.json:

Structure:
{
  "tones": [
    {
      "id": "professional_educational",
      "name": "Professional Educational",
      "description": "Formal, academic, authoritative",
      "best_for": ["tutorial", "educational", "technical"],
      "variations": [
        "variation_prompt_1",
        "variation_prompt_2",
        "variation_prompt_3"
      ]
    },
    {
      "id": "conversational_storytelling",
      "name": "Conversational Storytelling",
      "description": "Friendly, engaging, story-driven",
      "best_for": ["entertainment", "lifestyle", "personal story"],
      "variations": [...]
    },
    {
      "id": "energetic_motivational",
      "name": "Energetic Motivational",
      "description": "Upbeat, inspiring, high-energy",
      "best_for": ["fitness", "motivation", "self-help"],
      "variations": [...]
    },
    {
      "id": "curious_explainer",
      "name": "Curious Explainer",
      "description": "Curious, wondering, investigative",
      "best_for": ["mystery", "discovery", "how-it-works"],
      "variations": [...]
    },
    {
      "id": "quick_direct",
      "name": "Quick & Direct",
      "description": "Fast-paced, concise, to-the-point",
      "best_for": ["quick tips", "hacks", "news"],
      "variations": [...]
    }
  ]
}

SPECIFICATIONS FOR src/generation/tone_manager.py:

Class: ToneManager
Purpose: Manage tone selection and variation generation

Methods:
  __init__(self, tone_library_path: str = "config/tone_library.json")
    - Load tone library
    - Validate all tones
    - Setup random selection

  identify_content_type(self, script: str) -> str
    - Analyze script content
    - Return content type (tutorial, entertainment, etc.)
    - Used to filter applicable tones

  get_applicable_tones(self, content_type: str) -> list
    - Get all tones applicable to content type
    - Return list of tone objects
    - If no exact match, return all tones

  select_random_tone(self, applicable_tones: list = None) -> dict
    - Random select from applicable tones
    - Return selected tone object
    - Log selection for analytics

  generate_variations(self, script: str, tone: dict) -> list
    - Generate 2-3 rewrites in selected tone
    - Use ChatGPT to rewrite script
    - Return list of variation dicts
    
    Output per variation: {
      "variation_number": int (1, 2, or 3),
      "tone_id": str,
      "tone_name": str,
      "script": str,
      "timestamp": str
    }

Error Handling:
  - Validate tone library exists
  - Validate JSON format
  - Fallback to "professional_educational" if selection fails
  - Log all errors

SPECIFICATIONS FOR tests/test_tone_manager.py:

Unit Tests:
  - test_tone_manager_init
  - test_tone_library_loads
  - test_identify_content_type
  - test_get_applicable_tones
  - test_select_random_tone
  - test_generate_variations_returns_list
  - test_variations_have_correct_format
  - test_variation_count_is_2_or_3

CODE REQUIREMENTS:
  - Type hints on all methods
  - Docstrings on all methods
  - PEP 8 compliant
  - Logging all selections
  - Cost tracking for ChatGPT calls
  - Mock testing with sample scripts

OUTPUT CHECKLIST:
After generating, verify:
  ✅ src/generation/tone_manager.py created
  ✅ config/tone_library.json created with 5 tone profiles
  ✅ Each tone has 3 variations
  ✅ Random selection implemented
  ✅ Variation generation works
  ✅ All unit tests pass
```

---

## 📋 CURSOR SESSION 5: TTS HANDLER + IMAGE GENERATOR

**Copy and paste this prompt into Cursor:**

```
I'm building an automated YouTube video generation system. This is Stage 2, Session 5.

TASK: Create TTS Handler + Image Generator

FILES TO CREATE:
1. src/api/google_tts.py
2. src/generation/image_generator.py
3. tests/test_tts_handler.py
4. tests/test_image_generator.py

SPECIFICATIONS FOR src/api/google_tts.py:

Class: TTSHandler
Purpose: Text-to-speech using Google Cloud TTS

Methods:
  __init__(self, credentials_path: str, project_id: str)
    - Initialize Google Cloud client
    - Setup credentials from credentials_path
    - Setup voice selection

  generate_audio(self, text: str, voice_name: str = "en-US-Neural2-C") -> bytes
    - Convert text to speech
    - Return audio bytes
    - Format: WAV, 44.1kHz, 16-bit, Mono
    
  add_ssml_formatting(self, script: str) -> str
    - Add SSML tags for natural pacing
    - Add pauses, emphasis, rate changes
    - Return SSML-formatted text

  validate_audio_quality(self, audio_bytes: bytes) -> bool
    - Validate audio is not corrupted
    - Return True if valid, False if invalid

Error Handling:
  - Validate credentials exist
  - Validate text is not empty
  - Handle API errors gracefully
  - Log all operations

SPECIFICATIONS FOR src/generation/image_generator.py:

Class: ImageGenerator
Purpose: Generate images using Ollama/SDXL

Methods:
  __init__(self, model: str = "sdxl", base_url: str = "http://localhost:11434")
    - Initialize Ollama client
    - Setup SDXL model
    - Setup connection to Ollama

  generate_image(self, prompt: str, num_images: int = 1) -> list
    - Generate images from prompt
    - Return list of image paths (saved locally)
    - Save to: data/generated_videos/images/[timestamp]_[number].png
    
  select_random_prompt(self, topic: str, count: int = 3) -> list
    - Select random prompts from config/image_prompts.json
    - Return list of prompts
    - Ensure variety

  generate_with_variation(self, topic: str, num_variations: int = 3) -> list
    - Generate images with prompt variations
    - Return list of generated image paths

Error Handling:
  - Check Ollama is running
  - Handle connection errors
  - Fallback to placeholder images if generation fails
  - Log all attempts

SPECIFICATIONS FOR tests/test_tts_handler.py:

Unit Tests:
  - test_tts_handler_init
  - test_generate_audio_returns_bytes
  - test_add_ssml_formatting_returns_string
  - test_validate_audio_quality
  - test_error_handling_invalid_credentials
  - test_error_handling_empty_text

CODE REQUIREMENTS:
  - Type hints on all methods
  - Docstrings on all methods
  - PEP 8 compliant
  - Error handling and logging
  - Mock testing for external APIs

SPECIFICATIONS FOR tests/test_image_generator.py:

Unit Tests:
  - test_image_generator_init
  - test_generate_image_returns_list
  - test_generate_image_creates_files
  - test_select_random_prompt_returns_list
  - test_generate_with_variation_returns_list
  - test_error_handling_ollama_not_running

OUTPUT CHECKLIST:
After generating, verify:
  ✅ src/api/google_tts.py created
  ✅ src/generation/image_generator.py created
  ✅ tests/test_tts_handler.py created
  ✅ tests/test_image_generator.py created
  ✅ TTS generates audio bytes
  ✅ Images generated and saved locally
  ✅ Error handling for both
  ✅ All unit tests pass
```

---

## 📋 CURSOR SESSION 6: VIDEO ASSEMBLER + LOGGING

**Copy and paste this prompt into Cursor:**

```
I'm building an automated YouTube video generation system. This is Stage 2, Session 6 (FINAL).

TASK: Create Video Assembler + Logging System

FILES TO CREATE:
1. src/video/video_assembler.py
2. src/core/logger.py
3. src/core/performance_monitor.py
4. tests/test_video_assembler.py

SPECIFICATIONS FOR src/video/video_assembler.py:

Class: VideoAssembler
Purpose: Assemble final video from audio, images, metadata

Methods:
  __init__(self)
    - Initialize MoviePy
    - Setup video parameters (1080p, 30fps)

  assemble_video(self, audio_path: str, images: list, metadata: dict) -> str
    - Assemble complete video
    - Input: audio file, list of image paths, metadata
    - Output: path to final video file
    - Saved to: data/generated_videos/[timestamp].mp4
    
  add_transitions(self, clips: list, random: bool = True) -> list
    - Add transitions between clips
    - Fade (60%), Zoom (20%), Wipe (20%)
    - Duration: 0.3-1s random
    - Return modified clips

  apply_subtitles(self, video_path: str, script: str) -> str
    - Generate subtitles from script
    - Add to video
    - Return path with subtitles

  verify_final_quality(self, video_path: str) -> bool
    - Verify video file integrity
    - Check duration, bitrate, resolution
    - Return True if valid

Error Handling:
  - Validate input files exist
  - Handle encoding errors
  - Fallback if effects fail
  - Log all steps

SPECIFICATIONS FOR src/core/logger.py:

Class: Logger
Purpose: Comprehensive application logging

Methods:
  __init__(self, name: str, log_dir: str = "logs")
    - Setup logging configuration
    - Create log files in logs/ folder
    - Setup different handlers for different log types

  log_info(self, message: str, **kwargs)
  log_error(self, message: str, exception: Exception = None)
  log_debug(self, message: str)
  log_warning(self, message: str)
  
  log_api_call(self, api_name: str, method: str, cost: float, duration: float)
    - Log API calls to logs/api_logs/
    - Track cost and duration
    
  log_video_generation(self, topic: str, status: str, duration: float)
    - Log video generation to logs/daily_logs/

Log Files:
  - logs/daily_logs/[date].log (daily operations)
  - logs/error_logs/[date].log (errors only)
  - logs/api_logs/[date].log (API calls + costs)
  - logs/performance_logs/[date].log (performance metrics)

SPECIFICATIONS FOR src/core/performance_monitor.py:

Class: PerformanceMonitor
Purpose: Track system performance and costs

Methods:
  __init__(self)
    - Initialize metrics tracking
    - Setup start time

  track_api_cost(self, api_name: str, cost: float)
    - Track API costs
    - Log to logs/api_logs/

  track_duration(self, operation: str, duration: float)
    - Track operation duration
    - Log to logs/performance_logs/

  get_daily_summary(self) -> dict
    - Return daily stats: {
      "total_cost": float,
      "total_videos": int,
      "avg_duration": float,
      "errors": int
    }

SPECIFICATIONS FOR tests/test_video_assembler.py:

Unit Tests:
  - test_video_assembler_init
  - test_assemble_video_returns_string
  - test_assemble_video_creates_file
  - test_add_transitions
  - test_apply_subtitles
  - test_verify_final_quality
  - test_error_handling_missing_files

CODE REQUIREMENTS:
  - Type hints on all methods
  - Docstrings on all methods
  - PEP 8 compliant
  - Error handling and logging
  - File path validation

OUTPUT CHECKLIST:
After generating, verify:
  ✅ src/video/video_assembler.py created
  ✅ src/core/logger.py created
  ✅ src/core/performance_monitor.py created
  ✅ tests/test_video_assembler.py created
  ✅ Video assembly working
  ✅ All log files created
  ✅ Performance tracking working
  ✅ All unit tests pass
```

---

## 📋 SESSION EXECUTION ORDER

**Day 1:**
1. Session 1: Orchestrator (30 min)
2. Session 2: HybridScriptGenerator (45 min) ⭐
3. Session 3: Agent Verifier (30 min)
4. Session 4: Tone Manager (30 min)
5. Session 5: TTS + Images (45 min)

**Day 2:**
1. Session 6: Video Assembler + Logging (45 min)
2. Integration Testing (2-3 hours)

**Day 3:**
1. Agent Accuracy Verification
2. Generate 5 test videos
3. Measure ≥80% accuracy
4. Gate 2 Pass/Fail decision

---

## ✅ READY TO EXECUTE

All 6 Cursor prompts are ready to copy/paste.  
No additional configuration needed.  
All dependencies already installed in venv.

**Start with Session 1.**

