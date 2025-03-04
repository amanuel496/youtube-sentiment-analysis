import json
import pandas as pd
import logging

def save_comments_to_files(comments, json_filename='comments.json', csv_filename='comments.csv'):
    """Saves comments to JSON and CSV files."""
    # Save comments to a JSON file
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(comments, f, ensure_ascii=False, indent=4)
    
    # Convert to a DataFrame and save as CSV
    df = pd.DataFrame(comments)
    df.to_csv(csv_filename, index=False, encoding='utf-8')
    logging.info(f"Comments saved to {json_filename} and {csv_filename}")
