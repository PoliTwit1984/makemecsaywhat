from flask import Flask, render_template, request, jsonify, send_from_directory, url_for, session
from functools import wraps
from dotenv import load_dotenv
import os
import requests
import numpy as np
from scipy import signal
import soundfile as sf
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

# Get API keys and config from environment
ELEVEN_API_KEY = os.getenv('ELEVEN_API_KEY')
HEDRA_API_KEY = os.getenv('HEDRA_API_KEY')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

if not ELEVEN_API_KEY:
    raise ValueError("ELEVEN_API_KEY environment variable is not set")
if not HEDRA_API_KEY:
    raise ValueError("HEDRA_API_KEY environment variable is not set")
if not ADMIN_PASSWORD:
    raise ValueError("ADMIN_PASSWORD environment variable is not set")

# API endpoints
HEDRA_BASE_URL = 'https://mercury.dev.dream-ai.com/api'
GENERATED_VIDEOS_DIR = 'static/generated_videos'

# Voice settings
VOICE_ID = "RmgEBrAzINOXbTurITE5"  # Mary's voice ID
VOICE_SETTINGS = {
    "stability": 0.8,
    "similarity_boost": 0.6
}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///images.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)

# Import and initialize models
from models import db, Image, TextGeneration, MECVideoGeneration
db.init_app(app)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_password = request.headers.get('X-Admin-Password')
        if admin_password != ADMIN_PASSWORD:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function



@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/responsible_ai')
def responsible_ai():
    return render_template('responsible_ai.html')

@app.route('/')
def index():
    images = Image.query.all()
    # Add aspect ratio for each image
    images_with_ratio = [{
        'id': img.id,
        'filename': img.filename,
        'path': img.path,
        'aspect_ratio': get_aspect_ratio(img.filename)
    } for img in images]
    return render_template('index.html', images=images_with_ratio)

