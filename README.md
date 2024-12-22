# Make MEC Say What?

## Project Overview
This project creates a web application that allows users to select images and generate talking head videos using AI voice synthesis and lip-sync technology. The project combines ElevenLabs for voice generation and Hedra for video generation.

## Features

### 1. Web Interface
- Modern, minimalist, and energetic UI with responsive design
- Image selection with proper aspect ratio handling (16:9, 9:16, 1:1)
- Real-time audio preview before video generation
- Individual video pages with status tracking
- Static gallery of example videos
- Global navigation system

### 2. Voice Generation (ElevenLabs Integration)
- Successfully integrated with ElevenLabs API
- Using Mary voice (Voice ID: RmgEBrAzINOXbTurITE5)
- Implemented audio enhancement pipeline for better voice quality

#### Voice Generation Settings
```python
voice_settings = {
    "stability": 0.8,      # Higher stability for consistent output
    "similarity_boost": 0.6 # Balanced for natural sound while maintaining voice character
}
```

### 3. Video Generation (Hedra Integration)
- Using Hedra's character generation endpoint for lip-sync video creation
- Asynchronous video generation with status tracking
- Support for multiple aspect ratios (16:9, 9:16, 1:1)
- Individual video pages with auto-refresh
- Automatic video download on completion
- Instant video sharing via Hedra's viewer
- Real-time progress tracking through share URLs
- Videos shareable during generation and after completion

## Project Structure
```
/
├── app.py                    # Main Flask application
├── static/
│   ├── style.css            # CSS styles
│   ├── mecimages/           # Source images
│   ├── audio/               # Generated audio files
│   └── generated_videos/    # Generated video files
├── templates/
│   ├── index.html           # Main webpage template
│   ├── gallery.html         # Example videos gallery
│   ├── my_video.html        # Individual video page
│   ├── privacy.html         # Privacy policy page
│   └── responsible_ai.html  # AI documentation page
├── generate_test_audio.py    # Audio generation and enhancement script
├── get_elevenlabs_voices.py  # Script to list available voices
├── setup.sh                  # Environment setup script
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
└── instance/
    └── images.db            # SQLite database
```

## Database Schema
```sql
CREATE TABLE Image (
    id INTEGER PRIMARY KEY,
    filename VARCHAR(100) NOT NULL,
    path VARCHAR(200) NOT NULL
);

CREATE TABLE TextGeneration (
    id INTEGER PRIMARY KEY,
    image_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (image_id) REFERENCES Image(id)
);

CREATE TABLE MECVideoGeneration (
    id INTEGER PRIMARY KEY,
    image_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    job_id VARCHAR(100) NOT NULL UNIQUE,
    status VARCHAR(20) DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    video_url VARCHAR(500),
    unique_token VARCHAR(100) NOT NULL UNIQUE,
    share_url VARCHAR(500),
    FOREIGN KEY (image_id) REFERENCES Image(id)
);
```

## Quick Start

### Environment Setup
1. Install Redis (required for Celery):
   ```bash
   # macOS with Homebrew
   brew install redis
   brew services start redis
   
   # Ubuntu/Debian
   sudo apt-get install redis-server
   sudo systemctl start redis-server
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your API keys:
     ```
     ELEVEN_API_KEY=your_elevenlabs_api_key_here
     HEDRA_API_KEY=your_hedra_api_key_here
     ```

5. Initialize database:
   ```bash
   python app.py
   ```

6. Start the Celery worker (in a new terminal):
   ```bash
   celery -A celeryconfig worker --loglevel=info
   ```

7. Start the Celery beat scheduler (in another new terminal):
   ```bash
   celery -A celeryconfig beat --loglevel=info
   ```

8. Access the web interface:
   ```bash
   http://localhost:8000
   ```

### Architecture Overview

The application now uses a background worker architecture:

1. Web Application (Flask)
   - Handles user requests
   - Manages video generation requests
   - Shows real-time status updates

2. Background Worker (Celery)
   - Periodically checks video status
   - Updates database when videos complete
   - Runs independently of web interface

3. Message Broker (Redis)
   - Coordinates between web app and workers
   - Manages task queue and scheduling

4. Database (SQLite)
   - Stores video generation metadata
   - Tracks video status and URLs
   - Powers the gallery view

This architecture ensures:
- Reliable video status updates
- Gallery stays current
- System works even if users close their browsers

## Usage Flow

1. Create a Video:
   - Select an image from the grid
   - Enter the text you want MEC to say
   - Click "Generate MEC's Voice" to create audio
   - Preview the audio
   - Click "Create MEC Talking Video" to start video generation
   - Automatically redirected to your video's page

2. Video Generation:
   - Share URL available immediately
   - Watch progress directly on Hedra's viewer
   - Error handling and retries
   - Download video when complete
   - Progress tracking through Hedra's interface

## API Integration Details

### ElevenLabs API
- Base URL: https://api.elevenlabs.io/v1
- Key Endpoints:
  - `/text-to-speech/{voice_id}` - Generate speech
  - `/voices` - List available voices

### Hedra API
- Base URL: https://mercury.dev.dream-ai.com/api
- Key Endpoints:
  - `/v1/characters` - Generate talking head videos (with sharing enabled)
  - `/v1/projects/{job_id}` - Check video generation status
  - `/v1/audio` - Upload audio files
  - `/v1/portrait` - Upload portrait images
- Share URL Format: https://www.hedra.com/app/characters/{job_id}/view

## Dependencies
```
Flask
Flask-SQLAlchemy
requests
numpy
scipy
soundfile
python-dotenv
urllib3
```

## Admin Interface

### Setup
1. Configure admin password in `.env`:
   ```
   ADMIN_PASSWORD=your_admin_password_here
   ```

### Access
- Admin gallery URL: `http://127.0.0.1:8000/admin/gallery?password=your_admin_password`
- No visible login UI for regular users
- Password protected access

### Features
- View all generated videos
- Delete unwanted videos
- Instant UI updates after deletion
- Secure deletion with password verification

## Maintenance and Development

### Project Cleanup
To clean up generated files and reset the project state:

```bash
# Basic cleanup (removes generated files, cache, and database)
./cleanup.sh

# Full cleanup (also removes virtual environment)
./cleanup.sh --all
```

### Testing
Run the test suite to verify all components are working:
```bash
python test_setup.py
```

### Troubleshooting
If you encounter issues:
1. Check the Flask debug logs for detailed error messages
2. Verify API keys are correctly set in .env
3. Ensure all required directories exist
4. Check database connections and permissions
5. Verify network connectivity for API calls
