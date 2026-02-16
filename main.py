import argparse
import os
import threading
import time
import json
from dotenv import load_dotenv
from core.server import app, start_server
from core.voice_bot import VoiceBot
from evaluation.bug_detector import BugDetector
from evaluation.reporter import Reporter
from evaluation.check_runner import CheckRunner
from pyngrok import ngrok
import uvicorn

# Load environment variables
load_dotenv()

def run_server_thread(port):
    uvicorn.run(app, host="0.0.0.0", port=port)

def start_call_mode(scenario, target_number):
    port = int(os.getenv("PORT", 8000))
    
    # 1. Start Ngrok
    ngrok_token = os.getenv("NGROK_AUTHTOKEN")
    if ngrok_token:
        ngrok.set_auth_token(ngrok_token)
    public_url = ngrok.connect(port).public_url
    print(f"Ngrok tunnel running at: {public_url}")
    
    # Update server's base URL (hacky but works for simple script)
    from core import server
    server.BASE_URL = public_url
    
    # 2. Start Server in Thread
    server_thread = threading.Thread(target=run_server_thread, args=(port,), daemon=True)
    server_thread.start()
    print("Server started in background...")
    time.sleep(2) # Give it a sec
    
    # 3. Initiate Call
    bot = VoiceBot()
    # The first webhook for a call is usually just the URL
    # But we want to hit /voice
    webhook_url = f"{public_url}/voice"
    print(f"Initiating call to {target_number} with webhook {webhook_url}...")
    
    call_sid = bot.start_call(to_number=target_number, callback_url=webhook_url)
    
    if call_sid:
        print(f"Call {call_sid} initiated. Press Ctrl+C to stop server when call is done.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping server...")
    else:
        print("Failed to initiate call.")

def run_evaluation_mode(checks_config: str = None):
    print("Running evaluation on transcript files...")
    detector = BugDetector()
    reporter = Reporter()
    
    # Load custom evaluation if config provided
    custom_runner = None
    if checks_config and os.path.exists(checks_config):
        print(f"Loading custom evaluation from {checks_config}")
        detector.load_custom_evaluation(checks_config)
        custom_runner = CheckRunner(checks_config)
    
    recordings_dir = "recordings"
    if not os.path.exists(recordings_dir):
        print(f"No recordings directory found at {recordings_dir}")
        return

    processed_count = 0
    custom_eval_count = 0
    
    for filename in os.listdir(recordings_dir):
        if filename.endswith("_transcript.json"):
            filepath = os.path.join(recordings_dir, filename)
            print(f"Analyzing {filename}...")
            
            with open(filepath, "r") as f:
                transcript = json.load(f)
            
            call_id = filename.split("_transcript")[0]
            
            # Run standard bug detection
            result = detector.analyze_transcript(call_id, transcript)
            
            # Run custom evaluation if configured
            custom_report = None
            if detector.custom_evaluator:
                custom_report = detector.run_custom_evaluation(call_id, transcript)
                if custom_report:
                    custom_eval_count += 1
                    detector.save_custom_report(call_id, custom_report)
            
            reporter.save_report(result)
            processed_count += 1
            
    print(f"Evaluation complete. Processed {processed_count} transcripts.")
    if custom_eval_count > 0:
        print(f"Custom evaluation applied to {custom_eval_count} transcripts")
    stats = reporter.generate_summary_stats()
    print("Summary Stats:", json.dumps(stats, indent=2))


