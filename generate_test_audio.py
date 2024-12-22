import requests
import os
import numpy as np
from scipy import signal
import soundfile as sf
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
API_KEY = os.getenv('ELEVEN_API_KEY')
if not API_KEY:
    raise ValueError("ELEVEN_API_KEY environment variable is not set")

VOICE_ID = "RmgEBrAzINOXbTurITE5"  # Mary's voice ID

def clean_audio(input_file, output_file):
    print("Cleaning audio...")
    
    # Read the audio file
    data, samplerate = sf.read(input_file)
    
    # Convert to mono if stereo
    if len(data.shape) > 1:
        data = data.mean(axis=1)
    
    # Normalize audio (preserving dynamics)
    data = data / (np.max(np.abs(data)) + 1e-6)
    
    # Apply a gentle noise gate
    noise_threshold = 0.01
    data[np.abs(data) < noise_threshold] = 0
    
    # Design a bandpass filter focused on voice frequencies (300-3400 Hz)
    nyquist = samplerate // 2
    low = 300 / nyquist
    high = 3400 / nyquist
    
    # Use a lower order filter for gentler processing
    b, a = signal.butter(2, [low, high], btype='band')
    filtered_data = signal.filtfilt(b, a, data)
    
    # Blend the filtered audio with the original to preserve some natural qualities
    blend_ratio = 0.7  # 70% filtered, 30% original
    enhanced = blend_ratio * filtered_data + (1 - blend_ratio) * data
    
    # Final normalization to prevent clipping
    max_amplitude = np.max(np.abs(enhanced))
    if max_amplitude > 1.0:
        enhanced = enhanced / (max_amplitude + 1e-6)
    
    # Add a small amount of headroom
    enhanced *= 0.9
    
    # Save the enhanced audio
    sf.write(output_file, enhanced, samplerate, format='mp3')
    print(f"Enhanced audio saved as '{output_file}'")

def generate_audio(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": API_KEY
    }
    
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.8,  # Increased stability
            "similarity_boost": 0.6  # Slightly reduced to minimize artifacts
        }
    }
    
    print("Generating audio...")
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        # Save the raw audio file
        raw_file = "raw_audio.mp3"
        with open(raw_file, "wb") as f:
            f.write(response.content)
        print("Raw audio saved")
        
        # Clean and enhance the audio
        clean_audio(raw_file, "enhanced_audio.mp3")
        
        # Keep the raw file for comparison
        print("Both raw and enhanced files have been saved for comparison")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    # Test message
    test_text = "Hi, this is a test message to check how the voice sounds. I hope you like it!"
    generate_audio(test_text)
