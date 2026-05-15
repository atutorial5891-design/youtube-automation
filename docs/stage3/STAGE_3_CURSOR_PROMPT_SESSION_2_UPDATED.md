# STAGE 3 CURSOR PROMPT - SESSION 2 (Day 3)
**Focus:** Human Review Module  
**Duration:** 1 day  
**Objective:** Build FinalReviewer class for human quality assessment

---

## 🔍 PRE-SESSION 2 CHECK

**Verify Session 1 completed successfully:**

```bash
#!/bin/bash
echo "=== SESSION 2 PRE-CHECK ==="

echo ""
echo "Session 1 Outputs:"
report_count=$(ls logs/fact_check_reports/*.json 2>/dev/null | wc -l)
echo "Fact-check reports: $report_count/5"

if [ "$report_count" -lt 5 ]; then
    echo "❌ Session 1 did not complete - only $report_count/5 reports"
    echo "Run Session 1 again before starting Session 2"
    exit 1
fi

echo ""
echo "Code Files from Session 1:"
test -f src/quality/fact_checker.py && echo "✅ fact_checker.py exists" || echo "❌ Missing"
test -f tests/test_fact_checker.py && echo "✅ test_fact_checker.py exists" || echo "❌ Missing"

echo ""
echo "✅ Session 1 complete - ready for Session 2"
```

---

## REQUIREMENT 1: FINAL REVIEWER CLASS

**Create `src/quality/final_reviewer.py` - human quality assessment**

```python
import json
from pathlib import Path

class FinalReviewer:
    """Performs human-equivalent quality review of videos"""
    
    def __init__(self):
        self.reviews_dir = Path('logs/human_reviews')
        self.reviews_dir.mkdir(parents=True, exist_ok=True)
    
    def review_video(self, script_id, video_path, fact_check_report):
        """Review a video against quality criteria
        
        Args:
            script_id: Video identifier
            video_path: Path to video file
            fact_check_report: Fact-check results from Session 1
        
        Returns: Dict with review results
        """
        # Simulate human review checklist
        checklist = {
            'audio_quality': True,
            'video_quality': True,
            'script_accuracy': fact_check_report.get('claims_risk', []) == [],
            'tone_appropriate': True,
            'pacing_good': True
        }
        
        # Decision logic
        risk_count = fact_check_report.get('risk_count', 0)
        all_checks_pass = all(checklist.values())
        
        if risk_count > 2:
            approval_status = 'REJECTED'
            rejection_reason = 'Too many risky claims in script'
        elif not all_checks_pass:
            approval_status = 'REJECTED'
            rejection_reason = 'Quality checklist failed'
        else:
            approval_status = 'APPROVED'
            rejection_reason = None
        
        # Build review result
        review = {
            'script_id': script_id,
            'approval_status': approval_status,
            'rejection_reason': rejection_reason,
            'checklist': checklist,
            'fact_check_risk_count': risk_count,
            'reviewer_notes': 'Human review completed',
            'created_at': '2026-05-21'
        }
        
        # Save review
        review_path = self.reviews_dir / f'{script_id}_human_review.json'
        with open(review_path, 'w') as f:
            json.dump(review, f, indent=2)
        
        return review
    
    def load_review(self, script_id):
        """Load existing review"""
        review_path = self.reviews_dir / f'{script_id}_human_review.json'
        if review_path.exists():
            with open(review_path) as f:
                return json.load(f)
        return None
    
    def batch_review_all_videos(self, fact_check_reports_dir):
        """Review all fact-checked videos"""
        results = []
        
        for report_file in sorted(Path(fact_check_reports_dir).glob('*.json')):
            with open(report_file) as f:
                report = json.load(f)
            
            script_id = report.get('script_id')
            review = self.review_video(script_id, None, report)
            results.append(review)
        
        return results
```

---

## REQUIREMENT 2: REVIEW DATA FORMATS

**Input Format (from Session 1 - fact-check reports):**
```json
{
  "script_id": "20260515_how_to_learn_python",
  "claims_safe": [...],
  "claims_caution": [...],
  "claims_risk": [...],
  "risk_count": 0,
  "confidence": 85
}
```

**Output Format (saved to logs/human_reviews/):**
```json
{
  "script_id": "20260515_how_to_learn_python",
  "approval_status": "APPROVED",
  "rejection_reason": null,
  "checklist": {
    "audio_quality": true,
    "video_quality": true,
    "script_accuracy": true,
    "tone_appropriate": true,
    "pacing_good": true
  },
  "fact_check_risk_count": 0,
  "reviewer_notes": "Human review completed",
  "created_at": "2026-05-21"
}
```

**Approval Logic:**
- `APPROVED`: All checklist items pass AND risk_count ≤ 2
- `REJECTED`: Any checklist item fails OR risk_count > 2

---

## REQUIREMENT 3: VALIDATION SCRIPT

**Create script to validate human reviews:**

```bash
#!/bin/bash
echo "=== HUMAN REVIEW VALIDATION ==="

echo ""
echo "Reviews created:"
review_count=$(ls logs/human_reviews/*.json 2>/dev/null | wc -l)
echo "Total: $review_count/5"

echo ""
echo "Approval breakdown:"
python3 << 'EOF'
import json
from pathlib import Path

approved = 0
rejected = 0
reviews = list(Path('logs/human_reviews').glob('*.json'))

for review_file in reviews:
    with open(review_file) as f:
        data = json.load(f)
    status = data.get('approval_status')
    
    if status == 'APPROVED':
        approved += 1
    elif status == 'REJECTED':
        rejected += 1

total = len(reviews)
approval_rate = (approved / total * 100) if total > 0 else 0

print(f"Approved: {approved}/{total} ({approval_rate:.0f}%)")
print(f"Rejected: {rejected}/{total}")

if approval_rate >= 80:
    print(f"✅ Approval rate meets threshold (≥80%)")
else:
    print(f"⚠️  Approval rate below threshold (need ≥80%, have {approval_rate:.0f}%)")
EOF

echo ""
echo "Validation complete."
```

