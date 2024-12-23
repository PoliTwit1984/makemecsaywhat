import os
import sqlite3
import requests
import logging
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient

# Configuration (to be set in Azure Function App settings)
HEDRA_API_KEY = os.environ.get('HEDRA_API_KEY')
HEDRA_BASE_URL = 'https://mercury.dev.dream-ai.com/api'
DB_PATH = os.environ.get('DB_PATH', 'images.db')  # SQLite database path
STORAGE_CONNECTION_STRING = os.environ.get('STORAGE_CONNECTION_STRING')
CONTAINER_NAME = 'generated-videos'

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def download_video(video_id, video_url):
    """Download video from Hedra and upload to Azure Blob Storage"""
    try:
        # Download video
        headers = {
            'Accept': 'video/mp4',
            'User-Agent': 'Mozilla/5.0'
        }
        response = requests.get(video_url, stream=True, headers=headers)
        response.raise_for_status()
        
        # Generate filename
        filename = f"mec_video_{video_id}.mp4"
        
        # Upload to Azure Blob Storage
        blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        blob_client = container_client.get_blob_client(filename)
        
        # Upload video data
        blob_client.upload_blob(response.content, overwrite=True)
        
        # Generate URL (valid for 1 year)
        sas_token = blob_client.generate_sas(
            permission="r",
            expiry=datetime.utcnow() + timedelta(days=365)
        )
        blob_url = f"{blob_client.url}?{sas_token}"
        
        return f"generated_videos/{filename}", blob_url
    except Exception as e:
        logging.error(f"Error downloading video {video_id}: {str(e)}")
        return None, None

def ensure_video_shared(video_id):
    """Ensure video is shared on Hedra"""
    try:
        headers = {'X-API-KEY': HEDRA_API_KEY}
        share_response = requests.post(
            f"{HEDRA_BASE_URL}/v1/projects/{video_id}/sharing?shared=true",
            headers=headers
        )
        share_response.raise_for_status()
        return True
    except Exception as e:
        logging.error(f"Error sharing video {video_id}: {str(e)}")
        return False

def get_video_url(video_id):
    """Get fresh video URL from Hedra API"""
    try:
        headers = {'X-API-KEY': HEDRA_API_KEY}
        response = requests.get(
            f"{HEDRA_BASE_URL}/v1/projects/{video_id}",
            headers=headers
        )
        response.raise_for_status()
        data = response.json()
        return data.get('videoUrl')
    except Exception as e:
        logging.error(f"Error getting video URL for {video_id}: {str(e)}")
        return None

def main(timer: str) -> None:
    """Main function to run on a timer trigger"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get completed videos without local path
        cursor.execute("""
            SELECT job_id, status
            FROM mec_video_generation
            WHERE status = 'completed'
            AND (local_video_path IS NULL OR local_video_path = '')
        """)
        videos = cursor.fetchall()
        
        for video in videos:
            video_id = video['job_id']
            logging.info(f"Processing video {video_id}")
            
            # Ensure video is shared
            if not ensure_video_shared(video_id):
                continue
                
            # Get fresh video URL
            video_url = get_video_url(video_id)
            if not video_url:
                continue
            
            # Download video and upload to blob storage
            local_path, blob_url = download_video(video_id, video_url)
            if local_path and blob_url:
                # Update database
                cursor.execute("""
                    UPDATE mec_video_generation
                    SET local_video_path = ?, video_url = ?
                    WHERE job_id = ?
                """, (local_path, blob_url, video_id))
                conn.commit()
                logging.info(f"Successfully processed video {video_id}")
            
        conn.close()
        
    except Exception as e:
        logging.error(f"Error in main function: {str(e)}")
        if 'conn' in locals():
            conn.close()

# For local testing
if __name__ == "__main__":
    main("")
