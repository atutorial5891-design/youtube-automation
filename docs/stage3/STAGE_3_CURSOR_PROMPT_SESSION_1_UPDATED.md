# STAGE 3 CURSOR PROMPT - SESSION 1 (Days 1-2)
**Focus:** Fact-Checking Module with Pre-checks & Validation  
**Duration:** 2 days  
**Objective:** Build FactChecker class that validates claims in scripts and creates fact-check reports

---

## 🔍 PRE-CHECK: ENVIRONMENT VALIDATION

**Before starting, run this validation script to ensure your environment is ready:**

```bash
#!/bin/bash
echo "=== STAGE 3 SESSION 1 PRE-CHECK ==="

echo ""
echo "Directory Structure:"
mkdir -p src/quality src/analysis src/core tests logs/fact_check_reports logs/human_reviews config

echo "Verifying Stage 2 files exist:"
test -f src/api/chatgpt_client.py && echo "✅ ChatGPT client" || echo "❌ Missing: src/api/chatgpt_client.py"
test -f src/api/deepseek_client.py && echo "✅ DeepSeek client" || echo "❌ Missing: src/api/deepseek_client.py"
test -f src/core/logger.py && echo "✅ Logger" || echo "❌ Missing: src/core/logger.py"

echo ""
echo "Mock Data Validation:"
metadata_count=$(ls data/approved_scripts/*_metadata.json 2>/dev/null | wc -l)
echo "✅ Mock metadata files: $metadata_count/5"

video_count=$(ls data/generated_videos/*.mp4 2>/dev/null | wc -l)
echo "✅ Mock videos: $video_count/5"

echo ""
echo "Python dependencies:"
python3 -c "import pytest; print('✅ pytest installed')" 2>/dev/null || echo "❌ pytest missing"
python3 -c "import json; print('✅ json available')" 2>/dev/null || echo "❌ json missing"

echo ""
echo "API credentials:"
test -f credentials/api_keys.txt && echo "✅ API keys file exists" || echo "❌ credentials/api_keys.txt missing"

echo ""
echo "Pre-check complete. You can now start Session 1."
```

---

## REQUIREMENT 0: STAGE 2 COMPATIBILITY CHECK

**Create this compatibility validation function in `src/core/stage3_loader.py`:**

```python
from pathlib import Path
import json

def validate_stage2_compatibility():
    """Verify Stage 2 outputs are compatible with Stage 3"""
    
    issues = []
    
    # Check if Stage 2 modules exist
    required_files = [
        'src/api/chatgpt_client.py',
        'src/api/deepseek_client.py',
        'src/core/logger.py'
    ]
    
    for file in required_files:
        if not Path(file).exists():
            issues.append(f"Missing Stage 2 file: {file}")
    
    # Check mock data validity
    metadata_files = list(Path('data/approved_scripts').glob('*_metadata.json'))
    if len(metadata_files) < 5:
        issues.append(f"Expected 5 metadata files, found {len(metadata_files)}")
    
    for meta_file in metadata_files:
        try:
            with open(meta_file) as f:
                json.load(f)
        except json.JSONDecodeError:
            issues.append(f"Invalid JSON in {meta_file}")
    
    # Check if generated videos exist
    video_files = list(Path('data/generated_videos').glob('*.mp4'))
    if len(video_files) < 5:
        issues.append(f"Expected 5 video files, found {len(video_files)}")
    
    if issues:
        print("❌ Stage 2 Compatibility Issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    
    print("✅ Stage 2 outputs compatible with Stage 3")
    return True
```

---

## REQUIREMENT 1: STAGE 3 LOADER

**Create `src/core/stage3_loader.py` - loads Stage 2 outputs for Stage 3 processing:**

