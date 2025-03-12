import json
import pandas as pd
import logging
import boto3
from io import StringIO

# Initialize the S3 client
s3_client = boto3.client('s3')

# Define your S3 bucket name and folder path
BUCKET_NAME = "youtube-sentiment-analysis-backend"
S3_FOLDER = "lambda-results/"

def save_to_json(comments, json_filename='comments.json') -> None:
    """Saves a list of comments to a JSON file and uploads it to S3."""
    try:
        json_data = json.dumps(comments, ensure_ascii=False, indent=4)
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=f"{S3_FOLDER}{json_filename}",
            Body=json_data,
            ContentType="application/json"
        )
        logging.info(f"Comments saved to s3://{BUCKET_NAME}/{S3_FOLDER}{json_filename}")
    except Exception as e:
        logging.error(f"Failed to save comments to JSON: {e}", exc_info=True)

def save_to_csv(comments, csv_filename='comments.csv') -> None:
    """Saves a list of comments to a CSV file and uploads it to S3."""
    try:
        df = pd.DataFrame(comments)
        
        # Convert DataFrame to CSV in memory
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8')
        
        # Upload CSV to S3
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=f"{S3_FOLDER}{csv_filename}",
            Body=csv_buffer.getvalue(),
            ContentType="text/csv"
        )
        logging.info(f"Comments saved to s3://{BUCKET_NAME}/{S3_FOLDER}{csv_filename}")
        print(f"Comments saved to s3://{BUCKET_NAME}/{S3_FOLDER}{csv_filename}")
    except Exception as e:
        logging.error(f"Failed to save comments to CSV: {e}", exc_info=True)

# # Example usage
# comments = [
#     {"user": "Alice", "comment": "Great video!", "sentiment": "positive"},
#     {"user": "Bob", "comment": "I didn't like it.", "sentiment": "negative"}
# ]

# save_to_json(comments)
# save_to_csv(comments)