def generate_audio(text, output_file):
    """Generate audio using ElevenLabs API and save to file"""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVEN_API_KEY
    }
    
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": VOICE_SETTINGS
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"ElevenLabs API error: {response.text}")
    
    # Ensure the static/audio directory exists
    os.makedirs('static/audio', exist_ok=True)
    
    # Save the audio file
    with open(output_file, "wb") as f:
        f.write(response.content)
    
    return True

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        image_id = data.get('image_id')
        text = data.get('text')

        if not image_id or not text:
            return jsonify({'error': 'Missing image_id or text'}), 400

        # Store the generation request
        generation = TextGeneration(image_id=image_id, text=text)
        db.session.add(generation)
        db.session.commit()

        # Generate audio file
        audio_filename = f"audio_{generation.id}.mp3"
        audio_path = os.path.join('static/audio', audio_filename)
        
        generate_audio(text, audio_path)

        return jsonify({
            'success': True,
            'message': 'Text saved and audio generated successfully',
            'audio_url': f'/static/audio/{audio_filename}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def ensure_directories():
    """Ensure all required directories exist"""
    os.makedirs('static/audio', exist_ok=True)
    os.makedirs(GENERATED_VIDEOS_DIR, exist_ok=True)

def init_db():
    with app.app_context():
        db.create_all()
        # Only add images if the table is empty
        if not Image.query.first():
            image_files = [
                'mec.jpg', 'mec2.jpg', 'mec3.jpg', 'mec4.jpg',
                'mec5.jpg', 'mec6.jpeg', 'mec7.png'
            ]
            for img in image_files:
                image = Image(filename=img, path=f'mecimages/{img}')
                db.session.add(image)
            db.session.commit()

def get_aspect_ratio(filename):
    """Determine aspect ratio based on image filename"""
    if filename in ['mec.jpg', 'mec4.jpg']:
        return "9:16"
    elif filename == 'mec7.png':
        return "1:1"
    elif filename in ['mec2.jpg', 'mec3.jpg', 'mec5.jpg', 'mec6.jpeg']:
        return "16:9"
    else:
        return "16:9"  # Default fallback

def download_file(url):
    """Download a file from a URL and return its content"""
    response = requests.get(url)
    response.raise_for_status()
    return response.content

def generate_unique_token():
    """Generate a unique token for video access"""
    import secrets
    return secrets.token_urlsafe(16)

@app.route('/gallery')
def gallery():
    """Display the dynamic gallery of all MEC videos"""
    # Get all videos, ordered by newest first
    videos = MECVideoGeneration.query.order_by(MECVideoGeneration.created_at.desc()).all()
    return render_template('gallery.html', videos=videos, get_aspect_ratio=get_aspect_ratio)

@app.route('/my-video/<token>')
def my_video(token):
    """Display a specific video generation"""
    video = MECVideoGeneration.query.filter_by(unique_token=token).first_or_404()
    return render_template('my_video.html', video=video, get_aspect_ratio=get_aspect_ratio)

@app.route('/generate_video', methods=['POST'])
def generate_video():
    try:
        data = request.get_json()
        audio_url = data.get('audio_url')
        image_id = data.get('image_id')

        if not audio_url or not image_id:
            return jsonify({'error': 'Missing audio_url or image_id'}), 400

        # Get image path from database
        image = db.session.get(Image, image_id)
        if not image:
            return jsonify({'error': 'Image not found'}), 404

        # Download audio file
        audio_content = download_file(audio_url)

        # Upload audio to Hedra
        audio_response = requests.post(
            f"{HEDRA_BASE_URL}/v1/audio",
            headers={'X-API-KEY': HEDRA_API_KEY},
            files={'file': ('audio.mp3', audio_content, 'audio/mpeg')}
        )
        audio_response.raise_for_status()
        hedra_audio_url = audio_response.json()['url']

        # Get image file path
        image_path = os.path.join('static', image.path)
        
        # Upload image to Hedra
        with open(image_path, 'rb') as f:
            image_response = requests.post(
                f"{HEDRA_BASE_URL}/v1/portrait",
                headers={'X-API-KEY': HEDRA_API_KEY},
                files={'file': f}
            )
        image_response.raise_for_status()
        hedra_image_url = image_response.json()['url']

        # Initialize character generation with appropriate aspect ratio
        character_response = requests.post(
            f"{HEDRA_BASE_URL}/v1/characters",
            headers={
                'X-API-KEY': HEDRA_API_KEY,
                'Content-Type': 'application/json'
            },
            json={
                "avatarImage": hedra_image_url,
                "audioSource": "audio",
                "voiceUrl": hedra_audio_url,
                "aspectRatio": get_aspect_ratio(image.filename),
                "shared": True
            }
        )
        character_response.raise_for_status()
        
        # Get the text from the audio file name
        audio_path = urlparse(audio_url).path.split('/')[-1]
        text_gen_id = int(audio_path.split('_')[1].split('.')[0])
        text_gen = db.session.get(TextGeneration, text_gen_id)
        if not text_gen:
            return jsonify({'error': 'Text generation not found'}), 404

        # Create video generation record
        job_id = character_response.json()['jobId']
        video_gen = MECVideoGeneration(
            image_id=image_id,
            text=text_gen.text,
            job_id=job_id,
            unique_token=generate_unique_token()
        )

        # Set share URL
        video_gen.share_url = f"https://www.hedra.com/app/characters/{job_id}/view"
        
        db.session.add(video_gen)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Video generation started! Redirecting to your video page...',
            'job_id': job_id,
            'video_url': url_for('my_video', token=video_gen.unique_token, _external=True)
        })

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Hedra API error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/check_video_status/<job_id>', methods=['GET'])
def check_video_status(job_id):
    """Check video status directly from Hedra API"""
    video_gen = MECVideoGeneration.query.filter_by(job_id=job_id).first()
    if not video_gen:
        app.logger.error(f"Video not found for job_id: {job_id}")
        return jsonify({'error': 'Video not found'}), 404

    try:
        # Check video status with Hedra
        response = requests.get(
            f"{HEDRA_BASE_URL}/v1/projects/{job_id}",
            headers={'X-API-KEY': HEDRA_API_KEY}
        )
        response.raise_for_status()
        data = response.json()
        
        # Map Hedra status to our status
        status_mapping = {
            'Completed': 'completed',
            'Failed': 'failed',
            'Processing': 'pending'
        }
        current_status = status_mapping.get(data['status'], 'pending')
        
        # Update status if changed
        if current_status != video_gen.status:
            video_gen.status = current_status
            if current_status == 'completed':
                video_gen.video_url = data.get('videoUrl')
            db.session.commit()

        return jsonify({
            'status': current_status,
            'video_url': video_gen.video_url if current_status == 'completed' else None,
            'video_page': url_for('my_video', token=video_gen.unique_token, _external=True)
        })
    except Exception as e:
        app.logger.error(f"Error checking video status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/gallery')
def admin_gallery():
    admin_password = request.args.get('password')
    if admin_password != ADMIN_PASSWORD:
        return "Unauthorized", 401
    videos = MECVideoGeneration.query.order_by(MECVideoGeneration.created_at.desc()).all()
    return render_template('admin_gallery.html', videos=videos, get_aspect_ratio=get_aspect_ratio)

@app.route('/admin/delete_video/<int:video_id>', methods=['POST'])
@admin_required
def delete_video(video_id):
    try:
        video = MECVideoGeneration.query.get_or_404(video_id)
        db.session.delete(video)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    ensure_directories()
    init_db()
    app.run(port=8000, debug=True)
