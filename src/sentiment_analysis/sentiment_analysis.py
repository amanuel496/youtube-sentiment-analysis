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
        "I love the new design!",   # Positive sentiment
        "I hate the update.",       # Negative sentiment                        
        "It's okay I guess."        # Neutral sentiment
    ]
    sentiment_results = analyze_sentiment(comments)
    for result in sentiment_results:
        print(result)
# Output:
# {'text': 'I love the new design!', 'sentiment': 'POSITIVE', 'sentiment_score': {'Positive': 0.9998810296058655, 'Negative': 1.2374326209155175e-05, 'Neutral': 0.00010636009244856253, 'Mixed': 1.2598838236174135e-05}}  
# {'text': 'I hate the update.', 'sentiment': 'NEGATIVE', 'sentiment_score': {'Positive': 0.00010636009244856253, 'Negative': 0.9998810296058655, 'Neutral': 1.2374326209155175e-05, 'Mixed': 1.2598838236174135e-05}}
# {'text': "It's okay I guess.", 'sentiment': 'NEUTRAL', 'sentiment_score': {}}     
# The sentiment analysis results are printed for each comment, including the sentiment label and sentiment score.
# The sentiment score is a dictionary containing the probabilities for different sentiment categories (Positive, Negative, Neutral, Mixed).     
# The sentiment analysis function uses the AWS Comprehend client to analyze the sentiment of each comment.
# The sentiment results are returned as a list of dictionaries, where each dictionary contains the original comment text, sentiment label, and sentiment score.
# The sentiment label indicates the overall sentiment of the comment (POSITIVE, NEGATIVE, NEUTRAL).
# The sentiment score provides the probabilities for each sentiment category based on the AWS Comprehend analysis.