```python
from pathlib import Path
import json

def load_stage2_outputs():
    """Load all Stage 2 generated scripts with metadata
    
    Returns: List of dicts with script_id, script, topic, metadata
    """
    videos = []
    
    metadata_dir = Path('data/approved_scripts')
    for meta_file in sorted(metadata_dir.glob('*_metadata.json')):
        with open(meta_file) as f:
            metadata = json.load(f)
        
        videos.append({
            'script_id': metadata.get('script_id'),
            'script': metadata.get('script_content'),
            'topic': metadata.get('topic'),
            'metadata': metadata
        })
    
    return videos

def validate_stage2_compatibility():
    """Verify Stage 2 outputs are compatible with Stage 3"""
    issues = []
    
    required_files = [
        'src/api/chatgpt_client.py',
        'src/api/deepseek_client.py',
        'src/core/logger.py'
    ]
    
    for file in required_files:
        if not Path(file).exists():
            issues.append(f"Missing: {file}")
    
    metadata_files = list(Path('data/approved_scripts').glob('*_metadata.json'))
    if len(metadata_files) < 5:
        issues.append(f"Only {len(metadata_files)}/5 metadata files")
    
    if issues:
        print("❌ Compatibility issues:", issues)
        return False
    
    print("✅ Stage 2 ready for Stage 3")
    return True
```

---

## REQUIREMENT 2: FACT-CHECKER CLASS

**Create `src/quality/fact_checker.py` - validates claims in scripts**

```python
from src.api.chatgpt_client import ChatGPTClient
import json
from pathlib import Path

class FactChecker:
    """Fact-checks claims in video scripts using ChatGPT"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = ChatGPTClient(api_key=api_key, model='gpt-4o-mini')
        self.reports_dir = Path('logs/fact_check_reports')
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def fact_check_script(self, script_id, script, topic):
        """Fact-check claims in a script
        
        Args:
            script_id: Video script identifier
            script: Full script text
            topic: Video topic
        
        Returns: Dict with fact-check results
        """
        prompt = f"""Fact-check the following script and identify:
1. Claims that are definitely SAFE (verified facts)
2. Claims that warrant CAUTION (need verification)
3. Claims that are RISKY (potentially false or unverifiable)

Topic: {topic}

Script:
{script}

Return JSON with:
{{
    "script_id": "{script_id}",
    "claims_safe": ["list of safe claims"],
    "claims_caution": ["list of caution claims"],
    "claims_risk": ["list of risky claims"],
    "risk_count": number,
    "confidence": percentage
}}"""
        
        response = self.client.call_api(prompt)
        
        # Parse response
        try:
            result = json.loads(response.get('choices', [{}])[0].get('text', '{}'))
        except:
            result = {
                'script_id': script_id,
                'claims_safe': [],
                'claims_caution': [],
                'claims_risk': [],
                'risk_count': 0,
                'confidence': 0
            }
        
        # Save report
        report_path = self.reports_dir / f'{script_id}_fact_check.json'
        with open(report_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        return result

    def load_report(self, script_id):
        """Load existing fact-check report"""
        report_path = self.reports_dir / f'{script_id}_fact_check.json'
        if report_path.exists():
            with open(report_path) as f:
                return json.load(f)
        return None
```

**CRITICAL API ALLOCATION RULE:**
- ✅ Use ChatGPTClient for fact-checking (accurate claims validation)
- ❌ NEVER use DeepSeek for fact-checking (not reliable for accuracy)
- DeepSeek is reserved for cheap topic generation in Stage 1

---

## REQUIREMENT 3: DATA FORMAT SPECIFICATIONS

**Input Format (from Stage 2):**
```json
{
  "script_id": "20260515_how_to_learn_python",
  "topic": "How to Learn Python for Beginners",
  "script_content": "Full script text here...",
  "tone": "Professional Educational"
}
```

**Output Format (FactChecker report saved to logs/fact_check_reports/):**
```json
{
  "script_id": "20260515_how_to_learn_python",
  "claims_safe": [
    "Python is a programming language",
    "Python uses indentation for blocks"
  ],
  "claims_caution": [
    "You can learn Python in 30 days",
    "Python is the easiest language"
  ],
  "claims_risk": [
    "You can get a job in 2 weeks",
    "Python will be free forever"
  ],
  "risk_count": 2,
  "confidence": 85,
  "created_at": "2026-05-21T10:30:00Z"
}
```

