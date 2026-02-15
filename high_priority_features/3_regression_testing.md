# Automated Regression Testing

## Overview
Schedule recurring test runs to detect when AI receptionist behavior degrades over time.

## Core Features

### 1. Scheduled Test Runs
- Daily/weekly automated execution
- Configurable schedule per scenario
- Baseline comparison
- Run on-demand
- Parallel execution

### 2. Baseline Management
- Save "golden" conversation transcripts
- Version baselines
- Compare new results to baseline
- Auto-update baseline option
- Baseline drift alerts

### 3. Regression Detection
- Automatic pass/fail determination
- Quality score thresholds
- New bugs detection
- Performance degradation alerts
- Missing features detection

### 4. Trend Analysis
- Quality score over time graph
- Bug count trends
- Response time trends
- Success rate history
- Cost per test trends

### 5. Alerting
- Email notifications on failure
- Slack webhook integration
- Severity-based routing
- Daily summary reports
- Failure investigation links

## Configuration Example
```yaml
# regression_config.yaml
schedule:
  daily: "0 2 * * *"  # 2 AM daily
  weekly: "0 0 * * 0" # Sunday midnight

scenarios:
  scheduling:
    runs_per_scenario: 5
    baseline_version: "v1.2"
    pass_threshold: 8.0  # Quality score
    
  refill:
    runs_per_scenario: 3
    baseline_version: "v1.2"
    pass_threshold: 8.5

alerts:
  slack_webhook: "https://hooks.slack.com/..."
  email: "team@example.com"
  on_failure: true
  on_regression: true
```

## How It Works
1. Schedule triggers at configured time
2. Run all scenarios multiple times
3. Compare results to baseline
4. Generate regression report
5. Send alerts if thresholds not met
6. Update trend graphs

## Regression Report Format
```json
{
  "timestamp": "2024-01-15T02:00:00Z",
  "summary": {
    "total_tests": 20,
    "passed": 18,
    "failed": 2,
    "regressions": 1
  },
  "regressions": [
    {
      "scenario": "scheduling",
      "baseline_score": 9.2,
      "current_score": 6.8,
      "change": -2.4,
      "issues": ["Missed insurance question"]
    }
  ],
  "trends": {
    "avg_score_7d": 8.5,
    "avg_score_30d": 8.7,
    "trend": "declining"
  }
}
```

## Success Criteria
- Runs automatically on schedule
- Detects regressions within 24 hours
- Clear pass/fail status per test
- Baseline versioning works
- Alerts sent on failure
- Trend graphs update automatically

## Files to Create
- `regression/` folder
- `regression/scheduler.py` - Cron-like scheduling
- `regression/baseline.py` - Baseline management
- `regression/reporter.py` - Regression reports
- `regression/alerts.py` - Notification system
- `config/regression.yaml` - Configuration

## Integration Points
- Extend `evaluation/reporter.py` for regression logic
- Modify `main.py` for CLI regression commands
- Store baselines in `baselines/` folder
