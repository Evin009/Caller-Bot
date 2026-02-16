"""Boolean checks using GPT-4 to answer yes/no questions."""
import json
import os
from typing import Dict, List, Optional
from openai import OpenAI

from .base import Check, CheckResult


class BooleanCheck(Check):
    """A check that uses GPT-4 to answer a yes/no question about the transcript."""
    
    def __init__(
        self,
        name: str,
        query: str,
        weight: float = 1.0,
        required: bool = False,
        model: str = "gpt-4-turbo"
    ):
        super().__init__(name, "boolean", weight, required)
        self.query = query
        self.model = model
        self._client = None
    
    @property
    def client(self):
        """Lazy initialization of OpenAI client."""
        if self._client is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            self._client = OpenAI(api_key=api_key)
        return self._client
    
    def evaluate(self, transcript: List[Dict]) -> CheckResult:
        """Evaluate boolean check using GPT-4."""
        transcript_text = self._get_transcript_text(transcript)
        
        system_prompt = """You are a QA evaluator analyzing a conversation transcript.
Your task is to answer a yes/no question about the conversation.
Respond with ONLY a JSON object in this exact format:
{
  "answer": "yes" or "no",
  "confidence": float between 0.0 and 1.0,
  "evidence": "Brief explanation of why you answered this way, citing specific parts of the transcript"
}"""
        
        user_prompt = f"""Question: {self.query}

Transcript:
{transcript_text}

Answer the question with yes or no and provide evidence."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            answer = result.get("answer", "no").lower().strip()
            confidence = result.get("confidence", 0.5)
            evidence = result.get("evidence", "")
            
            passed = answer == "yes"
            # Calculate score based on confidence if passed, 0 if failed
            score = self.weight * confidence if passed else 0.0
            
            return CheckResult(
                name=self.name,
                passed=passed,
                score=score,
                weight=self.weight,
                evidence=evidence
            )
            
        except Exception as e:
            # Return failed result on error
            return CheckResult(
                name=self.name,
                passed=False,
                score=0.0,
                weight=self.weight,
                evidence=f"Error during evaluation: {str(e)}"
            )
    
    @classmethod
    def from_config(cls, config: Dict) -> "BooleanCheck":
        """Create from configuration dictionary."""
        return cls(
            name=config["name"],
            query=config["query"],
            weight=config.get("weight", 1.0),
            required=config.get("required", False),
            model=config.get("model", "gpt-4-turbo")
        )
