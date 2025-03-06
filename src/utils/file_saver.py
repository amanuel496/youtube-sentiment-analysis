import json
import pandas as pd
import logging
from pathlib import Path

# Set up the base path for saving files
base_path = Path.cwd() / 'data'
base_path.mkdir(parents=True, exist_ok=True)

def save_to_json(comments, json_filename='comments.json') -> None:
    """Saves a list of comments to a JSON file."""
    try:
        with open(base_path / json_filename, 'w', encoding='utf-8') as f:
            json.dump(comments, f, ensure_ascii=False, indent=4)
        logging.info(f"Comments saved to {json_filename}")
    except Exception as e:
        logging.error(f"Failed to save comments to JSON: {e}", exc_info=True)

def save_to_csv(comments, csv_filename='comments.csv') -> None:
    """Saves a list of comments to a CSV file."""
    try:
        df = pd.DataFrame(comments)
        df.to_csv(base_path / csv_filename, index=False, encoding='utf-8')
        logging.info(f"Comments saved to {csv_filename}")
    except Exception as e:
        logging.error(f"Failed to save comments to CSV: {e}", exc_info=True)
