import os
import sys
import requests
from pathlib import Path
import soundfile as sf
import numpy as np
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

def test_environment():
    print("Testing environment setup...")
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check required directories
    required_dirs = ['static', 'templates', 'static/mecimages']
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            print(f"❌ Missing directory: {dir_name}")
            return False
        print(f"✓ Found directory: {dir_name}")
    
    # Check required files
    required_files = [
        'app.py',
        'generate_test_audio.py',
        'requirements.txt',
        '.env.example',
        'static/style.css',
        'templates/index.html'
    ]
    for file_name in required_files:
        if not Path(file_name).exists():
            print(f"❌ Missing file: {file_name}")
            return False
        print(f"✓ Found file: {file_name}")
    
    return True

def test_api_keys():
    print("\nTesting API keys...")
    
    # Test ElevenLabs API
    eleven_key = os.getenv('ELEVEN_API_KEY', 'sk_fd0a98c9de02e55c97d250a2dba254f93a90768d25225b8c')
    response = requests.get(
        "https://api.elevenlabs.io/v1/voices",
        headers={"xi-api-key": eleven_key}
    )
    if response.status_code == 200:
        print("✓ ElevenLabs API key is valid")
    else:
        print(f"❌ ElevenLabs API key error: {response.status_code}")
        return False
    
    # Test Hedra API
    hedra_key = os.getenv('HEDRA_API_KEY', 'sk_hedra-W6DlNCZMSODqU-Mjj0V-u-QflWKOzCWi0IzGcBw1QFoqfDjr6RQQeGOVW2NnYa-P')
    response = requests.get(
        "https://mercury.dev.dream-ai.com/api/v1/voices",
        headers={"X-API-KEY": hedra_key}
    )
    if response.status_code == 200:
        print("✓ Hedra API key is valid")
    else:
        print(f"❌ Hedra API key error: {response.status_code}")
        return False
    
    return True

def test_database():
    print("\nTesting database setup...")
    
    try:
        # Initialize Flask app with test config
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///images.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db = SQLAlchemy(app)
        
        with app.app_context():
            # Try to query the database using SQLAlchemy text()
            from sqlalchemy import text
            result = db.session.execute(text('SELECT name FROM sqlite_master WHERE type="table"'))
            tables = [row[0] for row in result]
            
            required_tables = ['image', 'text_generation']
            for table in required_tables:
                if table not in tables:
                    print(f"❌ Missing table: {table}")
                    return False
                print(f"✓ Found table: {table}")
        
        return True
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
        return False

def test_audio_processing():
    print("\nTesting audio processing capabilities...")
    
    try:
        # Create a simple test signal
        sample_rate = 44100
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        test_signal = np.sin(2 * np.pi * 440 * t)  # 440 Hz sine wave
        
        # Try to save and load audio
        test_file = 'test_audio.wav'
        sf.write(test_file, test_signal, sample_rate)
        data, sr = sf.read(test_file)
        
        # Clean up
        os.remove(test_file)
        
        print("✓ Audio processing libraries are working")
        return True
    except Exception as e:
        print(f"❌ Audio processing error: {str(e)}")
        return False

def main():
    print("Running setup tests...\n")
    
    tests = [
        ("Environment", test_environment),
        ("API Keys", test_api_keys),
        ("Database", test_database),
        ("Audio Processing", test_audio_processing)
    ]
    
    all_passed = True
    for name, test_func in tests:
        print(f"{'='*20} Testing {name} {'='*20}")
        if not test_func():
            all_passed = False
            print(f"\n❌ {name} tests failed")
        else:
            print(f"\n✓ {name} tests passed")
        print()
    
    if all_passed:
        print("\n✨ All tests passed! The project is set up correctly.")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
