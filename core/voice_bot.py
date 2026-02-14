import os
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from dotenv import load_dotenv

load_dotenv()

class VoiceBot:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        if not all([self.account_sid, self.auth_token, self.from_number]):
            raise ValueError("Twilio credentials not found in environment variables.")
            
        self.client = Client(self.account_sid, self.auth_token)

    def start_call(self, to_number: str, callback_url: str):
        """
        Initiates an outbound call to the target number.
        """
        try:
            call = self.client.calls.create(
                to=to_number,
                from_=self.from_number,
                url=callback_url,
                record=True,
                recording_channels='dual' # Record both sides
            )
            print(f"Call initiated. SID: {call.sid}")
            return call.sid
        except Exception as e:
            print(f"Error starting call: {e}")
            return None
