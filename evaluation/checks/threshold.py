"""Threshold checks for numeric metrics."""
import re
from typing import Dict, List, Optional, Any
from datetime import datetime

from .base import Check, CheckResult


class ThresholdCheck(Check):
    """A check that validates a numeric metric against a threshold."""
    
    METRIC_FUNCTIONS = {}
    
    def __init__(
        self,
        name: str,
        metric: str,
        threshold: float,
        comparison: str = "<=",
        weight: float = 1.0,
        required: bool = False
    ):
        super().__init__(name, "threshold", weight, required)
        self.metric = metric
        self.threshold = threshold
        self.comparison = comparison
    
    def evaluate(self, transcript: List[Dict]) -> CheckResult:
        """Evaluate threshold check."""
        # Calculate the metric value
        value = self._calculate_metric(transcript)
        
        # Compare based on operator
        passed = self._compare(value, self.threshold, self.comparison)
        
        # Calculate score proportionally if it's a "less than" check
        if self.comparison in ["<=", "<"]:
            if value <= self.threshold:
                score = self.weight
            else:
                # Partial credit if close to threshold
                ratio = self.threshold / value if value > 0 else 0
                score = self.weight * max(0, ratio)
        else:
            score = self.weight if passed else 0.0
        
        evidence = self._generate_evidence(value, passed)
        
        return CheckResult(
            name=self.name,
            passed=passed,
            score=score,
            weight=self.weight,
            evidence=evidence,
            actual=value,
            threshold=self.threshold
        )
    
    def _calculate_metric(self, transcript: List[Dict]) -> float:
        """Calculate the metric value from transcript."""
        if self.metric in self.METRIC_FUNCTIONS:
            return self.METRIC_FUNCTIONS[self.metric](transcript)
        
        # Default metric calculations
        metric_calculators = {
            "turn_count": self._calc_turn_count,
            "response_count": self._calc_response_count,
            "avg_response_length": self._calc_avg_response_length,
            "user_turn_count": self._calc_user_turn_count,
            "assistant_turn_count": self._calc_assistant_turn_count,
        }
        
        if self.metric in metric_calculators:
            return metric_calculators[self.metric](transcript)
        
        # Unknown metric
        return 0.0
    
    def _calc_turn_count(self, transcript: List[Dict]) -> int:
        """Count total non-system turns."""
        return sum(1 for t in transcript if t.get("role") != "system")
    
    def _calc_response_count(self, transcript: List[Dict]) -> int:
        """Count assistant responses."""
        return sum(1 for t in transcript if t.get("role") == "assistant")
    
    def _calc_user_turn_count(self, transcript: List[Dict]) -> int:
        """Count user turns."""
        return sum(1 for t in transcript if t.get("role") == "user")
    
    def _calc_assistant_turn_count(self, transcript: List[Dict]) -> int:
        """Count assistant turns."""
        return sum(1 for t in transcript if t.get("role") == "assistant")
    
    def _calc_avg_response_length(self, transcript: List[Dict]) -> float:
        """Calculate average response length."""
        assistant_turns = [t for t in transcript if t.get("role") == "assistant"]
        if not assistant_turns:
            return 0.0
        total_length = sum(len(t.get("content", "")) for t in assistant_turns)
        return total_length / len(assistant_turns)
    
    def _compare(self, value: float, threshold: float, operator: str) -> bool:
        """Compare value against threshold."""
        operators = {
            "<=": value <= threshold,
            "<": value < threshold,
            ">=": value >= threshold,
            ">": value > threshold,
            "==": value == threshold,
            "!=": value != threshold,
        }
        return operators.get(operator, False)
    
    def _generate_evidence(self, value: float, passed: bool) -> str:
        """Generate evidence string."""
        status = "passed" if passed else "failed"
        return f"Metric '{self.metric}' = {value:.2f} (threshold: {self.comparison} {self.threshold}) - {status}"
    
    @classmethod
    def from_config(cls, config: Dict) -> "ThresholdCheck":
        """Create from configuration dictionary."""
        return cls(
            name=config["name"],
            metric=config["metric"],
            threshold=config.get("max", config.get("threshold", 0)),
            comparison=config.get("comparison", "<="),
            weight=config.get("weight", 1.0),
            required=config.get("required", False)
        )
    
    @classmethod
    def register_metric(cls, name: str, func):
        """Register a custom metric calculation function."""
        cls.METRIC_FUNCTIONS[name] = func
