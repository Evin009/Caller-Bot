# Load Testing & Concurrency

## Problem
The current system executes one call at a time. This is sufficient for functional testing but does not verify if the AI Receptionist can handle multiple simultaneous calls (concurrency) or sustained load.

## Proposed Solution
Add support for running multiple test calls in parallel to stress-test the target system's capacity.

### Key Features
- **Concurrency Control**: user can specify the number of concurrent calls (e.g., `--concurrency 5`).
- **Ramp-up Strategy**: Option to ramp up load gradually (e.g., start with 1 call, increase by 1 every 30 seconds).
- **Aggregate Reporting**: combine results from all concurrent calls into a single load test report.
- **Failure Analysis**: Identify if failures correlate with higher load (e.g., higher latency, dropped calls).

### Implementation Details
- **Multi-threading/Asyncio**: Use Python's `asyncio` or `threading` to spawn multiple `verify_server` instances or manage multiple active calls within one server instance.
- **Twilio Integration**: Twilio can handle concurrent calls, but we need to ensure our local server (ngrok) and backend logic can process multiple simultaneous webhooks.
- **State Management**: Ensure `logic/scenario_engine.py` maintains separate state for each active call ID.

### Benefits
- Verifies system stability under load.
- Detects race conditions or bottlenecks in the target AI Receptionist.
- Provides a more realistic simulation of peak traffic.
