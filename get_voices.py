import requests
import json
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = 'https://mercury.dev.dream-ai.com/api'

# Get API key from environment
API_KEY = os.getenv('HEDRA_API_KEY')
if not API_KEY:
    raise ValueError("HEDRA_API_KEY environment variable is not set")

headers = {'X-API-KEY': API_KEY}

def get_voices():
    response = requests.get(
        f"{BASE_URL}/v1/voices",
        headers=headers
    )
    return response.json()

def write_voices_to_file(voices):
    with open('voices.txt', 'w') as f:
        f.write("Available Hedra Voices:\n\n")
        for voice in voices['supported_voices']:
            f.write(f"Name: {voice['name']}\n")
            f.write(f"Voice ID: {voice['voice_id']}\n")
            f.write(f"Service: {voice['service']}\n")
            f.write(f"Premium: {voice['premium']}\n")
            
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
        voices = get_voices()
        write_voices_to_file(voices)
        print("Voice information has been saved to voices.txt")
    except Exception as e:
        print(f"Error: {e}")
