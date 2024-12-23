from flask import Flask
from models import db, MECVideoGeneration

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///images.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    videos = MECVideoGeneration.query.all()
    print(f"\nFound {len(videos)} videos in database:")
    for video in videos:
        print(f"\nVideo ID: {video.id}")
        print(f"Image ID: {video.image_id}")
        print(f"Text: {video.text}")
        print(f"Job ID: {video.job_id}")
        print(f"Status: {video.status}")
        print(f"Share URL: {video.share_url}")
        print("-" * 50)
