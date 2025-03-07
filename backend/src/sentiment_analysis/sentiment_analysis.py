import boto3
import logging
from typing import List, Dict
import os
import sys

# Add the src directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION

# Initialize Boto3 client using environment variables
comprehend = boto3.client(
    'comprehend',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def analyze_sentiment(comments: List[str]) -> List[Dict[str, str]]:
    """Analyzes sentiment of comments using AWS Comprehend."""
    try:
        sentiment_results = []
        for comment in comments:
            if comment.strip():
                response = comprehend.detect_sentiment(
                    Text=comment,
                    LanguageCode='en'
                )
                sentiment_results.append({
                    'text': comment,
                    'sentiment': response['Sentiment'],
                    'sentiment_score': response['SentimentScore']
                })
            else:
                sentiment_results.append({
                    'text': comment,
                    'sentiment': 'NEUTRAL',
                    'sentiment_score': {}
                })

        return sentiment_results

    except Exception as e:
        logging.error(f"Error during sentiment analysis: {e}", exc_info=True)
        return []
    
if __name__ == '__main__':  
    comments = [
        "I love the new design!",
        "I hate the update.",
        "It's okay I guess."
    ]
    sentiment_results = analyze_sentiment(comments)
    for result in sentiment_results:
        print(result)
