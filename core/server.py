from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pyngrok import ngrok
import uvicorn
import os
import logging
from .voice_bot import VoiceBot
from .transcriber import Transcriber
from .synthesizer import Synthesizer
from .audio_manager import AudioManager
from logic.scenario_engine import ScenarioEngine
from twilio.twiml.voice_response import VoiceResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Mount static directory to serve generated audio files
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global state to store conversation engines per Call SID
call_sessions = {}

# Initialize components
bot = VoiceBot()
transcriber = Transcriber()
synthesizer = Synthesizer()
audio_manager = AudioManager(
    base_dir="recordings",
    twilio_account_sid=os.getenv("TWILIO_ACCOUNT_SID"),
    twilio_auth_token=os.getenv("TWILIO_AUTH_TOKEN")
)

# Public URL (updated when ngrok starts)
BASE_URL = ""

class CallRequest(BaseModel):
    to_number: str
    scenario: str = "scheduling"

@app.post("/call")
async def trigger_call(request: CallRequest):
    """
    Trigger an outbound call to the specified number.
    """
    if not BASE_URL:
        return {"error": "Server not public yet. Wait for ngrok."}
    
    # We use /voice as the webhook for the call
    callback_url = f"{BASE_URL}/voice?scenario={request.scenario}"
    
    call_sid = bot.start_call(request.to_number, callback_url)
    
    if call_sid:
        return {"status": "initiated", "call_sid": call_sid}
    else:
        return {"status": "failed", "error": "Could not initiate call"}

@app.post("/voice")
async def voice_webhook(request: Request):
    """
    Handle incoming Twilio voice webhook (Start of call).
    """
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    scenario_param = request.query_params.get("scenario", "scheduling")
    
    logger.info(f"New call started: {call_sid} with scenario {scenario_param}")
    
    # Initialize new scenario engine for this call
    engine = ScenarioEngine(scenario_name=scenario_param)
    call_sessions[call_sid] = engine
    
    # Get opening line
    opening_text = engine.get_first_message()
    logger.info(f"Bot says: {opening_text}")
    
    return generate_response_twiml(call_sid, opening_text, engine.turn_count)

@app.post("/record")
async def record_webhook(request: Request):
    """
    Handle recording callback.
    """
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    recording_url = form_data.get("RecordingUrl")
    
    logger.info(f"Recording received for {call_sid}: {recording_url}")
    
    engine = call_sessions.get(call_sid)
    if not engine:
        logger.error("Error: No session found for this call.")
        return Response(content=str(VoiceResponse().hangup()), media_type="application/xml")

    # 1. Download recording
    audio_filename = f"{call_sid}_{engine.turn_count}_user.wav"
    local_audio_path = audio_manager.download_audio(recording_url, audio_filename)
    
    if not local_audio_path:
        logger.error("Failed to download audio")
        # In case of error, maybe ask again? Or hangup? 
        # For now, let's hangup to be safe or maybe a generic error message
        return Response(content=str(VoiceResponse().hangup()), media_type="application/xml")

    # 2. Transcribe
    transcript_text = transcriber.transcribe(local_audio_path)
    logger.info(f"User said: {transcript_text}")
    
    if not transcript_text:
        # Fallback if transcription fails
        transcript_text = "..."
    
    # 3. Generate response
    bot_response_text = engine.generate_response(transcript_text)
    logger.info(f"Bot says: {bot_response_text}")
    
    # 4. Check if conversation is over
    if engine.is_conversation_over():
        # Say goodbye and hang up
        response = generate_response_twiml(call_sid, bot_response_text, engine.turn_count, hangup=True)
        
        # Save transcript
        audio_manager.save_transcript(call_sid, engine.get_transcript())
        
        # Clean up session
        del call_sessions[call_sid]
        return response
    else:
        # Continue conversation
        return generate_response_twiml(call_sid, bot_response_text, engine.turn_count)

def generate_response_twiml(call_sid, text, turn_count, hangup=False):
    """
    Helper to generate TwiML with synthesized speech.
    """
    filename = f"{call_sid}_{turn_count}_bot.mp3"
    audio_path = f"static/{filename}"
    synthesizer.synthesize(text, audio_path)
    audio_url = f"{BASE_URL}/static/{filename}"
    
    response = VoiceResponse()
    response.play(audio_url)
    
    if hangup:
        response.hangup()
    else:
        # Record user response
        response.record(action=f"{BASE_URL}/record", method="POST", max_length=10, play_beep=True)
        
    return Response(content=str(response), media_type="application/xml")

def start_server(port: int = 8000):
    global BASE_URL
    # Start ngrok
    ngrok_token = os.getenv("NGROK_AUTHTOKEN")
    if ngrok_token:
        ngrok.set_auth_token(ngrok_token)
    
    try:
        # Check if we are already running in a way that ngrok is open (reloads)
        # But mostly we just open a new tunnel
        public_url = ngrok.connect(port).public_url
        BASE_URL = public_url
        print(f"Ngrok tunnel started: {BASE_URL}")
        
        # Start Uvicorn
        uvicorn.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    start_server()
