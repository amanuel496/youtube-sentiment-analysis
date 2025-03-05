import json
import pandas as pd
import logging
from pathlib import Path

base_path = Path.cwd() / 'data'  # Use the current working directory
base_path.mkdir(parents=True, exist_ok=True)

def save_to_json(comments, json_filename='comments.json'):
    """Saves comments to JSON file."""
    # Save comments to a JSON file
    with open(base_path / json_filename, 'w', encoding='utf-8') as f:
        json.dump(comments, f, ensure_ascii=False, indent=4)
    logging.info(f"Comments saved to {json_filename}")

def save_to_csv(comments, csv_filename='comments.csv'):
    """Saves comments to CSV file."""
    # Convert to a DataFrame and save as CSV
    df = pd.DataFrame(comments)
    df.to_csv(base_path / csv_filename, index=False, encoding='utf-8')
    logging.info(f"Comments saved to {csv_filename}")
