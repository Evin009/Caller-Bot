import json
import os
from datetime import datetime

class Reporter:
    def __init__(self, report_dir="reports"):
        self.report_dir = report_dir
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)

    def save_report(self, analysis_result: dict):
        """
        Saves the analysis result to a JSON file.
        """
        if not analysis_result:
            return None
            
        call_id = analysis_result.get("call_id", "unknown")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.report_dir}/report_{call_id}_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(analysis_result, f, indent=2)
            
        print(f"Report saved to {filename}")
        return filename

    def generate_summary_stats(self):
        """
        Aggregates stats from all reports in the directory.
        """
        total_calls = 0
        successful_calls = 0
        total_score = 0
        issues_count = 0
        
        for filename in os.listdir(self.report_dir):
            if filename.endswith(".json"):
                with open(os.path.join(self.report_dir, filename), "r") as f:
                    data = json.load(f)
                    total_calls += 1
                    if data.get("success"):
                        successful_calls += 1
                    total_score += data.get("quality_score", 0)
                    issues_count += len(data.get("issues", []))
        
        avg_score = total_score / total_calls if total_calls > 0 else 0
        
        return {
            "total_calls": total_calls,
            "success_rate": successful_calls / total_calls if total_calls > 0 else 0,
            "average_quality_score": avg_score,
            "total_issues_found": issues_count
        }
