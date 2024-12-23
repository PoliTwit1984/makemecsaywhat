import os
import shutil

def clean_videos_directory():
    """Remove all videos except the target one"""
    target_video = "mec_video_f120ff53-efbb-46c5-bd55-ce5072ef7094.mp4"
    videos_dir = "static/generated_videos"
    
    # List all files in the directory
    if not os.path.exists(videos_dir):
        print(f"Directory {videos_dir} does not exist")
        return
        
    files = os.listdir(videos_dir)
    for file in files:
        if file != target_video:
            file_path = os.path.join(videos_dir, file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Deleted: {file}")
            except Exception as e:
                print(f"Error deleting {file}: {str(e)}")
    
    print("\nRemaining files:")
    remaining = os.listdir(videos_dir)
    for file in remaining:
        print(f"- {file}")

if __name__ == "__main__":
    clean_videos_directory()
