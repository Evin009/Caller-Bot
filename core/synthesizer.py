from openai import OpenAI
import os
import requests

class Synthesizer:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        
        if not self.openai_api_key and not self.elevenlabs_api_key:
            raise ValueError("Neither OPENAI_API_KEY nor ELEVENLABS_API_KEY found.")
            
        if self.openai_api_key:
            self.client = OpenAI(api_key=self.openai_api_key)

    def synthesize(self, text: str, output_path: str):
        """
        Converts text to speech using ElevenLabs (preferred) or OpenAI TTS.
        """
        if self.elevenlabs_api_key:
            return self.synthesize_elevenlabs(text, output_path)
        else:
            return self.synthesize_openai(text, output_path)

    def synthesize_openai(self, text: str, output_path: str):
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text
            )
            response.stream_to_file(output_path)
            return output_path
        except Exception as e:
            print(f"Error synthesizing speech (OpenAI): {e}")
            return None

    def synthesize_elevenlabs(self, text: str, output_path: str):
        try:
            # Using a default voice ID (e.g., "Rachel" - 21m00Tcm4TlvDq8ikWAM)
            # You can change this to any voice ID from your library
            voice_id = "21m00Tcm4TlvDq8ikWAM" 
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return output_path
            else:
                print(f"ElevenLabs Error: {response.text}")
                # Fallback to OpenAI if possible
                if self.openai_api_key:
                    print("Falling back to OpenAI TTS...")
                    return self.synthesize_openai(text, output_path)
                return None
        except Exception as e:
            print(f"Error synthesizing speech (ElevenLabs): {e}")
            return None
