import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
logging.info(f"Loading environment variables from {env_path}")
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    logging.warning(f"Warning: .env file not found at {env_path}")

API_KEY = os.getenv('YOUTUBE_API_KEY')
if not API_KEY:
    logging.error("Error: YOUTUBE_API_KEY not found in environment variables.")
    raise ValueError("YOUTUBE_API_KEY not found in environment variables.")

YOUTUBE_API_URL="https://www.googleapis.com/youtube/v3/commentThreads"