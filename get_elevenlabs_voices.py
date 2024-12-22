import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
API_KEY = os.getenv('ELEVEN_API_KEY')
if not API_KEY:
    raise ValueError("ELEVEN_API_KEY environment variable is not set")

HEADERS = {
    "Accept": "application/json",
    "xi-api-key": API_KEY
}

def write_voices_to_file():
    # Get all voices using the REST API
    response = requests.get(
        "https://api.elevenlabs.io/v1/voices",
        headers=HEADERS
    )
    
    if response.status_code != 200:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
    
    voices_data = response.json()
    
    with open('elevenlabs_voices.txt', 'w') as f:
        f.write("Available ElevenLabs Voices:\n\n")
        for voice in voices_data.get('voices', []):
            f.write(f"Name: {voice.get('name', 'N/A')}\n")
            f.write(f"Voice ID: {voice.get('voice_id', 'N/A')}\n")
            
            if 'category' in voice:
                f.write(f"Category: {voice['category']}\n")
            
            if voice.get('description'):
                f.write(f"Description: {voice['description']}\n")
            
            if voice.get('labels'):
                f.write("Labels:\n")
                for key, value in voice['labels'].items():
                    f.write(f"  - {key}: {value}\n")
            
            if voice.get('preview_url'):
                f.write(f"Preview URL: {voice['preview_url']}\n")
            
            f.write("\n" + "-"*50 + "\n\n")

if __name__ == "__main__":
    try:
        write_voices_to_file()
        print("ElevenLabs voice information has been saved to elevenlabs_voices.txt")
    except Exception as e:
        print(f"Error: {e}")
