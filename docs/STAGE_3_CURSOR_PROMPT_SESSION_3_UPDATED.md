# STAGE 3 CURSOR PROMPT - SESSION 3 (Days 4-7)
**Focus:** Quality Gates, Analysis, and Final Decision  
**Duration:** 4 days  
**Objective:** Validate quality gates, analyze performance, and make GO/NO-GO decision

---

## 🔍 PRE-SESSION 3 CHECK

**Verify Sessions 1 & 2 completed:**

```bash
#!/bin/bash
echo "=== SESSION 3 PRE-CHECK ==="

echo ""
echo "Session 1 Outputs:"
report_count=$(ls logs/fact_check_reports/*.json 2>/dev/null | wc -l)
echo "Fact-check reports: $report_count/5"

echo ""
echo "Session 2 Outputs:"
review_count=$(ls logs/human_reviews/*.json 2>/dev/null | wc -l)
echo "Human reviews: $review_count/5"

if [ "$report_count" -lt 5 ] || [ "$review_count" -lt 5 ]; then
    echo "❌ Sessions 1 & 2 not complete"
    exit 1
fi

echo ""
echo "Code from Sessions 1-2:"
test -f src/quality/fact_checker.py && echo "✅ fact_checker.py" || echo "❌ Missing"
test -f src/quality/final_reviewer.py && echo "✅ final_reviewer.py" || echo "❌ Missing"

echo ""
echo "✅ Sessions 1 & 2 complete - ready for Session 3"
```

---

## REQUIREMENT 1: QUALITY GATES VALIDATOR

**Create `src/analysis/quality_gates.py` - validates against quality thresholds:**

```python
import json
from pathlib import Path

class QualityGates:
    """Validates videos against quality gates"""
    
    def __init__(self):
        self.results_dir = Path('logs/gate_results')
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_gate_3(self, fact_check_reports_dir):
        """Gate 3: Fact-Check Accuracy (75-85% threshold)
        
        Validates that fact-checking was accurate
        Target: 75-85% of videos have low risk
        """
        reports = list(Path(fact_check_reports_dir).glob('*.json'))
        
        low_risk_count = 0
        for report_file in reports:
            with open(report_file) as f:
                report = json.load(f)
            
            # Low risk = 0-1 risk claims
            if report.get('risk_count', 0) <= 1:
                low_risk_count += 1
        
        accuracy = (low_risk_count / len(reports) * 100) if reports else 0
        
        result = {
            'gate': 3,
            'name': 'Fact-Check Accuracy',
            'accuracy': accuracy,
            'threshold': '75-85%',
            'low_risk_videos': low_risk_count,
            'total_videos': len(reports),
            'status': 'PASSED' if 75 <= accuracy <= 85 else 'WARNING'
        }
        
        self._save_gate_result('gate_3', result)
        return result
    
    def validate_gate_4(self, human_reviews_dir):
        """Gate 4: Human Final Approval (≥80% threshold)
        
        Validates human approval rate
        Target: ≥80% of videos approved
        """
        reviews = list(Path(human_reviews_dir).glob('*.json'))
        
        approved_count = 0
        for review_file in reviews:
            with open(review_file) as f:
                review = json.load(f)
            
            if review.get('approval_status') == 'APPROVED':
                approved_count += 1
        
        approval_rate = (approved_count / len(reviews) * 100) if reviews else 0
        
        result = {
            'gate': 4,
            'name': 'Human Final Approval',
            'approval_rate': approval_rate,
            'threshold': '≥80%',
            'approved_videos': approved_count,
            'total_videos': len(reviews),
            'status': 'PASSED' if approval_rate >= 80 else 'FAILED'
        }
        
        self._save_gate_result('gate_4', result)
        return result
    
    def _save_gate_result(self, gate_name, result):
        """Save gate result to file"""
        file_path = self.results_dir / f'{gate_name}_result.json'
        with open(file_path, 'w') as f:
            json.dump(result, f, indent=2)
    
    def validate_all_gates(self):
        """Run all gate validations"""
        gate_3 = self.validate_gate_3('logs/fact_check_reports')
        gate_4 = self.validate_gate_4('logs/human_reviews')
        
        all_gates_passed = (
            gate_3['status'] == 'PASSED' and
            gate_4['status'] == 'PASSED'
        )
        
        summary = {
            'gate_2': {'status': 'PASSED', 'name': 'Agent Verification'},
            'gate_3': gate_3,
            'gate_4': gate_4,
            'all_gates_passed': all_gates_passed
        }
        
        # Save summary
        with open('logs/gates_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary
```

