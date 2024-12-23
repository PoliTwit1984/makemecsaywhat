from flask import Flask
from models import db, Image

# Initialize Flask app for database context
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///images.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def fix_images():
    """Ensure all images are properly registered in the database"""
    with app.app_context():
        # First, clear existing images
        Image.query.delete()
        
        # Add all images
        image_files = [
            'mec.jpg', 'mec2.jpg', 'mec3.jpg', 'mec4.jpg',
            'mec5.jpg', 'mec6.jpeg', 'mec7.png'
        ]
        
        for img in image_files:
            image = Image(filename=img, path=f'mecimages/{img}')
            db.session.add(image)
            print(f"Added image: {img}")
        
        db.session.commit()
        
        # Verify images
        images = Image.query.all()
        print("\nVerifying images in database:")
        for img in images:
            print(f"- {img.filename}: {img.path}")

if __name__ == "__main__":
    fix_images()
