# Enhanced Scenarios & Personas

## Problem
The current system has basic scenarios (Scheduling, Refill, Insurance). To thoroughly test an AI receptionist, we need a wider variety of patient behaviors and edge cases.

## Proposed Solution
Expand the library of scenarios and patient personas to cover more complex and challenging interactions.

### New Scenarios
1.  **Emergency / Urgent Care**: Patient has severe symptoms and needs immediate attention (testing if AI properly escalates/triages).
2.  **Language Barrier**: Patient speaks broken English or switches languages (testing AI's robustness).
3.  **Angry / Frustrated Patient**: Patient is upset about a bill or previous service (testing AI's empathy and de-escalation).
4.  **Bad Audio Quality**: Simulate background noise or poor connection (testing STT robustness).
5.  **Complex Medical History**: Patient provides a long, rambling history with irrelevant details (testing AI's ability to extract key info).
6.  **Privacy / HIPAA Baiting**: Patient asks for someone else's information (testing AI's security compliance).

### Implementation Details
- **Prompt Engineering**: Create new system prompts in `logic/prompts.py` for each persona.
- **Audio Modulation**: For "Bad Audio", post-process the TTS output with noise/distortion before sending to Twilio.
- **Scenario Config**: Allow defining scenarios via JSON/YAML files instead of hardcoding in Python, making it easier to add new ones.

### Benefits
- Increases test coverage significantly.
- Identifies weaknesses in AI understanding and policy compliance.
- Ensures the AI is robust against real-world variability.
