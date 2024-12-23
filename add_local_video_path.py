from flask import Flask
from models import db, MECVideoGeneration
import sqlalchemy as sa

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///images.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def add_column():
    with app.app_context():
        # Add local_video_path column if it doesn't exist
        inspector = sa.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('mec_video_generation')]
        
        if 'local_video_path' not in columns:
            print("Adding local_video_path column...")
            with db.engine.connect() as conn:
                conn.execute(sa.text(
                    'ALTER TABLE mec_video_generation ADD COLUMN local_video_path VARCHAR(500)'
                ))
                print("Column added successfully")
        else:
            print("local_video_path column already exists")

if __name__ == '__main__':
    add_column()
