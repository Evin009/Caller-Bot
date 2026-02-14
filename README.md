# AI Patient Stress Tester

Automated voice bot to stress-test AI agents.

## Setup

1.  **Clone the repository** (if you haven't already).
2.  **Create a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure Environment**:
    - Copy `.env.template` to `.env`:
        ```bash
        cp .env.template .env
        ```
    - Fill in your Twilio and OpenAI API keys in `.env`.

## Usage

```bash
python main.py --mode call --scenario scheduling
```
