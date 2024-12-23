import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

HEDRA_API_KEY = os.getenv('HEDRA_API_KEY')
HEDRA_BASE_URL = 'https://mercury.dev.dream-ai.com/api'

# Get one of our completed video job IDs from the database
from flask import Flask
from models import db, MECVideoGeneration

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///images.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    # Check specific video
    job_id = "97549171-dd6e-4d57-9ebc-94e05f52eaa6"
    video = MECVideoGeneration.query.filter_by(job_id=job_id).first()
    if video:
        print(f"Checking video with job_id: {video.job_id}")
        
        # Make request to Hedra API
        response = requests.get(
            f"{HEDRA_BASE_URL}/v1/projects/{video.job_id}",
            headers={'X-API-KEY': HEDRA_API_KEY}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("\nHedra API Response:")
            print("-------------------")
            for key, value in data.items():
                print(f"{key}: {value}")
            
            print("\nLocal Database Status:")
            print("----------------------")
            print(f"Status: {video.status}")
            print(f"Local video path: {video.local_video_path}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    else:
        print("No completed videos found in database")
