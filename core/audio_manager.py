import requests
import os

class AudioManager:
    def __init__(self, base_dir="recordings"):
        self.base_dir = base_dir
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def download_audio(self, url: str, filename: str):
        """
        Downloads audio from a URL and saves it to the base_dir.
        """
        try:
            response = requests.get(url)
            if response.status_code == 200:
                file_path = os.path.join(self.base_dir, filename)
                with open(file_path, "wb") as f:
                    f.write(response.content)
                return file_path
            else:
                print(f"Failed to download audio. Status: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error downloading audio: {e}")
            return None
            
    def get_public_url(self, filename: str, base_url: str):
        """
        Returns the public URL for a file served by our server.
        """
        return f"{base_url}/static/{filename}"

    def save_transcript(self, call_sid: str, history: list):
        """
        Saves the conversation transcript to a JSON file.
        """
        import json
        filename = f"{call_sid}_transcript.json"
        file_path = os.path.join(self.base_dir, filename)
        try:
            with open(file_path, "w") as f:
                json.dump(history, f, indent=2)
            return file_path
        except Exception as e:
            print(f"Error saving transcript: {e}")
            return None