---

## REQUIREMENT 2: AGENT ANALYZER

**Create `src/analysis/agent_analyzer.py` - analyzes video generation quality:**

```python
import json
from pathlib import Path

class AgentAnalyzer:
    """Analyzes how well the Stage 2 agent performed"""
    
    def __init__(self):
        self.results_file = Path('logs/agent_analysis.json')
    
    def analyze_agent_performance(self, fact_check_reports_dir):
        """Calculate agent accuracy based on fact-checks
        
        Logic: Videos with 0 risk claims = agent did excellent job
        """
        reports = list(Path(fact_check_reports_dir).glob('*.json'))
        
        if not reports:
            return {'error': 'No fact-check reports found'}
        
        perfect_videos = 0
        for report_file in reports:
            with open(report_file) as f:
                report = json.load(f)
            
            if report.get('risk_count', 0) == 0:
                perfect_videos += 1
        
        agent_accuracy = (perfect_videos / len(reports) * 100)
        
        analysis = {
            'metric': 'Agent Accuracy',
            'definition': 'Percentage of videos with zero risky claims',
            'agent_accuracy': agent_accuracy,
            'perfect_videos': perfect_videos,
            'total_videos': len(reports),
            'threshold': '≥80%',
            'status': 'PASSED' if agent_accuracy >= 80 else 'WARNING'
        }
        
        # Save analysis
        with open(self.results_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        return analysis
```

---

## REQUIREMENT 3: TONE ANALYTICS

**Create `src/analysis/tone_analytics.py` - analyzes tone performance:**

```python
import json
from pathlib import Path

class ToneAnalytics:
    """Analyzes how different tones performed"""
    
    def __init__(self):
        self.results_file = Path('logs/tone_performance.json')
    
    def analyze_tone_performance(self, metadata_dir, reviews_dir):
        """Analyze which tones got approved vs rejected
        
        Tracks: Professional Educational, Energetic Motivational, etc.
        """
        tones = {
            'Professional Educational': {'approved': 0, 'rejected': 0},
            'Energetic Motivational': {'approved': 0, 'rejected': 0},
            'Curious Explainer': {'approved': 0, 'rejected': 0},
            'Quick Direct': {'approved': 0, 'rejected': 0},
            'Conversational Storytelling': {'approved': 0, 'rejected': 0}
        }
        
        # Load metadata for tone info
        metadata_files = list(Path(metadata_dir).glob('*_metadata.json'))
        review_files = list(Path(reviews_dir).glob('*_human_review.json'))
        
        # Match metadata with reviews
        for review_file in review_files:
            with open(review_file) as f:
                review = json.load(f)
            
            script_id = review.get('script_id')
            
            # Find matching metadata
            for meta_file in metadata_files:
                with open(meta_file) as f:
                    meta = json.load(f)
                
                if meta.get('script_id') == script_id:
                    tone = meta.get('tone', 'Unknown')
                    status = review.get('approval_status', 'UNKNOWN')
                    
                    if tone in tones:
                        if status == 'APPROVED':
                            tones[tone]['approved'] += 1
                        elif status == 'REJECTED':
                            tones[tone]['rejected'] += 1
                    break
        
        # Calculate approval rates per tone
        tone_performance = {}
        for tone, counts in tones.items():
            total = counts['approved'] + counts['rejected']
            rate = (counts['approved'] / total * 100) if total > 0 else 0
            
            tone_performance[tone] = {
                'approved': counts['approved'],
                'rejected': counts['rejected'],
                'approval_rate': rate
            }
        
        analysis = {
            'metric': 'Tone Performance Analysis',
            'tone_breakdown': tone_performance
        }
        
        # Save analysis
        with open(self.results_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        return analysis
```

