from flask import Flask
from models import db, MECVideoGeneration
import requests
import os
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///images.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def download_and_save_video(video_url, job_id):
    """
    Download video from Hedra and save it locally
    """
    try:
        # Create videos directory if it doesn't exist
        videos_dir = os.path.join('static', 'generated_videos')
        os.makedirs(videos_dir, exist_ok=True)

        # Generate unique filename
        filename = f"mec_video_{job_id}_{uuid.uuid4().hex[:8]}.mp4"
        filepath = os.path.join(videos_dir, filename)

        print(f"Downloading video from: {video_url}")
        print(f"Saving to: {filepath}")

        # Download video
        response = requests.get(video_url, stream=True)
        response.raise_for_status()

        # Save video to file
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        # Return relative path from static directory
        return os.path.join('generated_videos', filename)
    except Exception as e:
        print(f"Error downloading video: {str(e)}")
        return None

def test_download():
    with app.app_context():
        # Get a completed video
        video = MECVideoGeneration.query.filter_by(status='completed').first()
        if video:
            print(f"Found completed video with job_id: {video.job_id}")
            if video.video_url:
                local_path = download_and_save_video(video.video_url, video.job_id)
                if local_path:
                    print(f"Successfully downloaded video to {local_path}")
                    # Update database with local path
                    video.local_video_path = local_path
                    db.session.commit()
                    print("Database updated with local path")
            else:
                print("No video URL found")
        else:
            print("No completed videos found in database")

if __name__ == '__main__':
    test_download()