def run_custom_evaluation_mode(checks_config: str, transcript_file: str = None):
    """Run custom evaluation on specific transcript or all transcripts."""
    if not os.path.exists(checks_config):
        print(f"Error: Checks config not found: {checks_config}")
        return
    
    runner = CheckRunner(checks_config)
    print(f"Loaded {len(runner.checks)} checks from {checks_config}")
    print(f"Pass threshold: {runner.pass_threshold}%")
    
    if transcript_file:
        # Evaluate single transcript
        if not os.path.exists(transcript_file):
            print(f"Error: Transcript file not found: {transcript_file}")
            return
        
        with open(transcript_file, "r") as f:
            transcript = json.load(f)
        
        call_id = os.path.basename(transcript_file).replace("_transcript.json", "")
        report = runner.evaluate(transcript)
        
        print(f"\n{'='*60}")
        print(f"Evaluation Results for {call_id}")
        print(f"{'='*60}")
        print(f"Status: {'PASSED' if report.passed else 'FAILED'}")
        print(f"Score: {report.overall_score}/{report.max_score}")
        print(f"\nCheck Results:")
        for result in report.check_results:
            status = "✓" if result.passed else "✗"
            print(f"  {status} {result.name}: {result.score:.1f}/{result.weight}")
            if result.evidence:
                print(f"      Evidence: {result.evidence}")
        
        if report.failures:
            print(f"\nFailures:")
            for failure in report.failures:
                print(f"  - {failure}")
        
        # Save report
        if not os.path.exists("reports"):
            os.makedirs("reports")
        report_file = f"reports/{call_id}_custom_eval.json"
        with open(report_file, "w") as f:
            json.dump(report.to_dict(), f, indent=2)
        print(f"\nReport saved to {report_file}")
    else:
        # Evaluate all transcripts in recordings directory
        recordings_dir = "recordings"
        if not os.path.exists(recordings_dir):
            print(f"No recordings directory found at {recordings_dir}")
            return
        
        print(f"\nEvaluating all transcripts in {recordings_dir}...")
        processed = 0
        passed = 0
        
        for filename in os.listdir(recordings_dir):
            if filename.endswith("_transcript.json"):
                filepath = os.path.join(recordings_dir, filename)
                with open(filepath, "r") as f:
                    transcript = json.load(f)
                
                call_id = filename.replace("_transcript.json", "")
                report = runner.evaluate(transcript)
                
                status = "PASS" if report.passed else "FAIL"
                print(f"  {call_id}: {status} ({report.overall_score:.1f}%)")
                
                if report.passed:
                    passed += 1
                processed += 1
                
                # Save individual report
                if not os.path.exists("reports"):
                    os.makedirs("reports")
                report_file = f"reports/{call_id}_custom_eval.json"
                with open(report_file, "w") as f:
                    json.dump(report.to_dict(), f, indent=2)
        
        if processed > 0:
            pass_rate = (passed / processed) * 100
            print(f"\n{'='*60}")
            print(f"Summary: {passed}/{processed} passed ({pass_rate:.1f}%)")
            print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(description="AI Patient Stress Tester Bot")
    parser.add_argument("--mode", choices=["call", "evaluate", "custom-eval"], default="call",
                       help="Mode to run the bot in: call (make test calls), evaluate (bug detection), custom-eval (custom checks)")
    parser.add_argument("--scenario", type=str, default="scheduling", help="Scenario to run (call mode)")
    parser.add_argument("--number", type=str, default=os.getenv("TARGET_PHONE_NUMBER"), help="Target phone number")
    parser.add_argument("--checks", type=str, help="Path to custom checks YAML config (for evaluate/custom-eval modes)")
    parser.add_argument("--transcript", type=str, help="Specific transcript file to evaluate (custom-eval mode)")
    args = parser.parse_args()

    if args.mode == "call":
        if not args.number:
            print("Error: Target number not provided in args or .env")
            return
        start_call_mode(args.scenario, args.number)
    elif args.mode == "evaluate":
        run_evaluation_mode(args.checks)
    elif args.mode == "custom-eval":
        if not args.checks:
            print("Error: --checks argument required for custom-eval mode")
            print("Example: python main.py --mode custom-eval --checks checks/scheduling.yaml")
            return
        run_custom_evaluation_mode(args.checks, args.transcript)

if __name__ == "__main__":
    main()
