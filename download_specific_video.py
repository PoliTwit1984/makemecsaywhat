import os
import requests
from dotenv import load_dotenv
from flask import Flask
from models import db, MECVideoGeneration

# Load environment variables
load_dotenv()

HEDRA_API_KEY = os.getenv('HEDRA_API_KEY')
HEDRA_BASE_URL = 'https://mercury.dev.dream-ai.com/api'
GENERATED_VIDEOS_DIR = 'static/generated_videos'

# Initialize Flask app for database context
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///images.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def download_video(job_id):
    """Download a specific video by job_id"""
    try:
        # Ensure directory exists
        os.makedirs(GENERATED_VIDEOS_DIR, exist_ok=True)

        # Get video details from Hedra
        response = requests.get(
            f"{HEDRA_BASE_URL}/v1/projects/{job_id}",
            headers={'X-API-KEY': HEDRA_API_KEY}
        )
        response.raise_for_status()
        data = response.json()

        if data['status'] != 'Completed':
            print(f"Video {job_id} is not completed. Status: {data['status']}")
            return False

        # Ensure video is shared
        share_response = requests.post(
            f"{HEDRA_BASE_URL}/v1/projects/{job_id}/sharing?shared=true",
            headers={'X-API-KEY': HEDRA_API_KEY}
        )
        share_response.raise_for_status()

        # Get video URL
        video_url = data.get('videoUrl')
        if not video_url:
            print(f"No video URL found for {job_id}")
            return False

        # Download video
        print(f"Downloading video from {video_url}")
        video_response = requests.get(video_url, stream=True)
        video_response.raise_for_status()

        # Save video locally
        local_path = f"generated_videos/mec_video_{job_id}.mp4"
        full_path = os.path.join('static', local_path)
        
        with open(full_path, 'wb') as f:
            for chunk in video_response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        # Update database
        with app.app_context():
            video = MECVideoGeneration.query.filter_by(job_id=job_id).first()
            if video:
                video.local_video_path = local_path
                db.session.commit()
                print(f"Updated database for video {job_id}")
            else:
                print(f"No database record found for video {job_id}")

        print(f"Successfully downloaded video to {full_path}")
        return True

    except Exception as e:
        print(f"Error downloading video: {str(e)}")
        return False

if __name__ == "__main__":
    # Extract job_id from URL
    job_id = "f120ff53-efbb-46c5-bd55-ce5072ef7094"
    success = download_video(job_id)
    print("Download successful" if success else "Download failed")
