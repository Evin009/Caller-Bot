from openai import OpenAI
import os
import json

import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BUG_DETECTION_PROMPT = """
You are a QA engineer analyzing a transcript of a call between a patient (user) and an AI medical receptionist (assistant).
Your goal is to identify bugs, errors, or quality issues in the AI receptionist's behavior.

Analyze the transcript for the following issues:
1. Hallucinations (inventing facts not in the context).
2. Repetitiveness (repeating the same phrase unnaturally).
3. Failure to understand (asking for information already provided).
4. Long latency or silence (if indicated in text, though hard to tell from transcript alone).
5. Awkward phrasing or robotic tone.
6. Task completion failure (did not schedule, did not refill, etc.).

Output your analysis as a JSON object with the following structure:
{
  "call_id": "string",
  "success": boolean,
  "quality_score": integer (1-10),
  "issues": [
    {
      "type": "string (hallucination|logic_error|understanding|other)",
      "description": "string",
      "severity": "high|medium|low"
    }
  ],
  "summary": "string"
}
"""

class BugDetector:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)

    def analyze_transcript(self, call_id: str, transcript: list):
        """
        Analyzes the transcript using GPT-4.
        """
        if not transcript:
            logger.warning(f"Empty transcript for call {call_id}")
            return None

        messages = [
            {"role": "system", "content": BUG_DETECTION_PROMPT},
            {"role": "user", "content": f"Call ID: {call_id}\nTranscript: {json.dumps(transcript)}"}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo", # Use turbo for JSON mode reliability and speed
                messages=messages,
                response_format={"type": "json_object"}
            )
            result_json = response.choices[0].message.content
            return json.loads(result_json)
        except Exception as e:
            logger.error(f"Error analyzing transcript: {e}")
            return None

    def save_report(self, call_id: str, report: dict):
        """
        Saves the analysis report to a JSON file.
        """
        if not report:
            return
            
        filename = f"reports/{call_id}_report.json"
        if not os.path.exists("reports"):
            os.makedirs("reports")
            
        try:
            with open(filename, "w") as f:
                json.dump(report, f, indent=2)
            logger.info(f"Report saved to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error saving report: {e}")
            return None
