from flask import Flask
from models import db, Image, MECVideoGeneration

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///images.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    # First, verify all images exist
    images = Image.query.all()
    print(f"\nFound {len(images)} images in database:")
    for img in images:
        print(f"ID: {img.id}, Path: {img.path}")

    # Then check videos and their image relationships
    videos = MECVideoGeneration.query.all()
    print(f"\nFound {len(videos)} videos in database:")
    for video in videos:
        print(f"\nVideo ID: {video.id}")
        print(f"Image ID: {video.image_id}")
        # Try to get the related image
        image = Image.query.get(video.image_id)
        if image:
            print(f"Image found: {image.path}")
        else:
            print(f"WARNING: No image found for image_id {video.image_id}")
            # Try to find a matching image by filename
            image = Image.query.filter_by(filename=f"mec{video.image_id}.jpg").first()
            if image:
                print(f"Found matching image, updating relationship...")
                video.image_id = image.id
                db.session.commit()
                print(f"Updated video {video.id} to use image {image.id}")
