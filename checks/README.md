# Custom Evaluation Checks

This directory contains YAML configuration files for custom evaluation checks.

## File Structure

Each YAML file defines a set of checks for a specific scenario or use case:

- `scheduling.yaml` - Checks for appointment scheduling calls
- `refill.yaml` - Checks for prescription refill calls
- `general.yaml` - General quality checks for all calls

## Usage

### Loading a Check Configuration

```python
from evaluation.check_runner import CheckRunner

# Load from YAML file
runner = CheckRunner("checks/scheduling.yaml")

# Run evaluation on a transcript
report = runner.evaluate(transcript)

# Check if passed
if report.passed:
    print("Call passed quality checks!")
else:
    print(f"Call failed: {report.failures}")

# Get detailed results
print(f"Score: {report.overall_score}/{report.max_score}")
for result in report.check_results:
    print(f"  {result.name}: {'✓' if result.passed else '✗'} ({result.score}/{result.weight})")
```

### Creating Custom Checks

You can create your own check configurations by following this structure:

```yaml
name: "My Custom Evaluation"
description: "Description of what this evaluates"

checks:
  - name: "Check Name"
    type: boolean|threshold|content
    # type-specific parameters
    weight: 10
    required: false

scoring:
  pass_threshold: 80
  max_score: 100
```

## Check Types

### Boolean Checks

Uses GPT-4 to answer yes/no questions about the transcript.

```yaml
- name: "Asked for DOB"
  type: boolean
  query: "Did the receptionist ask for the patient's date of birth?"
  required: true
  weight: 10
```

### Threshold Checks

Validates numeric metrics against thresholds.

```yaml
- name: "Response Count"
  type: threshold
  metric: "turn_count"  # or: response_count, avg_response_length
  max: 20
  weight: 5
```

Available metrics:
- `turn_count` - Total conversation turns
- `response_count` - Number of assistant responses
- `user_turn_count` - Number of user turns
- `assistant_turn_count` - Number of assistant turns
- `avg_response_length` - Average response length in characters

### Content Checks

Validates content based on phrases, regex, or semantic analysis.

**Phrase matching:**
```yaml
- name: "Politeness Check"
  type: content
  subtype: phrases
  required:
    - "please"
    - "thank you"
  prohibited:
    - "I don't know"
```

**Semantic analysis (uses GPT-4):**
```yaml
- name: "Professional Tone"
  type: content
  subtype: semantic
  query: "Did the receptionist maintain a professional tone?"
```

**Regex patterns:**
```yaml
- name: "Date Format Check"
  type: content
  subtype: regex
  required:
    - "\d{1,2}/\d{1,2}/\d{4}"
```

## Scoring

- Each check has a `weight` that contributes to the total score
- `required: true` means the check must pass for overall success
- `pass_threshold` is the minimum score (0-100) to pass overall
- Final score is calculated as weighted average of all checks