**Directory Structure to Create:**
```
src/quality/
├── __init__.py
├── fact_checker.py          ← REQUIREMENT 2
├── final_reviewer.py        ← Will create in Session 2
└── review_display.py        ← Helper for display

src/analysis/
├── __init__.py
├── quality_gates.py         ← Will create in Session 3
├── agent_analyzer.py        ← Will create in Session 3
├── tone_analytics.py        ← Will create in Session 3
└── final_decision.py        ← Will create in Session 3

src/core/
├── stage3_loader.py         ← REQUIREMENT 0
└── orchestrator.py          ← Will create in Session 3

logs/
├── fact_check_reports/      ← Session 1 output
├── human_reviews/           ← Session 2 output
├── gate_results/            ← Session 3 output
└── stage_3_final_report.json ← Final decision

tests/
├── test_fact_checker.py     ← REQUIREMENT 4
├── test_final_reviewer.py   ← Session 2
└── test_stage3_complete.py  ← Session 3
```

---

## REQUIREMENT 4: UNIT TESTS

**Create `tests/test_fact_checker.py` - comprehensive tests for FactChecker:**

```python
import pytest
import json
from pathlib import Path
from src.quality.fact_checker import FactChecker

class MockChatGPTClient:
    """Mock ChatGPT client for testing"""
    def call_api(self, prompt):
        return {
            'choices': [{
                'text': json.dumps({
                    'claims_safe': ['Safe claim 1'],
                    'claims_caution': ['Caution claim 1'],
                    'claims_risk': ['Risky claim 1'],
                    'risk_count': 1,
                    'confidence': 85
                })
            }]
        }

@pytest.fixture
def fact_checker():
    """Create test instance"""
    checker = FactChecker(api_key='test_key')
    # Inject mock client
    checker.client = MockChatGPTClient()
    return checker

def test_fact_checker_initialization(fact_checker):
    """Test FactChecker initializes correctly"""
    assert fact_checker is not None
    assert fact_checker.reports_dir.exists()

def test_fact_check_script_returns_dict(fact_checker):
    """Test fact_check_script returns proper format"""
    result = fact_checker.fact_check_script(
        'test_script_001',
        'This is a test script',
        'Test Topic'
    )
    
    assert isinstance(result, dict)
    assert 'script_id' in result
    assert 'claims_safe' in result
    assert 'claims_caution' in result
    assert 'claims_risk' in result
    assert 'risk_count' in result

def test_fact_check_creates_report_file(fact_checker):
    """Test fact_check_script saves report to file"""
    script_id = 'test_script_002'
    fact_checker.fact_check_script(script_id, 'Test', 'Topic')
    
    report_file = fact_checker.reports_dir / f'{script_id}_fact_check.json'
    assert report_file.exists()
    
    with open(report_file) as f:
        data = json.load(f)
    assert data['script_id'] == script_id

def test_load_report(fact_checker):
    """Test loading existing report"""
    script_id = 'test_script_003'
    fact_checker.fact_check_script(script_id, 'Test', 'Topic')
    
    loaded = fact_checker.load_report(script_id)
    assert loaded is not None
    assert loaded['script_id'] == script_id

def test_fact_check_multiple_scripts(fact_checker):
    """Test processing multiple scripts"""
    for i in range(5):
        fact_checker.fact_check_script(
            f'test_script_{i:03d}',
            f'Script {i}',
            f'Topic {i}'
        )
    
    reports = list(fact_checker.reports_dir.glob('*.json'))
    assert len(reports) >= 5

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

---

## PERFORMANCE TARGETS

- **API Response Time:** <10 seconds per script
- **Claim Processing:** <5 seconds per high-risk claim
- **Test Execution:** <15 seconds total for all FactChecker tests
- **Report File I/O:** <3 seconds per report save

---

## ERROR HANDLING & RECOVERY

### Error: ChatGPTClient fails
```python
# Add error handling to fact_check_script:
try:
    response = self.client.call_api(prompt)