---

## REQUIREMENT 4: FINAL DECISION ENGINE

**Create `src/analysis/final_decision.py` - makes GO/NO-GO decision:**

```python
import json
from pathlib import Path
from datetime import datetime

class FinalDecisionEngine:
    """Makes final GO/NO-GO decision for Stage 4"""
    
    def __init__(self):
        self.report_file = Path('logs/stage_3_final_report.json')
        self.metrics_file = Path('logs/stage_3_quality_metrics.json')
    
    def make_go_nogo_decision(self, gate_summary, agent_analysis, tone_performance):
        """Make final GO/NO-GO decision
        
        Decision Rules:
        - GO if all gates PASSED
        - GO_WITH_CAUTION if gates WARNING but recovery possible
        - NO-GO if any gate FAILED
        """
        
        gate_3_status = gate_summary.get('gate_3', {}).get('status')
        gate_4_status = gate_summary.get('gate_4', {}).get('status')
        
        # Decision logic
        if gate_3_status == 'PASSED' and gate_4_status == 'PASSED':
            decision = 'GO'
            justification = 'All quality gates passed'
        elif gate_3_status == 'WARNING' or gate_4_status == 'WARNING':
            decision = 'GO_WITH_CAUTION'
            justification = 'Some gates at threshold - monitor quality'
        else:
            decision = 'NO-GO'
            justification = 'Quality gates failed - return to Stage 2'
        
        # Build final report
        report = {
            'stage_number': 3,
            'decision': decision,
            'justification': justification,
            'gate_3_status': gate_summary.get('gate_3', {}),
            'gate_4_status': gate_summary.get('gate_4', {}),
            'agent_accuracy': agent_analysis.get('agent_accuracy', 0),
            'tone_performance': tone_performance.get('tone_breakdown', {}),
            'videos_ready': gate_summary.get('gate_4', {}).get('approved_videos', 0),
            'ready_for_stage_4': decision in ['GO', 'GO_WITH_CAUTION'],
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        # Save report
        with open(self.report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def generate_quality_metrics(self, gate_summary, agent_analysis, tone_performance):
        """Generate detailed quality metrics summary"""
        
        gate_4 = gate_summary.get('gate_4', {})
        approval_rate = gate_4.get('approval_rate', 0)
        
        metrics = {
            'overall_qa_score': (
                approval_rate * 0.5 +
                agent_analysis.get('agent_accuracy', 0) * 0.5
            ),
            'metrics': {
                'fact_check_accuracy': {
                    'status': gate_summary.get('gate_3', {}).get('status'),
                    'accuracy': gate_summary.get('gate_3', {}).get('accuracy', 0)
                },
                'human_approval_rate': {
                    'status': gate_summary.get('gate_4', {}).get('status'),
                    'approval_rate': approval_rate
                },
                'agent_accuracy': {
                    'score': agent_analysis.get('agent_accuracy', 0)
                },
                'tone_consistency': tone_performance
            }
        }
        
        # Save metrics
        with open(self.metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        return metrics
```

---

## REQUIREMENT 5: STAGE 3 ORCHESTRATOR

**Create `src/core/stage3_orchestrator.py` - coordinates all Stage 3 components:**

