"""Base classes for custom evaluation checks."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CheckResult:
    """Result of a single check evaluation."""
    name: str
    passed: bool
    score: float
    weight: float
    evidence: Optional[str] = None
    actual: Optional[Any] = None
    threshold: Optional[Any] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        result = {
            "name": self.name,
            "passed": self.passed,
            "score": self.score,
            "weight": self.weight,
        }
        if self.evidence:
            result["evidence"] = self.evidence
        if self.actual is not None:
            result["actual"] = self.actual
        if self.threshold is not None:
            result["threshold"] = self.threshold
        return result


@dataclass
class EvaluationReport:
    """Complete evaluation report for a transcript."""
    overall_score: float
    max_score: float
    pass_threshold: float
    passed: bool
    check_results: List[CheckResult] = field(default_factory=list)
    failures: List[str] = field(default_factory=list)
    summary: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "overall_score": self.overall_score,
            "max_score": self.max_score,
            "pass_threshold": self.pass_threshold,
            "passed": self.passed,
            "checks": [r.to_dict() for r in self.check_results],
            "failures": self.failures,
            "summary": self.summary,
        }


class Check(ABC):
    """Abstract base class for all checks."""
    
    def __init__(self, name: str, check_type: str, weight: float = 1.0, required: bool = False):
        self.name = name
        self.check_type = check_type
        self.weight = weight
        self.required = required
    
    @abstractmethod
    def evaluate(self, transcript: List[Dict]) -> CheckResult:
        """Evaluate the check against the transcript.
        
        Args:
            transcript: List of conversation turns with 'role' and 'content' keys
            
        Returns:
            CheckResult with the evaluation outcome
        """
        pass
    
    @classmethod
    @abstractmethod
    def from_config(cls, config: Dict) -> "Check":
        """Create a check instance from configuration dictionary.
        
        Args:
            config: Dictionary containing check configuration
            
        Returns:
            Instantiated Check
        """
        pass
    
    def _get_transcript_text(self, transcript: List[Dict]) -> str:
        """Convert transcript to readable text format."""
        lines = []
        for turn in transcript:
            role = turn.get("role", "unknown")
            content = turn.get("content", "")
            if role != "system" and content:
                speaker = "Assistant" if role == "assistant" else "User"
                lines.append(f"{speaker}: {content}")
        return "\n".join(lines)
