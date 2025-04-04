import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Detect the environment mode
ENV = os.getenv("ENV", "dev")  # Default to "dev" if ENV is not set

if ENV == "dev":
    # Load environment variables from .env file in development
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        logging.info(f"Loading environment variables from {env_path}")
        load_dotenv(dotenv_path=env_path)
    else:
        logging.warning(f"Warning: .env file not found at {env_path}")

# Load API keys and configuration from environment variables
API_KEY = os.getenv('YOUTUBE_API_KEY')
AWS_ACCESS_KEY_ID = os.getenv('MY_AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('MY_AWS_SECRET_KEY')
AWS_REGION = os.getenv('MY_AWS_REGION')
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/commentThreads"

# Validate environment variables
if not all([API_KEY, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION]):
    logging.error("Error: Required environment variables are missing.")
    raise ValueError("Environment variables not found.")

logging.info("Environment variables loaded successfully.")
