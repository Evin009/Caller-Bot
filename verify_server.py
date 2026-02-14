import sys
import os
import asyncio
from fastapi.testclient import TestClient
from ai_patient_tester.core.server import app

# Mock environment variables if needed
os.environ["OPENAI_API_KEY"] = "mock_key"
os.environ["TWILIO_ACCOUNT_SID"] = "mock_sid"
os.environ["TWILIO_AUTH_TOKEN"] = "mock_token"
os.environ["TWILIO_PHONE_NUMBER"] = "mock_number"

client = TestClient(app)

def test_voice_webhook():
    print("Testing POST /voice...")
    # Simulate a call start
    response = client.post(
        "/voice",
        data={"CallSid": "CA123456789"},
        params={"scenario": "scheduling"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if "<Play>" in response.text and "<Record>" in response.text:
        print("✅ TwiML contains Play and Record.")
    else:
        print("❌ TwiML Missing Play or Record.")

def test_record_webhook():
    print("\nTesting POST /record...")
    # Simulate a recording callback
    # We need to mock AudioManager and Transcriber to avoid real network calls
    # For now, we expect it to fail gracefully or we can mock them in the server module
    
    # Let's just run it to see if it crashes
    response = client.post(
        "/record",
        data={
            "CallSid": "CA123456789",
            "RecordingUrl": "http://example.com/rec.wav"
        }
    )
    print(f"Status: {response.status_code}")
    # It might fail because of real API calls, but we want to see if the code path works
    print(f"Response: {response.text}")

def test_call_trigger():
    print("\nTesting POST /call...")
    # This requires ngrok setup in the code, so it might return error
    response = client.post(
        "/call",
        json={"to_number": "+15551234567", "scenario": "refill"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    print("Starting visual verification...")
    try:
        test_voice_webhook()
        test_record_webhook()
        test_call_trigger()
    except Exception as e:
        print(f"Verification failed with error: {e}")
