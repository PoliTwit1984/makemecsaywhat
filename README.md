# Make MEC Say What?

A web application that lets users create talking head videos using Hedra and ElevenLabs APIs.

## Recent Updates

### Video Storage and Processing Improvements
- Migrated from Celery to Azure Functions for video processing
- Added automatic video downloading via Azure Function (runs hourly)
- Improved video status tracking and user feedback
- Enhanced error handling and reliability

### New Features
- Added Privacy Policy page
- Added Responsible AI Usage Guidelines
- Improved error handling for video generation
- Added support for multiple aspect ratios (1:1, 16:9, 9:16)

### Technical Improvements
- Implemented Azure Function for reliable video downloading
- Removed Redis and Celery dependencies for simpler architecture
- Added detailed logging for video processing
- Fixed video sharing mechanism to ensure videos remain accessible

## Setup

1. Create a `.env` file with your API keys:
```
ELEVEN_API_KEY=your_elevenlabs_api_key
HEDRA_API_KEY=your_hedra_api_key
ADMIN_PASSWORD=your_admin_password
AZURE_STORAGE_CONNECTION_STRING=your_azure_storage_connection_string
```

2. Build and run with Docker:
```bash
docker compose up --build
```

3. Deploy Azure Function:
```bash
cd azure_function
func azure functionapp publish mec-video-downloader
```

See azure_function/README.md for detailed Azure Function setup instructions.

## Architecture

- Flask web application
- Azure Function for video processing (runs hourly)
- SQLite database for storing video metadata
- Local storage for completed videos

## API Integrations

- ElevenLabs for voice synthesis
- Hedra for video generation
- Azure Functions for video processing

## Directory Structure

- `/static/audio` - Generated audio files
- `/static/generated_videos` - Downloaded video files
- `/static/mecimages` - Source images
- `/templates` - HTML templates
- `/instance` - SQLite database
- `/azure_function` - Azure Function code and configuration

## Development

To run locally:
1. Create and activate a Python virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env`
4. Run Flask: `flask run --port 8000`

For Azure Function development:
1. Install Azure Functions Core Tools
2. Navigate to azure_function directory
3. Install dependencies: `pip install -r requirements.txt`
4. Run locally: `func start`

## Production

The application is containerized using Docker and includes:
- Gunicorn for serving the Flask application
- Azure Function for video processing
- Automatic directory creation
- Health checks
- Container resource limits

## Admin Features

Access the admin gallery at `/admin/gallery?password=your_admin_password` to:
- View all generated videos
- Delete videos
- Monitor video status

## Video Generation Flow

1. User selects image and enters text
2. Audio is generated using ElevenLabs
3. Image and audio are uploaded to Hedra
4. Video generation is initiated
5. Azure Function checks hourly for completed videos
6. Completed videos are downloaded and stored locally
7. Videos are served from local storage

## Error Handling

- Azure Function retries for failed operations
- Detailed error logging
- User-friendly error messages
- Status indicators for all processes

## Video Processing Mechanism

The application ensures reliable video processing through multiple steps:
1. After video creation, immediately shares using Hedra's `/projects/{id}/sharing` endpoint
2. Azure Function checks hourly for completed videos
3. When a video is completed, the Azure Function:
   - Downloads the video
   - Stores it locally
   - Updates the database with the local path
4. Videos are served from local storage to prevent access issues

## Future Improvements

- [ ] Add video cleanup for old/unused videos
- [ ] Implement user authentication
- [ ] Add video preview thumbnails
- [ ] Support custom image uploads
- [ ] Add batch video processing capabilities