except Exception as e:
    print(f"API error: {e}")
    result = {
        'script_id': script_id,
        'claims_safe': [],
        'claims_caution': [script[:100]],  # Default to caution
        'claims_risk': [],
        'risk_count': 0,
        'error': str(e)
    }
```

### Error: Invalid JSON response
```python
# Response might not be valid JSON
try:
    result = json.loads(response_text)
except json.JSONDecodeError:
    # Parse manually or return default
    result = {'error': 'Invalid response format'}
```

### Error: Missing API key
```bash
# Verify API key exists:
cat credentials/api_keys.txt | grep OPENAI
# Should output your OpenAI API key
```

---

## VERIFICATION STEPS (End of Days 1-2)

**After completing all code, verify with:**

```bash
#!/bin/bash
echo "=== SESSION 1 VERIFICATION ==="

echo ""
echo "1. Code Files Created:"
test -f src/core/stage3_loader.py && echo "✅ stage3_loader.py" || echo "❌ Missing"
test -f src/quality/fact_checker.py && echo "✅ fact_checker.py" || echo "❌ Missing"
test -f tests/test_fact_checker.py && echo "✅ test_fact_checker.py" || echo "❌ Missing"

echo ""
echo "2. Run Tests:"
python3 -m pytest tests/test_fact_checker.py -v

echo ""
echo "3. Check Reports:"
report_count=$(ls logs/fact_check_reports/*.json 2>/dev/null | wc -l)
echo "Fact-check reports: $report_count/5"

echo ""
echo "4. Verify Report Format:"
python3 << 'EOF'
import json
from pathlib import Path

reports = list(Path('logs/fact_check_reports').glob('*.json'))
if reports:
    with open(reports[0]) as f:
        sample = json.load(f)
    
    required_fields = ['script_id', 'claims_safe', 'claims_caution', 'claims_risk', 'risk_count']
    all_present = all(field in sample for field in required_fields)
    
    if all_present:
        print("✅ Report format valid")
    else:
        print("❌ Report missing fields")
else:
    print("❌ No reports created")
EOF

echo ""
echo "Session 1 verification complete!"
```

---

## BACKWARD COMPATIBILITY CHECK

**Ensure Stage 3 can load Stage 2 outputs:**

```python
# In your test, verify:
from src.core.stage3_loader import load_stage2_outputs

videos = load_stage2_outputs()
assert len(videos) == 5, "Should load all 5 mock videos"
assert all('script_id' in v for v in videos), "All must have script_id"
assert all('script' in v for v in videos), "All must have script content"
```

---

## NEXT: DAYS 1-2 IMPLEMENTATION STEPS

1. **Day 1 Morning:**
   - Run pre-check validation
   - Create src/quality and src/analysis directories
   - Create src/core/stage3_loader.py with validation function
   - Verify Stage 2 files load correctly

2. **Day 1 Afternoon:**
   - Create src/quality/fact_checker.py with FactChecker class
   - Review API client integration (ChatGPT only)
   - Test basic initialization

3. **Day 2 Morning:**
   - Create tests/test_fact_checker.py
   - Run pytest - all tests should pass
   - Verify mock data loads and processes

4. **Day 2 Afternoon:**
   - Run fact-checking on all 5 mock videos
   - Verify fact-check reports created (logs/fact_check_reports/)
   - Run verification script
   - Document results

---

## SUCCESS CRITERIA

✅ All tests pass (pytest tests/test_fact_checker.py -v)  
✅ 5 fact-check reports created in logs/fact_check_reports/  
✅ Each report has required fields  
✅ Risk counts calculated correctly  
✅ Reports saved as valid JSON  

---

**End of Session 1 Prompt - Days 1-2**