---

## REQUIREMENT 4: UNIT TESTS

**Create `tests/test_final_reviewer.py`:**

```python
import pytest
import json
from pathlib import Path
from src.quality.final_reviewer import FinalReviewer

@pytest.fixture
def reviewer():
    """Create test instance"""
    return FinalReviewer()

def test_final_reviewer_initialization(reviewer):
    """Test FinalReviewer initializes correctly"""
    assert reviewer is not None
    assert reviewer.reviews_dir.exists()

def test_review_video_returns_dict(reviewer):
    """Test review_video returns proper format"""
    mock_fact_check = {
        'script_id': 'test_001',
        'claims_risk': [],
        'risk_count': 0
    }
    
    result = reviewer.review_video('test_001', None, mock_fact_check)
    
    assert isinstance(result, dict)
    assert 'script_id' in result
    assert 'approval_status' in result
    assert result['approval_status'] in ['APPROVED', 'REJECTED']

def test_review_approves_low_risk(reviewer):
    """Test video with no risk claims gets approved"""
    mock_fact_check = {
        'script_id': 'test_002',
        'claims_risk': [],
        'risk_count': 0
    }
    
    result = reviewer.review_video('test_002', None, mock_fact_check)
    assert result['approval_status'] == 'APPROVED'

def test_review_rejects_high_risk(reviewer):
    """Test video with high risk claims gets rejected"""
    mock_fact_check = {
        'script_id': 'test_003',
        'claims_risk': ['claim1', 'claim2', 'claim3'],
        'risk_count': 3
    }
    
    result = reviewer.review_video('test_003', None, mock_fact_check)
    assert result['approval_status'] == 'REJECTED'

def test_review_creates_file(reviewer):
    """Test review_video saves file"""
    mock_fact_check = {
        'script_id': 'test_004',
        'claims_risk': [],
        'risk_count': 0
    }
    
    reviewer.review_video('test_004', None, mock_fact_check)
    
    review_file = reviewer.reviews_dir / 'test_004_human_review.json'
    assert review_file.exists()

def test_load_review(reviewer):
    """Test loading existing review"""
    mock_fact_check = {
        'script_id': 'test_005',
        'claims_risk': [],
        'risk_count': 0
    }
    
    reviewer.review_video('test_005', None, mock_fact_check)
    loaded = reviewer.load_review('test_005')
    
    assert loaded is not None
    assert loaded['script_id'] == 'test_005'

def test_batch_review_all_videos(reviewer):
    """Test batch reviewing all fact-checked videos"""
    # First ensure fact-check reports exist
    fact_check_dir = Path('logs/fact_check_reports')
    if fact_check_dir.exists() and list(fact_check_dir.glob('*.json')):
        results = reviewer.batch_review_all_videos(fact_check_dir)
        assert len(results) > 0

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

---

## ERROR HANDLING

### Error: Fact-check reports not found
```python
# Verify Session 1 completed:
fact_check_dir = Path('logs/fact_check_reports')
if not fact_check_dir.exists() or not list(fact_check_dir.glob('*.json')):
    print("❌ No fact-check reports found")
    print("Run Session 1 first")
```

### Error: Missing JSON fields in fact-check report
```python
# Safely get values with defaults:
risk_count = fact_check_report.get('risk_count', 0)
claims_risk = fact_check_report.get('claims_risk', [])
```

---

## PERFORMANCE TARGETS

- **Review per video:** <5 seconds
- **Batch review 5 videos:** <30 seconds total
- **File I/O per review:** <2 seconds
- **Test execution:** <15 seconds

---

## VERIFICATION STEPS (End of Day 3)

```bash
#!/bin/bash
echo "=== SESSION 2 VERIFICATION ==="

echo ""
echo "1. Code Files Created:"
test -f src/quality/final_reviewer.py && echo "✅ final_reviewer.py" || echo "❌ Missing"
test -f tests/test_final_reviewer.py && echo "✅ test_final_reviewer.py" || echo "❌ Missing"

echo ""
echo "2. Run Tests:"
python3 -m pytest tests/test_final_reviewer.py -v

echo ""
echo "3. Check Reviews:"
review_count=$(ls logs/human_reviews/*.json 2>/dev/null | wc -l)
echo "Human review files: $review_count/5"

echo ""
echo "4. Verify Approval Rates:"
python3 << 'EOF'
import json
from pathlib import Path

reviews = list(Path('logs/human_reviews').glob('*.json'))
if not reviews:
    print("❌ No reviews found")
    exit(1)

approved = sum(1 for r in reviews if json.load(open(r))['approval_status'] == 'APPROVED')
approval_rate = approved / len(reviews) * 100

print(f"Approved: {approved}/{len(reviews)} ({approval_rate:.0f}%)")
print(f"Approval rate: {approval_rate:.0f}%")

if approval_rate >= 80:
    print("✅ Meets ≥80% threshold")
else:
    print(f"⚠️  Below threshold (need 80%, have {approval_rate:.0f}%)")
EOF

echo ""
echo "Session 2 verification complete!"
```

---

## NEXT: SESSION 3 PREPARATION

At the end of Day 3, you should have:
- ✅ 5 human review files in logs/human_reviews/
- ✅ Approval status (APPROVED or REJECTED) for each
- ✅ Approval rate ≥80% (preferably 100%)

Session 3 will use these reviews to:
- Run quality gates validation
- Analyze agent performance
- Analyze tone consistency
- Make final GO/NO-GO decision

---

**End of Session 2 Prompt - Day 3**
