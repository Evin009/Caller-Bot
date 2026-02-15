# Web Dashboard

## Problem
Currently, the AI Patient Stress Tester runs as a CLI tool. Results are stored as JSON files and users must inspect the file system or console logs to understand test outcomes. There is no easy way to visualize trends or replay calls without manual file navigation.

## Proposed Solution
Build a lightweight web interface to visualize test results, listen to call recordings, and trigger new tests.

### Key Features
- **Test History View**: List all past test runs with pass/fail status, duration, and quality score.
- **Call Detail View**: drill down into a specific call to see the full transcript, listen to the audio recording, and view detected bugs.
- **Run New Test**: Form to configure and launch a new test (select scenario, number of calls) directly from the browser.
- **Metrics Dashboard**: Graphs showing success rate over time, average quality score, and most common issues.

### Implementation Details
- **Backend**: Extend the existing FastAPI server (`verify_server.py`) or create a new `dashboard.py` using FastAPI/Flask.
- **Frontend**: Simple HTML/JS/CSS or a framework like React/Vue.
- **API Endpoints**:
    - `GET /api/reports`: List all reports.
    - `GET /api/reports/{id}`: Get details for a specific report.
    - `POST /api/test/start`: Trigger a new test run.
    - `GET /api/stats`: Get aggregate statistics.

### Benefits
- Makes the tool accessible to non-technical users (e.g., QA analysts, product managers).
- Centralizes test results and artifacts.
- Improves analysis workflow.
