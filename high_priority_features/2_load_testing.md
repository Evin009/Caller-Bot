# Load Testing & Concurrency

## Overview
Run multiple simultaneous calls to test the AI receptionist under stress.

## Core Features

### 1. Concurrent Call Orchestrator
- Launch N calls simultaneously
- Control max concurrency (10-100 calls)
- Pacing controls (calls per second)
- Queue management
- Automatic cleanup on failure

### 2. Scenario Distribution
- Assign different scenarios to calls
- Randomize patient personas
- A/B testing support
- Weighted distribution

### 3. Real-time Metrics
- Active calls counter
- Success/failure rate
- Average response time
- Error rate by type
- Resource utilization

### 4. Load Report
- Total calls made
- Success percentage
- Average duration
- Peak concurrent calls
- Failures breakdown
- Cost summary

## Technical Design
```python
class LoadTestOrchestrator:
    def __init__(self, max_concurrent=50):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.active_calls = []
        self.results = []
    
    async def run_load_test(
        self, 
        scenarios, 
        num_calls=100, 
        max_concurrent=20,
        pacing_calls_per_sec=5
    ):
        # Distribute calls across scenarios
        # Control concurrency with semaphore
        # Track metrics in real-time
        pass
```

## CLI Usage
```bash
# Run 50 calls, max 10 concurrent
python main.py --mode load --calls 50 --concurrent 10

# Run with specific scenarios
python main.py --mode load --scenarios scheduling,refill --calls 100

# Set pacing (1 call every 2 seconds)
python main.py --mode load --calls 20 --pacing 0.5
```

## Success Criteria
- Support 100 concurrent calls
- Configurable pacing (0.1-10 calls/sec)
- <5% failure rate at max load
- Real-time metrics update
- Generates load test report

## Files to Create/Modify
- Create `core/load_tester.py` - Orchestrator logic
- Create `core/metrics.py` - Metrics collection
- Modify `main.py` - Add load test CLI commands
- Modify `core/voice_bot.py` - Support batch operations

## Potential Issues
- Twilio rate limits (need backoff/retry)
- OpenAI token limits
- Memory usage with many concurrent calls
- Network bandwidth
