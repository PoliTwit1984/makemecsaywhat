import requests
import os
from dotenv import load_dotenv
from celeryconfig import celery_app
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Load environment variables
load_dotenv()
HEDRA_API_KEY = os.getenv('HEDRA_API_KEY')
HEDRA_BASE_URL = 'https://mercury.dev.dream-ai.com/api'

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///images.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import and initialize models
from models import db, MECVideoGeneration
db.init_app(app)

@celery_app.task
def check_pending_videos():
    """
    Background task to check status of all pending videos
    """
    with app.app_context():
        print("Starting check_pending_videos task")
        # Get all pending video generations
        pending_videos = MECVideoGeneration.query.filter_by(status='pending').all()
        print(f"Found {len(pending_videos)} pending videos")
        
        for video in pending_videos:
            try:
                print(f"Checking status for video {video.job_id}")
                # Check video status with Hedra
                url = f"{HEDRA_BASE_URL}/v1/projects/{video.job_id}"
                print(f"Making request to: {url}")
                response = requests.get(
                    url,
                    headers={'X-API-KEY': HEDRA_API_KEY}
                )
                response.raise_for_status()
                data = response.json()
                print(f"Response data: {data}")
                
                # Map Hedra status to our status (Hedra uses capitalized status)
                status_mapping = {
                    'Completed': 'completed',
                    'Failed': 'failed',
                    'Processing': 'pending'
                }
                current_status = status_mapping.get(data['status'], 'pending')
                print(f"Mapped status: {current_status}")
                
                # Update status if changed
                if current_status != video.status:
                    print(f"Updating status from {video.status} to {current_status}")
                    video.status = current_status
                    if current_status == 'completed':
                        video.video_url = data.get('videoUrl')
                        print(f"Setting video URL: {data.get('videoUrl')}")
                    db.session.commit()
                    print("Database updated successfully")
                    
            except Exception as e:
                print(f"Error checking video {video.job_id}: {str(e)}")
                continue

# Note: Periodic schedule is defined in celeryconfig.py
