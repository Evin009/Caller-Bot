# System Architecture

## Overview
The AI Patient Stress Tester is a Python-based voice bot designed to call an AI medical receptionist, simulate various patient scenarios, and evaluate the AI's performance.

## Components

### 1. Telephony Layer (Twilio & FastAPI)
- **Twilio Voice API**: Handles the PSTN connection to the target phone number.
- **FastAPI Server**: Hosted locally and exposed via `ngrok`. Receives webhooks from Twilio to control the call flow using TwiML.
- **Workflow**: 
    1. Python script initiates outbound call via Twilio REST API.
    2. Twilio connects and requests TwiML from our `/voice` endpoint.
    3. Server responds with `<Play>` (TTS audio) and `<Record>` (capture user audio).
    4. When recording finishes, Twilio sends it to `/record` endpoint.
    5. Server processes audio and returns next TwiML.

### 2. Audio Processing
- **Speech-to-Text (STT)**: `core/transcriber.py` uses OpenAI **Whisper API**.
    - Downloads audio from Twilio.
    - Sends to Whisper for accurate transcription.
- **Text-to-Speech (TTS)**: `core/synthesizer.py` uses OpenAI **TTS API** (or ElevenLabs).
    - Converts LLM text response to `.mp3`.
    - Saves to `static/` directory to be served to Twilio.

### 3. Scenario Engine (Logic)
- **`logic/scenario_engine.py`**: Manages the conversation state.
- **GPT-4**: powered "Patient Persona". 
- **System Prompts**: Defined in `logic/prompts.py` (Scheduling, Refill, Insurance).
    - The LLM tracks the conversation history and generates context-aware responses.
    - Includes logic to detect when the conversation goal is met (or failed) to end the call.

### 4. Evaluation & Reporting
- **`evaluation/bug_detector.py`**: Post-call analysis.
    - Feeds the full conversation transcript (saved as JSON) to GPT-4.
    - Prompts GPT-4 to act as a QA Engineer detecting hallucinations, repetitions, or logic errors.
- **`evaluation/reporter.py`**: Saves the analysis as structured JSON reports and calculates aggregate stats.

## Data Flow diagram
```mermaid
sequenceDiagram
    participant Main as Python Script
    participant Twilio
    participant Server as FastAPI/Ngrok
    participant LLM as GPT-4/Whisper
    participant Target as AI Receptionist

    Main->>Twilio: Start Call (POST /Calls)
    Twilio->>Target: Ring...
    Target-->>Twilio: Answer
    Twilio->>Server: POST /voice
    Server->>LLM: Generate Opening Line
    LLM-->>Server: "Hello, I need an appointment"
    Server-->>Twilio: Play Audio, Then Record
    Twilio->>Target: "Hello, I need an appointment"
    Target-->>Twilio: "Sure, what is your name?"
    Twilio->>Server: POST /record (Audio URL)
    Server->>LLM: Transcribe Audio
    LLM-->>Server: "Sure, what is your name?"
    Server->>LLM: Generate Response
    LLM-->>Server: "My name is Alex."
    Server-->>Twilio: Play Audio, Then Record
    ...Conversation Loop...
```
