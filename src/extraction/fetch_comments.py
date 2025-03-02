from googleapiclient.discovery import build
import json
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
print(f"Loading environment variables from {env_path}")
if env_path.exists():   # Check if the .env file exists
    load_dotenv(dotenv_path=env_path)
else:
    print(f"Warning: .env file not found at {env_path}")

# YouTube API configuration
api_key = os.getenv('YOUTUBE_API_KEY') 
youtube = build('youtube', 'v3', developerKey=api_key)

def get_video_comments(video_id, max_results=100):
    """Fetches comments from a YouTube video."""
    comments = []
    try:
        response = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=max_results,
            textFormat='plainText'
        ).execute()

        for item in response.get('items', []):
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)
        
        print(f"Fetched {len(comments)} comments from video ID: {video_id}")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return comments

# Test the function
video_id = "th5_9woFJmk"
comments = get_video_comments(video_id)

# Save comments to a JSON file
with open('comments.json', 'w', encoding='utf-8') as f:
    json.dump(comments, f, ensure_ascii=False, indent=4)
