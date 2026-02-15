# AI Patient Stress Tester

A small toolset for automating voice-based stress tests of AI agents. The project provides scripts to simulate phone calls/interactions, run scenarios, and verify agent behavior.

Features
- Scenario-based voice call simulation
- Local verification server for testing
- Recordings and evaluation utilities included

Requirements
- Python 3.8+
- See requirements.txt for exact dependencies

Setup
1. Clone the repository (if you haven't already).
2. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configuration:
- If present, copy `.env.template` to `.env` and add your credentials (e.g., Twilio, OpenAI):

```bash
cp .env.template .env
```

Running the project
- Run a call scenario (example):

```bash
python main.py --mode call --scenario scheduling
```

- Start the local verification server:

```bash
python verify_server.py
```

Project layout
- main.py — entry point for running scenarios
- verify_server.py — simple HTTP server for verification
- core/ — core agent and call logic
- evaluation/ — evaluation tools and metrics
- logic/ — scenario/interaction definitions
- recordings/ — example audio recordings
- reports/ — generated evaluation reports

Contributing
- Open issues or PRs for improvements or bug fixes.

License
- MIT License (add license file if desired)

Contact
- Maintainer: project repository owner
