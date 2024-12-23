from flask import Flask
from models import db, Image

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///images.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    # Update all image paths to include 'static/'
    images = Image.query.all()
    for img in images:
        if not img.path.startswith('static/'):
            print(f"Updating path for image {img.id} from {img.path} to static/{img.path}")
            img.path = f"static/{img.path}"
    
    db.session.commit()
    
    # Verify the changes
    print("\nVerifying updated paths:")
    for img in Image.query.all():
        print(f"ID: {img.id}, Path: {img.path}")