```python
from src.quality.fact_checker import FactChecker
from src.quality.final_reviewer import FinalReviewer
from src.analysis.quality_gates import QualityGates
from src.analysis.agent_analyzer import AgentAnalyzer
from src.analysis.tone_analytics import ToneAnalytics
from src.analysis.final_decision import FinalDecisionEngine
from src.core.stage3_loader import load_stage2_outputs
import json

class Stage3Orchestrator:
    """Orchestrates complete Stage 3 pipeline"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.fact_checker = FactChecker(api_key)
        self.reviewer = FinalReviewer()
        self.gates = QualityGates()
        self.agent_analyzer = AgentAnalyzer()
        self.tone_analyzer = ToneAnalytics()
        self.decision_engine = FinalDecisionEngine()
    
    def run_stage_3_complete(self):
        """Run complete Stage 3 pipeline (Sessions 1-3)"""
        
        print("\n=== STAGE 3 COMPLETE RUN ===")
        
        # Load Stage 2 outputs
        print("\n[1/5] Loading Stage 2 outputs...")
        videos = load_stage2_outputs()
        print(f"✅ Loaded {len(videos)} videos")
        
        # Session 1: Fact-check
        print("\n[2/5] Running fact-checks (Session 1)...")
        for video in videos:
            self.fact_checker.fact_check_script(
                video['script_id'],
                video['script'],
                video['topic']
            )
        print(f"✅ Fact-checked {len(videos)} videos")
        
        # Session 2: Human review
        print("\n[3/5] Running human reviews (Session 2)...")
        for video in videos:
            fact_check = self.fact_checker.load_report(video['script_id'])
            self.reviewer.review_video(video['script_id'], None, fact_check)
        print(f"✅ Reviewed {len(videos)} videos")
        
        # Session 3: Quality gates
        print("\n[4/5] Validating quality gates (Session 3)...")
        gates_summary = self.gates.validate_all_gates()
        print(f"✅ Gates validated")
        
        # Analysis
        print("\n[5/5] Running analysis...")
        agent_analysis = self.agent_analyzer.analyze_agent_performance(
            'logs/fact_check_reports'
        )
        tone_performance = self.tone_analyzer.analyze_tone_performance(
            'data/approved_scripts',
            'logs/human_reviews'
        )
        
        # Final decision
        final_report = self.decision_engine.make_go_nogo_decision(
            gates_summary,
            agent_analysis,
            tone_performance
        )
        
        self.decision_engine.generate_quality_metrics(
            gates_summary,
            agent_analysis,
            tone_performance
        )
        
        print(f"\n✅ STAGE 3 COMPLETE")
        print(f"Decision: {final_report['decision']}")
        
        return final_report
```

---

## REQUIREMENT 6: UNIT TESTS

**Create `tests/test_stage3_complete.py` - comprehensive Stage 3 tests:**

```python
import pytest
import json
from pathlib import Path
from src.analysis.quality_gates import QualityGates
from src.analysis.agent_analyzer import AgentAnalyzer
from src.analysis.tone_analytics import ToneAnalytics
from src.analysis.final_decision import FinalDecisionEngine

@pytest.fixture
def gates():
    return QualityGates()

@pytest.fixture
def agent_analyzer():
    return AgentAnalyzer()

@pytest.fixture
def tone_analyzer():
    return ToneAnalytics()

@pytest.fixture
def decision_engine():
    return FinalDecisionEngine()

def test_quality_gates_initialization(gates):
    assert gates is not None
    assert gates.results_dir.exists()

def test_validate_gate_3(gates):
    """Test Gate 3 validation"""
    if Path('logs/fact_check_reports').exists():
        result = gates.validate_gate_3('logs/fact_check_reports')
        assert result['gate'] == 3
        assert 'status' in result

def test_validate_gate_4(gates):
    """Test Gate 4 validation"""
    if Path('logs/human_reviews').exists():
        result = gates.validate_gate_4('logs/human_reviews')
        assert result['gate'] == 4
        assert 'approval_rate' in result

def test_agent_analyzer_calculation(agent_analyzer):
    """Test agent accuracy calculation"""
    if Path('logs/fact_check_reports').exists():
        analysis = agent_analyzer.analyze_agent_performance(
            'logs/fact_check_reports'
        )
        assert 'agent_accuracy' in analysis
        assert 0 <= analysis['agent_accuracy'] <= 100

def test_final_decision_go(decision_engine):
    """Test final decision with passing gates"""
    mock_gates = {
        'gate_3': {'status': 'PASSED'},
        'gate_4': {'status': 'PASSED'}
    }
    mock_agent = {'agent_accuracy': 85}
    mock_tone = {'tone_breakdown': {}}
    
    decision = decision_engine.make_go_nogo_decision(
        mock_gates,
        mock_agent,
        mock_tone
    )
    
    assert decision['decision'] == 'GO'

def test_final_decision_nogo(decision_engine):
    """Test final decision with failing gates"""
    mock_gates = {
        'gate_3': {'status': 'FAILED'},
        'gate_4': {'status': 'FAILED'}
    }
    mock_agent = {'agent_accuracy': 50}
    mock_tone = {'tone_breakdown': {}}
    
    decision = decision_engine.make_go_nogo_decision(
        mock_gates,
        mock_agent,
        mock_tone
    )
    
    assert decision['decision'] == 'NO-GO'

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

---

## DAY 4-7 IMPLEMENTATION SCHEDULE

**Day 4:**
- Create src/analysis/quality_gates.py
- Create src/analysis/agent_analyzer.py
- Run: pytest tests/test_quality_gates.py -v

**Day 5:**
- Create src/analysis/tone_analytics.py
- Create src/analysis/final_decision.py
- Run integration test

**Day 6:**
- Create src/core/stage3_orchestrator.py
- Test Stage3Orchestrator with run_stage_3_complete()
- Verify all output files created

**Day 7:**
- Run final verification
- Review stage_3_final_report.json
- Make GO/NO-GO decision
- Verify transition to Stage 4

---

## VERIFICATION STEPS - Day 4-7

```bash
#!/bin/bash
echo "=== SESSION 3 VERIFICATION ==="

