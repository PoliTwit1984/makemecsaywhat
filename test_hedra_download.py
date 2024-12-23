import os
import requests
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
HEDRA_API_KEY = os.getenv('HEDRA_API_KEY')

def download_hedra_video(share_url):
    """
    Download video from Hedra's shared URL and save it locally
    """
    print(f"\nStarting video download process")
    print(f"Share URL: {share_url}")
    
    # Create videos directory if it doesn't exist
    videos_dir = 'downloaded_videos'
    os.makedirs(videos_dir, exist_ok=True)
    print(f"Ensured directory exists: {videos_dir}")

    try:
        # Get video ID from share URL
        video_id = share_url.split('/')[-2]
        
        # First try to get video URL directly from Hedra API
        print("Getting video details from Hedra API...")
        api_url = f"https://mercury.dev.dream-ai.com/api/v1/projects/{video_id}"
        headers = {
            'X-API-KEY': HEDRA_API_KEY
        }
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        
        # Try to get video URL from API response first
        data = response.json()
        video_url = data.get('videoUrl')
        
        if video_url:
            print(f"Found video URL in API response: {video_url}")
        else:
            print("No video URL in API response, trying share URL...")
            
            # Ensure video is shared
            print("Ensuring video is shared...")
            share_response = requests.post(
                f"https://mercury.dev.dream-ai.com/api/v1/projects/{video_id}/sharing?shared=true",
                headers=headers
            )
            share_response.raise_for_status()
            
            # Get the share page
            print("Getting video page...")
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'X-API-KEY': HEDRA_API_KEY
            }
            response = requests.get(share_url, headers=headers)
            response.raise_for_status()
            
            # Try to parse as JSON first
            try:
                json_data = response.json()
                if 'videoUrl' in json_data:
                    video_url = json_data['videoUrl']
                    print(f"Found video URL in share page JSON: {video_url}")
                elif 'data' in json_data and isinstance(json_data['data'], dict) and 'videoUrl' in json_data['data']:
                    video_url = json_data['data']['videoUrl']
                    print(f"Found video URL in share page data: {video_url}")
            except Exception as e:
                print(f"Failed to parse share page as JSON: {e}")
            
            # If still no URL, try HTML parsing
            if not video_url:
                print("Searching for video URL in page content...")
                patterns = [
                    r'https://dream-product\.s3\.amazonaws\.com/[^"\']+\.mp4',  # Direct S3 URL
                    r'videoUrl":\s*"([^"]+)"',  # JSON data
                    r'video src="([^"]+)"',  # Video tag
                    r'"url":"(https://dream-product[^"]+\.mp4)"'  # JSON URL format
                ]
                
                for pattern in patterns:
                    video_match = re.search(pattern, response.text)
                    if video_match:
                        video_url = video_match.group(1) if '(' in pattern else video_match.group(0)
                        print(f"Found video URL using pattern '{pattern}': {video_url}")
                        break
        
        if not video_url:
            print("Could not find video URL in page")
            print("Page content sample (first 1000 chars):")
            print(response.text[:1000])
            return None
        
        # Download video
        print("Starting download...")
        headers = {
            'Accept': 'video/mp4',
            'User-Agent': 'Mozilla/5.0'
        }
        response = requests.get(video_url, stream=True, headers=headers, allow_redirects=True)
        response.raise_for_status()
        content_length = int(response.headers.get('content-length', 0))
        print(f"Content length: {content_length} bytes")

        # Generate filename from share URL
        video_id = share_url.split('/')[-2]  # Extract ID from share URL
        filename = f"hedra_video_{video_id}.mp4"
        filepath = os.path.join(videos_dir, filename)

        # Save video to file
        bytes_written = 0
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    bytes_written += len(chunk)
                    if content_length:
                        progress = (bytes_written / content_length) * 100
                        print(f"Download progress: {progress:.1f}%")

        print(f"Download complete. Total bytes written: {bytes_written}")
        
        # Verify file size
        if content_length > 0:
            file_size = os.path.getsize(filepath)
            if file_size != content_length:
                print(f"File size mismatch: expected {content_length}, got {file_size}")
                os.remove(filepath)
                return None
            print(f"File size verified: {file_size} bytes")
        
        print(f"Video saved to: {filepath}")
        return filepath

    except requests.exceptions.RequestException as e:
        print(f"Error downloading video: {str(e)}")
        if 'response' in locals():
            print(f"Response status code: {response.status_code}")
            print(f"Response headers: {response.headers}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None

if __name__ == "__main__":
    # Test with the shared video URL
    share_url = "https://www.hedra.com/app/characters/97549171-dd6e-4d57-9ebc-94e05f52eaa6/view"
    result = download_hedra_video(share_url)
    if result:
        print(f"\nSuccess! Video downloaded to: {result}")
    else:
        print("\nFailed to download video")
