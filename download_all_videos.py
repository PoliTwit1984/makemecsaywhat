from flask import Flask
from models import db, MECVideoGeneration
import os
import requests
from tasks import download_and_save_video
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///images.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def download_missing_videos():
    """Download all completed videos that are missing locally"""
    with app.app_context():
        # Get all completed videos
        videos = MECVideoGeneration.query.filter_by(status='completed').all()
        print(f"Found {len(videos)} completed videos")
        
        for video in videos:
            # Check if video needs downloading
            needs_download = False
            if not video.local_video_path:
                print(f"\nVideo {video.job_id} has no local path")
                needs_download = True
            elif not os.path.exists(os.path.join('static', video.local_video_path)):
                print(f"\nVideo {video.job_id} file is missing from {video.local_video_path}")
                needs_download = True
                
            if needs_download:
                print(f"Attempting to download video {video.job_id}")
                
                # First ensure video is shared
                print("Ensuring video is shared...")
                share_response = requests.post(
                    f"https://mercury.dev.dream-ai.com/api/v1/projects/{video.job_id}/sharing?shared=true",
                    headers={'X-API-KEY': os.getenv('HEDRA_API_KEY')}
                )
                share_response.raise_for_status()
                
                # Get fresh video URL from API
                print("Getting fresh video URL from API...")
                api_response = requests.get(
                    f"https://mercury.dev.dream-ai.com/api/v1/projects/{video.job_id}",
                    headers={'X-API-KEY': os.getenv('HEDRA_API_KEY')}
                )
                api_response.raise_for_status()
                api_data = api_response.json()
                
                video_url = api_data.get('videoUrl')
                if video_url:
                    print(f"Got fresh video URL from API: {video_url}")
                    video.video_url = video_url  # Update stored URL
                    local_path = download_and_save_video(video_url, video.job_id)
                    if local_path:
                        video.local_video_path = local_path
                        db.session.commit()
                        print(f"Successfully downloaded to {local_path}")
                        continue
                
                print("Failed to get video URL from API")
            else:
                print(f"\nVideo {video.job_id} already downloaded at {video.local_video_path}")

if __name__ == '__main__':
    print("Starting video download process...")
    download_missing_videos()
    print("\nDownload process complete")
