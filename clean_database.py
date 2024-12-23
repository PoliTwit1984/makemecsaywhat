from flask import Flask
from models import db, MECVideoGeneration

# Initialize Flask app for database context
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///images.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def clean_database():
    """Delete all videos except the specified one"""
    target_job_id = "f120ff53-efbb-46c5-bd55-ce5072ef7094"
    
    with app.app_context():
        # Delete all videos except the target
        deleted = MECVideoGeneration.query.filter(
            MECVideoGeneration.job_id != target_job_id
        ).delete()
        
        db.session.commit()
        print(f"Deleted {deleted} video entries")
        
        # Verify remaining video
        remaining = MECVideoGeneration.query.all()
        print(f"\nRemaining videos: {len(remaining)}")
        for video in remaining:
            print(f"- Video {video.job_id}")

if __name__ == "__main__":
    clean_database()
