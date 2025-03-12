from src.utils import nltk_setup
import logging
import asyncio
import json
from src.extraction.fetch_comments import get_detailed_comments
from src.utils.file_saver import save_to_csv, save_to_json
from src.preprocessing.preprocessing import preprocess_comments
from src.sentiment_analysis.sentiment_analysis import analyze_sentiment
from collections import Counter
from nltk.corpus import stopwords
import re
from urllib.parse import urlparse, parse_qs

import boto3
import csv
import io

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_content_suggestions(keywords_summary):
    """
    Generate content suggestions based on frequently mentioned keywords in negative or positive feedback.
    Expands coverage by adding broad topics and more natural language variants.
    """
    # Expanded suggestions map with broader topics and synonyms
    suggestions_map = {
        # Improvement suggestions (from negative feedback)
        "audio": "Consider improving your microphone setup, sound quality, or background music.",
        "sound": "Enhancing sound quality can improve viewer engagement.",
        "mic": "Your microphone quality might need improvement.",
        "volume": "Check for consistent volume levels throughout your video.",
        "editing": "Shorter cuts, dynamic transitions, or more concise storytelling might help.",
        "lighting": "Investing in better lighting can enhance video quality.",
        "quality": "Improving video resolution and stability can increase viewer satisfaction.",
        "length": "Consider adjusting video length based on audience retention data.",
        "clarity": "Clearer visuals or audio can make your content more accessible.",
        "speed": "Adjusting the pace of your content might improve viewer retention.",
        "engagement": "Encourage more comments, likes, and shares to boost engagement.",
        "content": "Diversify your content to keep your audience interested.",
        "presentation": "Improve presentation style, such as tone, pacing, and clarity.",
        "graphics": "Use more dynamic graphics or visuals to enhance your videos.",

        # Expansion suggestions (from positive feedback)
        "funny": "Viewers like your humor! Consider adding more comedic segments.",
        "tutorial": "People want step-by-step guides. Consider making more in-depth tutorial content.",
        "collab": "Your audience is interested in collaborations. Reach out to other creators!",
        "music": "Viewers enjoy your music choice. Keep up the great soundtracks!",
        "engaging": "Your engagement with the audience is great! Keep asking questions or starting discussions.",
        "creative": "Your creativity stands out. Try exploring more innovative formats or ideas.",
        "informative": "Your audience values the information you provide. More deep dives could be beneficial.",
        "relatable": "Your content resonates well. Sharing more personal stories might increase this effect.",
        "motivating": "People find your content inspiring. More motivational content could attract new viewers.",
        "interactive": "Interactive content is a hit! Consider adding polls, quizzes, or viewer challenges."
    }

    suggestions = []

    # We'll look at both negative and positive keywords for suggestions
    for sentiment, keywords in keywords_summary.items():
        for keyword in keywords.keys():
            key_lower = keyword.lower()
            if key_lower in suggestions_map:
                suggestions.append(suggestions_map[key_lower])

    # Deduplicate and return
    suggestions = list(set(suggestions))
    return suggestions


def generate_executive_summary(sentiment_counts, keywords_summary, content_suggestions):
    """
    Generates an executive summary based on sentiment analysis, keyword highlights, and content suggestions.
    """
    total_comments = sum(sentiment_counts.values())
    if total_comments == 0:
        return "No comments were available to generate an executive summary."

    positive_pct = (sentiment_counts.get('positive', 0) / total_comments) * 100
    negative_pct = (sentiment_counts.get('negative', 0) / total_comments) * 100
    neutral_pct = (sentiment_counts.get('neutral', 0) / total_comments) * 100
    mixed_pct = (sentiment_counts.get('mixed', 0) / total_comments) * 100

    sentiment_summary = (
        f"The overall sentiment is positive ({positive_pct:.1f}%), "
        f"with {neutral_pct:.1f}% neutral, {negative_pct:.1f}% negative, "
        f"and {mixed_pct:.1f}% mixed reactions."
    )

    # Highlight top keywords
    top_keywords = []
    for sentiment, keywords in keywords_summary.items():
        if keywords:
            # Only take the first 5 keywords from each sentiment to avoid overly long summary
            top_keywords.extend([f"{k} ({v})" for k, v in list(keywords.items())[:5]])

    if top_keywords:
        keywords_summary_text = f"Top keywords mentioned include: {', '.join(top_keywords)}."
    else:
        keywords_summary_text = "No significant keywords were highlighted in the analysis."

    # Summarize content suggestions
    if content_suggestions:
        suggestions_text = "Recommended actions: " + "; ".join(content_suggestions)
    else:
        suggestions_text = "No specific content suggestions were generated."

    executive_summary = (
        f"{sentiment_summary}"
        f"{keywords_summary_text}"
        f"{suggestions_text}"
    )
    return executive_summary

