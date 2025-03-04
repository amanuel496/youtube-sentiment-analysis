import aiohttp
import os
import logging
from dotenv import load_dotenv
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential
from src.extraction.file_saver import save_comments_to_files
from config import YOUTUBE_API_URL, API_KEY

@retry(stop=stop_after_attempt(5), wait=wait_exponential(min=1, max=10), reraise=True)
async def fetch_comments_page(session, video_id, page_token=None):
    """Fetches a page of comments from YouTube API asynchronously."""
    params = {
        'part': 'snippet',
        'videoId': video_id,
        'maxResults': 100,
        'textFormat': 'plainText',
        'key': API_KEY
    }
    # Add 'pageToken' only if it is not None
    if page_token:
        params['pageToken'] = page_token

    async with session.get(YOUTUBE_API_URL, params=params) as response:
        if response.status == 200:
            return await response.json()
        else:
            logging.error(f"Failed to fetch comments page: HTTP {response.status}")
            print(f"params: {params}")

            response.raise_for_status()

async def get_detailed_comments(video_id, max_results=1000):
    """Fetches detailed comments from a YouTube video asynchronously with pagination and retry logic."""
    comments = []
    async with aiohttp.ClientSession() as session:
        next_page_token = None
        while len(comments) < max_results:
            print(f"Fetching comments for video ID: {video_id}, page token: {next_page_token}")
            try:
                response = await fetch_comments_page(session, video_id, next_page_token)
                print(f"Response: {response}")
                if 'error' in response:
                    logging.error(f"Error in response: {response['error']['message']}")
                    break
                for item in response.get('items', []):
                    comment_data = item['snippet']['topLevelComment']['snippet']
                    comment = {
                        'text': comment_data['textDisplay'],
                        'author': comment_data['authorDisplayName'],
                        'likes': comment_data['likeCount'],
                        'published_at': comment_data['publishedAt']
                    }
                    comments.append(comment)
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
            except Exception as e:
                logging.error(f"Error fetching comments: {e}")
                break

        logging.info(f"Fetched {len(comments)} comments from video ID: {video_id}")
    return comments

if __name__ == '__main__':
    import asyncio
    video_id = "th5_9woFJmk"  # Example YouTube video ID
    comments = asyncio.run(get_detailed_comments(video_id, max_results=2))
    save_comments_to_files(comments)