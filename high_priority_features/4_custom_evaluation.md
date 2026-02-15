# Custom Evaluation Framework

## Overview
Define your own quality metrics and pass/fail criteria for test calls.

## Core Features

### 1. Check Types

#### Boolean Checks (Pass/Fail)
- Did they ask for date of birth?
- Did they confirm the appointment?
- Did they mention insurance?
- Did they provide callback number?

#### Threshold Checks
- Response time < 5 seconds
- Conversation duration < 10 minutes
- Silence gaps < 3 seconds
- Number of turns < 20

#### Content Checks
- Required phrases mentioned
- Prohibited phrases not used
- Correct information provided
- Appropriate tone maintained

### 2. Check Configuration
```yaml
# checks/scheduling.yaml
name: "Scheduling Scenario Quality"
description: "Validates scheduling flow quality"

checks:
  - name: "Asked for DOB"
    type: boolean
    query: "Did the receptionist ask for the patient's date of birth?"
    required: true
    weight: 10

  - name: "Response Time"
    type: threshold
    metric: "avg_response_time_seconds"
    max: 5.0
    weight: 5

  - name: "Confirmed Details"
    type: boolean
    query: "Did the receptionist confirm the appointment details before ending?"
    required: true
    weight: 15

  - name: "No Hallucinations"
    type: boolean
    query: "Did the receptionist make up any false information?"
    required: false
    weight: 20

scoring:
  pass_threshold: 80
  max_score: 100
```

### 3. Automated Evaluation Pipeline
1. Run test call
2. Extract transcript
3. Run all checks via GPT-4
4. Calculate weighted score
5. Determine pass/fail
6. Generate detailed report

### 4. Check Results Report
```json
{
  "overall_score": 85,
  "passed": true,
  "checks": [
    {
      "name": "Asked for DOB",
      "passed": true,
      "score": 10,
      "evidence": "At 00:45, asked: 'Can you confirm your date of birth?'"
    },
    {
      "name": "Response Time",
      "passed": false,
      "score": 2.5,
      "actual": 8.5,
      "threshold": 5.0,
      "evidence": "Average response time was 8.5 seconds"
    }
  ],
  "failures": ["Response time exceeded threshold"]
}
```

## Check Implementation
```python
class Check:
    def evaluate(self, transcript: Transcript) -> CheckResult:
        pass

class BooleanCheck(Check):
    query: str
    required: bool
    
    def evaluate(self, transcript):
        # Use GPT-4 to answer yes/no question
        response = self.ask_gpt(self.query, transcript)
        passed = response == "yes"
        return CheckResult(passed=passed, ...)

class ThresholdCheck(Check):
    metric: str
    max: float
    
    def evaluate(self, transcript):
        value = self.calculate_metric(transcript)
        passed = value <= self.max
        return CheckResult(passed=passed, actual=value)
```

## Success Criteria
- Support 10+ different check types
- Configurable via YAML
- Accurate GPT-4 evaluation
- Clear pass/fail reporting
- Weighted scoring system
- Easy to add new checks

## Files to Create
- `evaluation/checks/` folder
- `evaluation/checks/base.py` - Base check classes
- `evaluation/checks/boolean.py` - Boolean checks
- `evaluation/checks/threshold.py` - Threshold checks
- `evaluation/checks/content.py` - Content checks
- `evaluation/check_runner.py` - Execute checks
- `checks/` - User-defined check YAML files

## Integration
- Extend `evaluation/bug_detector.py` to use new framework
- Modify `main.py` for custom evaluation commands
- Store check results in reports