def extract_video_id(video_link):
    if not video_link:
        return None

    # Try extracting from a standard YouTube URL (e.g., https://www.youtube.com/watch?v=VIDEO_ID)
    parsed_url = urlparse(video_link)
    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        query_params = parse_qs(parsed_url.query)
        return query_params.get("v", [None])[0]

    # Try extracting from a shortened YouTube URL (e.g., https://youtu.be/VIDEO_ID)
    match = re.match(r"(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]+)", video_link)
    if match:
        return match.group(1)

    return None

async def run_etl_pipeline(video_id: str, output_format: str = 'json') -> dict:
    """Executes the ETL pipeline for YouTube comment sentiment analysis."""
    try:
        logging.info(f"Starting ETL pipeline for video ID: {video_id}")
        
        # # Step 1: Extract - Fetch comments
        # comments = await get_detailed_comments(video_id)
        # if not comments:
        #     logging.warning(f"No comments found for video ID: {video_id}")
        #     return {"status": "No comments found"}

        # # Step 2: Transform - Preprocess
        # preprocessed_comments = preprocess_comments([{'text': comment} for comment in comments])
        # if preprocessed_comments.empty:
        #     logging.warning("No valid comments to preprocess.")
        #     return {"status": "No valid comments to preprocess"}

        # # Step 3: Sentiment Analysis
        # # sentiment_results = analyze_sentiment(preprocessed_comments['clean_text'].tolist())
        # # if not sentiment_results:
        # #     logging.warning("No sentiment analysis results available.")
        # #     return {"status": "No sentiment analysis results"}
        s3_client = boto3.client('s3')
        BUCKET_NAME = "youtube-sentiment-analysis-backend"
        S3_FOLDER = "lambda-results/"
        json_filename = "sentiment_results.csv"
        response = s3_client.get_object(
            Bucket=BUCKET_NAME,
            Key=f"{S3_FOLDER}{json_filename}"
        )

        # Read the content
        # sentiment_results = json_data['Body'].read().decode('utf-8')
        # Read the CSV file
        csv_data = response['Body'].read().decode('utf-8')

        # Parse CSV into a list of dictionaries
        sentiment_results = list(csv.DictReader(io.StringIO(csv_data)))
        # print("sentiment_results type", type(sentiment_results))
        # print("json_data type", type(json_data))
        # print("sentiment results data", sentiment_results)
        # print("json_data", json_data)


        # Calculate sentiment breakdown
        sentiment_counts = {
            'positive': sum(1 for r in sentiment_results if r['sentiment'] == 'POSITIVE'),
            'negative': sum(1 for r in sentiment_results if r['sentiment'] == 'NEGATIVE'),
            'neutral':  sum(1 for r in sentiment_results if r['sentiment'] == 'NEUTRAL'),
            'mixed':    sum(1 for r in sentiment_results if r['sentiment'] == 'MIXED')
        }

        # Keywords by sentiment
        stop_words = set(stopwords.words('english'))
        keywords_by_sentiment = {'positive': [], 'negative': [], 'neutral': [], 'mixed': []}

        for result in sentiment_results:
            sentiment = result['sentiment'].lower()
            if sentiment in keywords_by_sentiment:
                words = [
                    word for word in result['text'].split()
                    if word.lower() not in stop_words
                ]
                keywords_by_sentiment[sentiment].extend(words)
            else:
                logging.warning(f"Unexpected sentiment type: {sentiment}")

        # Top 10 keywords for each sentiment
        keywords_summary = {
            sentiment: dict(Counter(words).most_common(10))
            for sentiment, words in keywords_by_sentiment.items()
        }

        # Generate content suggestions from keywords
        content_suggestions = generate_content_suggestions(keywords_summary)
    except Exception as e:
        logging.error(f"Error during ETL pipeline execution: {e}", exc_info=True)
        return {"status": "Error", "message": str(e)}
    # Generate content suggestions from keywords
    content_suggestions = generate_content_suggestions(keywords_summary)

    # Generate the executive summary
    executive_summary = generate_executive_summary(
        sentiment_counts,
        keywords_summary,
        content_suggestions
    )

    # Load - Save the sentiment analysis results to a file
    output_filename = f"comments_{video_id}.{output_format}"
    if output_format == 'json':
        save_to_json(sentiment_results, output_filename)
    elif output_format == 'csv':
        save_to_csv(sentiment_results, output_filename)
    else:
        logging.error(f"Unsupported output format: {output_format}")
            # return
        
    logging.info(f"ETL pipeline completed successfully. Output saved to {output_filename}")

    return {
        "status": "Success",
        "sentiment_breakdown": sentiment_counts,
        "keywords_summary": keywords_summary,
        "content_suggestions": content_suggestions,
        "executive_summary": executive_summary
    }


def lambda_handler(event, context):
    video_link = event.get("queryStringParameters", {}).get("videoLink", "")
    video_id = extract_video_id(video_link)
    print(f"video id: {video_id} and video link: {video_link}")
    if not video_id:
        logging.error("Invalid video link provided.")
        return {"status": "Invalid video link"}
    output_format = event.get("queryStringParameters", {}).get("outputFormat", "json").lower()
    
    loop = asyncio.get_event_loop()
    response = loop.run_until_complete(run_etl_pipeline(video_id, output_format))

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps(response)
    }