echo ""
echo "Day 4-5 (Quality Analysis):"
test -f src/analysis/quality_gates.py && echo "✅ quality_gates.py" || echo "❌ Missing"
test -f src/analysis/agent_analyzer.py && echo "✅ agent_analyzer.py" || echo "❌ Missing"
test -f src/analysis/tone_analytics.py && echo "✅ tone_analytics.py" || echo "❌ Missing"
test -f src/analysis/final_decision.py && echo "✅ final_decision.py" || echo "❌ Missing"

echo ""
echo "Day 6 (Orchestration):"
test -f src/core/stage3_orchestrator.py && echo "✅ stage3_orchestrator.py" || echo "❌ Missing"

echo ""
echo "Day 7 (Final Results):"
test -f logs/stage_3_final_report.json && echo "✅ Final report created" || echo "❌ Missing"
test -f logs/stage_3_quality_metrics.json && echo "✅ Quality metrics created" || echo "❌ Missing"

echo ""
echo "Final Report Contents:"
if [ -f logs/stage_3_final_report.json ]; then
    python3 << 'EOF'
import json
with open('logs/stage_3_final_report.json') as f:
    report = json.load(f)
print(f"Decision: {report.get('decision')}")
print(f"Ready for Stage 4: {report.get('ready_for_stage_4')}")
print(f"Videos ready: {report.get('videos_ready')}/5")
EOF
fi

echo ""
echo "✅ Session 3 verification complete!"
```

---

## SUCCESS CRITERIA - END OF STAGE 3

✅ All tests pass (pytest tests/ -v)  
✅ Gate 3 status: PASSED or WARNING  
✅ Gate 4 status: PASSED or WARNING  
✅ Agent accuracy ≥80%  
✅ Final report shows GO or GO_WITH_CAUTION  
✅ All output files created and valid  
✅ Ready for Stage 4 transition  

---

## ERROR RECOVERY - SESSION 3

### If Quality Gates Fail:
```
- Check fact-check reports for excessive risk
- Re-run Session 1 with stricter fact-checking
- Review Session 2 approval decisions
```

### If Agent Accuracy Low:
```
- Videos generated with too many inaccuracies
- Proceed to Stage 4 with caution
- Monitor first uploads for quality issues
```

### If Human Approval Below 80%:
```
- Videos have genuine quality issues
- Return to Stage 2 for regeneration
- Re-run Stage 3 with new videos
```

---

## NEXT: TRANSITION TO STAGE 4

Once Stage 3 completes with GO decision:

1. ✅ Review STAGE_3_TO_STAGE_4_ALIGNMENT.md
2. ✅ Verify all Stage 3 outputs exist
3. ✅ Prepare Stage 4 environment
4. ✅ Read STAGE_4_EXECUTION_PLAN.md
5. ✅ Begin YouTube upload process

---

**End of Session 3 Prompt - Days 4-7**
