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

def run_evaluation_mode():
    print("Running evaluation on transcript files...")
    detector = BugDetector()
    reporter = Reporter()
    
    recordings_dir = "recordings"
    if not os.path.exists(recordings_dir):
        print(f"No recordings directory found at {recordings_dir}")
        return

    processed_count = 0
    for filename in os.listdir(recordings_dir):
        if filename.endswith("_transcript.json"):
            filepath = os.path.join(recordings_dir, filename)
            print(f"Analyzing {filename}...")
            
            with open(filepath, "r") as f:
                transcript = json.load(f)
            
            # Simple check to avoid re-analyzing based on filename existence in reports?
            # For now, just analyze everything.
            call_id = filename.split("_transcript")[0]
            
            result = detector.analyze_transcript(call_id, transcript)
            reporter.save_report(result)
            processed_count += 1
            
    print(f"Evaluation complete. Processed {processed_count} transcripts.")
    stats = reporter.generate_summary_stats()
    print("Summary Stats:", json.dumps(stats, indent=2))


def main():
    parser = argparse.ArgumentParser(description="AI Patient Stress Tester Bot")
    parser.add_argument("--mode", choices=["call", "evaluate"], default="call", help="Mode to run the bot in")
    parser.add_argument("--scenario", type=str, default="scheduling", help="Scenario to run (call mode)")
    parser.add_argument("--number", type=str, default=os.getenv("TARGET_PHONE_NUMBER"), help="Target phone number")
    args = parser.parse_args()

    if args.mode == "call":
        if not args.number:
            print("Error: Target number not provided in args or .env")
            return
        start_call_mode(args.scenario, args.number)
    elif args.mode == "evaluate":
        run_evaluation_mode()

if __name__ == "__main__":
    main()
