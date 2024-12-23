from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    path = db.Column(db.String(200), nullable=False)

class TextGeneration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class MECVideoGeneration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    job_id = db.Column(db.String(100), nullable=False, unique=True)
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    video_url = db.Column(db.String(500), nullable=True)
    unique_token = db.Column(db.String(100), nullable=False, unique=True)
    share_url = db.Column(db.String(500), nullable=True)
    local_video_path = db.Column(db.String(500), nullable=True)  # Path to locally stored video file
    
    # Relationships
    image = db.relationship('Image', backref='video_generations')

    def get_share_url(self):
        """Get the Hedra share URL for this video"""
        if self.job_id:
            return f"https://www.hedra.com/app/characters/{self.job_id}/view"
        return None
