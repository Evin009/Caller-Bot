"""Check runner to execute all checks and generate evaluation reports."""
import json
import os
from typing import Dict, List, Optional
import yaml

from .checks.base import Check, CheckResult, EvaluationReport
from .checks.boolean import BooleanCheck
from .checks.threshold import ThresholdCheck
from .checks.content import ContentCheck


class CheckRunner:
    """Runs a set of checks against a transcript and generates evaluation reports."""
    
    # Registry of available check types
    CHECK_TYPES = {
        "boolean": BooleanCheck,
        "threshold": ThresholdCheck,
        "content": ContentCheck,
    }
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.checks: List[Check] = []
        self.pass_threshold = 80.0
        self.max_score = 100.0
        self.name = "Custom Evaluation"
        self.description = ""
        
        if config_path and os.path.exists(config_path):
            self.load_config(config_path)
    
    def load_config(self, config_path: str):
        """Load checks from YAML configuration file."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.name = config.get("name", "Custom Evaluation")
        self.description = config.get("description", "")
        
        scoring = config.get("scoring", {})
        self.pass_threshold = scoring.get("pass_threshold", 80.0)
        self.max_score = scoring.get("max_score", 100.0)
        
        # Create checks from config
        for check_config in config.get("checks", []):
            check = self._create_check(check_config)
            if check:
                self.checks.append(check)
    
    def _create_check(self, config: Dict) -> Optional[Check]:
        """Create a check instance from configuration."""
        check_type = config.get("type", "").lower()
        
        if check_type not in self.CHECK_TYPES:
            print(f"Warning: Unknown check type '{check_type}'")
            return None
        
        check_class = self.CHECK_TYPES[check_type]
        return check_class.from_config(config)
    
    def add_check(self, check: Check):
        """Add a check to the runner."""
        self.checks.append(check)
    
    def register_check_type(self, name: str, check_class):
        """Register a custom check type."""
        self.CHECK_TYPES[name] = check_class
    
    def evaluate(self, transcript: List[Dict]) -> EvaluationReport:
        """Run all checks against the transcript and generate a report."""
        if not self.checks:
            return EvaluationReport(
                overall_score=0.0,
                max_score=self.max_score,
                pass_threshold=self.pass_threshold,
                passed=False,
                summary="No checks configured"
            )
        
        check_results = []
        failures = []
        total_weight = sum(check.weight for check in self.checks)
        total_score = 0.0
        
        for check in self.checks:
            result = check.evaluate(transcript)
            check_results.append(result)
            
            # Calculate weighted score contribution
            if total_weight > 0:
                normalized_score = (result.score / check.weight) * (check.weight / total_weight) * self.max_score
                total_score += normalized_score
            
            # Track failures
            if not result.passed:
                if check.required:
                    failures.append(f"REQUIRED: {check.name} failed")
                else:
                    failures.append(f"{check.name} failed")
        
        # Determine overall pass/fail
        passed = total_score >= self.pass_threshold and not any(
            f.startswith("REQUIRED:") for f in failures
        )
        
        # Generate summary
        summary = self._generate_summary(check_results, total_score, passed)
        
        return EvaluationReport(
            overall_score=round(total_score, 2),
            max_score=self.max_score,
            pass_threshold=self.pass_threshold,
            passed=passed,
            check_results=check_results,
            failures=failures,
            summary=summary
        )
    
    def _generate_summary(
        self,
        results: List[CheckResult],
        total_score: float,
        passed: bool
    ) -> str:
        """Generate a summary of the evaluation."""
        passed_count = sum(1 for r in results if r.passed)
        total_count = len(results)
        
        status = "PASSED" if passed else "FAILED"
        summary = f"{self.name}: {status} ({passed_count}/{total_count} checks passed, score: {total_score:.1f}/{self.max_score})"
        
        return summary
    
    def get_available_check_types(self) -> List[str]:
        """Get list of available check types."""
        return list(self.CHECK_TYPES.keys())


def run_evaluation_from_config(
    transcript: List[Dict],
    config_path: str
) -> EvaluationReport:
    """Convenience function to run evaluation from a config file."""
    runner = CheckRunner(config_path)
    return runner.evaluate(transcript)


def run_evaluation_with_checks(
    transcript: List[Dict],
    checks: List[Check],
    pass_threshold: float = 80.0,
    max_score: float = 100.0
) -> EvaluationReport:
    """Convenience function to run evaluation with a list of checks."""
    runner = CheckRunner()
    runner.pass_threshold = pass_threshold
    runner.max_score = max_score
    
    for check in checks:
        runner.add_check(check)
    
    return runner.evaluate(transcript)
