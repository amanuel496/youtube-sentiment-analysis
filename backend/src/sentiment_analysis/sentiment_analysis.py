import logging
from typing import List, Dict
from nltk.sentiment import SentimentIntensityAnalyzer

# Initialize NLTK's VADER Sentiment Analyzer
sia = SentimentIntensityAnalyzer()

def analyze_sentiment(comments: List[str]) -> List[Dict[str, str]]:
    """Analyzes sentiment of comments using NLTK's VADER."""
    try:
        sentiment_results = []
        for comment in comments:
            if comment.strip():
                sentiment_score = sia.polarity_scores(comment)
                sentiment_label = (
                    "POSITIVE" if sentiment_score['compound'] > 0.05 
                    else "NEGATIVE" if sentiment_score['compound'] < -0.05 
                    else "NEUTRAL"
                )
                sentiment_results.append({
                    'text': comment,
                    'sentiment': sentiment_label,
                    'sentiment_score': sentiment_score
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
