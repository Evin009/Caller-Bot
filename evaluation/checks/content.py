"""Content checks for phrase matching and validation."""
import json
import os
import re
from typing import Dict, List, Optional
from openai import OpenAI

from .base import Check, CheckResult


class ContentCheck(Check):
    """A check that validates content based on required/prohibited phrases or semantic content."""
    
    def __init__(
        self,
        name: str,
        check_subtype: str = "phrases",  # "phrases", "semantic", "regex"
        required_phrases: Optional[List[str]] = None,
        prohibited_phrases: Optional[List[str]] = None,
        query: Optional[str] = None,
        weight: float = 1.0,
        required: bool = False,
        model: str = "gpt-4-turbo"
    ):
        super().__init__(name, "content", weight, required)
        self.check_subtype = check_subtype
        self.required_phrases = required_phrases or []
        self.prohibited_phrases = prohibited_phrases or []
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
        """Evaluate content check."""
        if self.check_subtype == "phrases":
            return self._evaluate_phrases(transcript)
        elif self.check_subtype == "semantic":
            return self._evaluate_semantic(transcript)
        elif self.check_subtype == "regex":
            return self._evaluate_regex(transcript)
        else:
            return CheckResult(
                name=self.name,
                passed=False,
                score=0.0,
                weight=self.weight,
                evidence=f"Unknown check subtype: {self.check_subtype}"
            )
    
    def _evaluate_phrases(self, transcript: List[Dict]) -> CheckResult:
        """Check for required and prohibited phrases."""
        transcript_text = self._get_transcript_text(transcript).lower()
        
        missing_required = []
        found_prohibited = []
        
        # Check required phrases
        for phrase in self.required_phrases:
            if phrase.lower() not in transcript_text:
                missing_required.append(phrase)
        
        # Check prohibited phrases
        for phrase in self.prohibited_phrases:
            if phrase.lower() in transcript_text:
                found_prohibited.append(phrase)
        
        # Calculate score
        total_checks = len(self.required_phrases) + len(self.prohibited_phrases)
        if total_checks == 0:
            passed = True
            score = self.weight
        else:
            passed_checks = (len(self.required_phrases) - len(missing_required)) + \
                          (len(self.prohibited_phrases) - len(found_prohibited))
            score = self.weight * (passed_checks / total_checks)
            passed = len(missing_required) == 0 and len(found_prohibited) == 0
        
        # Build evidence
        evidence_parts = []
        if missing_required:
            evidence_parts.append(f"Missing required phrases: {', '.join(missing_required)}")
        if found_prohibited:
            evidence_parts.append(f"Found prohibited phrases: {', '.join(found_prohibited)}")
        if not evidence_parts:
            evidence_parts.append("All phrase checks passed")
        
        return CheckResult(
            name=self.name,
            passed=passed,
            score=score,
            weight=self.weight,
            evidence="; ".join(evidence_parts)
        )
    
    def _evaluate_semantic(self, transcript: List[Dict]) -> CheckResult:
        """Use GPT-4 for semantic content analysis."""
        if not self.query:
            return CheckResult(
                name=self.name,
                passed=False,
                score=0.0,
                weight=self.weight,
                evidence="No semantic query provided"
            )
        
        transcript_text = self._get_transcript_text(transcript)
        
        system_prompt = """You are a content analyzer evaluating a conversation transcript.
Analyze the content based on the user's query and respond with ONLY a JSON object:
{
  "passed": true/false,
  "confidence": float between 0.0 and 1.0,
  "evidence": "Explanation with specific examples from the transcript"
}"""
        
        user_prompt = f"""Query: {self.query}

Transcript:
{transcript_text}

Analyze and provide your assessment."""
        
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
            passed = result.get("passed", False)
            confidence = result.get("confidence", 0.5)
            evidence = result.get("evidence", "")
            
            score = self.weight * confidence if passed else 0.0
            
            return CheckResult(
                name=self.name,
                passed=passed,
                score=score,
                weight=self.weight,
                evidence=evidence
            )
            
        except Exception as e:
            return CheckResult(
                name=self.name,
                passed=False,
                score=0.0,
                weight=self.weight,
                evidence=f"Error during semantic evaluation: {str(e)}"
            )
    
    def _evaluate_regex(self, transcript: List[Dict]) -> CheckResult:
        """Check content using regex patterns."""
        transcript_text = self._get_transcript_text(transcript)
        
        evidence_parts = []
        total_patterns = 0
        matched_patterns = 0
        
        # Check required patterns
        if self.required_phrases:
            for pattern in self.required_phrases:
                total_patterns += 1
                try:
                    if re.search(pattern, transcript_text, re.IGNORECASE):
                        matched_patterns += 1
                    else:
                        evidence_parts.append(f"Pattern not found: {pattern}")
                except re.error as e:
                    evidence_parts.append(f"Invalid regex pattern '{pattern}': {e}")
        
        # Check prohibited patterns
        if self.prohibited_phrases:
            for pattern in self.prohibited_phrases:
                total_patterns += 1
                try:
                    if re.search(pattern, transcript_text, re.IGNORECASE):
                        evidence_parts.append(f"Prohibited pattern found: {pattern}")
                    else:
                        matched_patterns += 1
                except re.error as e:
                    evidence_parts.append(f"Invalid regex pattern '{pattern}': {e}")
        
        if total_patterns == 0:
            passed = True
            score = self.weight
        else:
            score = self.weight * (matched_patterns / total_patterns)
            passed = matched_patterns == total_patterns
        
        if not evidence_parts:
            evidence_parts.append("All regex patterns matched correctly")
        
        return CheckResult(
            name=self.name,
            passed=passed,
            score=score,
            weight=self.weight,
            evidence="; ".join(evidence_parts)
        )
    
    @classmethod
    def from_config(cls, config: Dict) -> "ContentCheck":
        """Create from configuration dictionary."""
        return cls(
            name=config["name"],
            check_subtype=config.get("subtype", "phrases"),
            required_phrases=config.get("required_phrases", config.get("required", [])),
            prohibited_phrases=config.get("prohibited_phrases", config.get("prohibited", [])),
            query=config.get("query"),
            weight=config.get("weight", 1.0),
            required=config.get("required", False),
            model=config.get("model", "gpt-4-turbo")
        )
