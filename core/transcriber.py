from openai import OpenAI
import os

class Transcriber:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found.")
        self.client = OpenAI(api_key=self.api_key)

    def transcribe(self, audio_file_path: str):
        """
        Transcribes the audio file using OpenAI Whisper.
        """
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            return transcript.text
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return None
