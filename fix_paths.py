from flask import Flask
from models import db, Image

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///images.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    # Remove 'static/' prefix from all image paths
    images = Image.query.all()
    for img in images:
        if img.path.startswith('static/'):
            print(f"Updating path for image {img.id} from {img.path} to {img.path[7:]}")  # Remove 'static/'
            img.path = img.path[7:]  # Remove 'static/' prefix
    
    db.session.commit()
    
    # Verify the changes
    print("\nVerifying updated paths:")
    for img in Image.query.all():
        print(f"ID: {img.id}, Path: {img.path}")
