import logging
import asyncio
import re
from urllib.parse import urlparse, parse_qs

# Gensim & NLTK
from gensim import corpora, models
from nltk.tokenize import word_tokenize

# Local Modules
from src.extraction.fetch_comments import get_detailed_comments
from src.preprocessing.preprocessing import preprocess_comments
from src.sentiment_analysis.sentiment_analysis import analyze_sentiment

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ---------------------------------------------------------------------
# 1) STOPWORDS & SYNONYMS
# ---------------------------------------------------------------------
CUSTOM_STOPWORDS = {
    "text",   # Generic
    "this",   # Overly common
    "of",     # Overly common
    "n",
    "ch",
    "b",
    "c",
    "is",
    "u",
    "ng",
    "like",
    ""        # Empty string
}

SYNONYM_MAP = {
    "mr_beast": "mrbeast",
    "jimmy": "mrbeast",          # unify references to MrBeast
    "this_is": "this",
    "thanks_subscriber": "thanks"
}

# ---------------------------------------------------------------------
# 2) VIDEO ID EXTRACTION
# ---------------------------------------------------------------------
def extract_video_id(video_link: str):
    """
    Extract a YouTube video ID from either:
      - a standard link (https://www.youtube.com/watch?v=XYZ)
      - a shortened link (https://youtu.be/XYZ)

    :param video_link: The full YouTube URL
    :return: The extracted video ID or None if invalid
    """
    if not video_link:
        return None

    parsed_url = urlparse(video_link)
    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        return parse_qs(parsed_url.query).get("v", [None])[0]

    match = re.match(r"(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]+)", video_link)
    return match.group(1) if match else None

# ---------------------------------------------------------------------
# 3) SYNONYM UNIFICATION
# ---------------------------------------------------------------------
def unify_synonyms(tokens):
    """
    Replace tokens with unified forms based on the synonym map.
    Example: "mr_beast" -> "mrbeast"
    """
    return [SYNONYM_MAP.get(t, t) for t in tokens]

# ---------------------------------------------------------------------
# 4) TOPIC EXTRACTION & FORMATTING
# ---------------------------------------------------------------------
def extract_words_from_topics(topics, max_words=10):
    """
    Extracts and cleans LDA topic words, ensuring that each word has an associated weight.
    
    :param topics: list of raw topic strings from LDA.
    :param max_words: how many words to take from each raw topic.
    :return: dict with words and weights:
        {
            "positive": {"word1": weight, "word2": weight, ...},
            "negative": {"word1": weight, ...},
            "neutral": {"word1": weight, ...},
            "mixed": {"word1": weight, ...}
        }
    """
    cleaned_topics = {
        "positive": {},
        "negative": {},
        "neutral": {},
        "mixed": {}
    }

    for i, topic in enumerate(topics):
        # Extract words and weights
        word_weight_pairs = re.findall(r'([\d.]+)\*"(.*?)"', topic.lower())

        if not word_weight_pairs:
            continue

        sentiment_category = list(cleaned_topics.keys())[i % 4]  # Cycle through categories

        for weight, word in word_weight_pairs[:max_words]:
            weight = float(weight)  # Convert weight from string to float
            word = SYNONYM_MAP.get(word, word)  # Replace synonyms

            if word in CUSTOM_STOPWORDS:
                continue  # Skip stopwords

            # normalized_weight = max(1, round(weight * 100))  # Ensure positive integer weights

            normalized_weight = max(10, round(weight * 10000))  # Increase base weight for visibility


            # ✅ Store as a dictionary instead of a list
            cleaned_topics[sentiment_category][word] = normalized_weight

    return cleaned_topics


# ---------------------------------------------------------------------
# 5) CONTENT SUGGESTIONS
# ---------------------------------------------------------------------
def generate_content_suggestions(topics):
    """
    Generates content suggestions based on topic modeling results.
    Looks for keywords in the raw LDA topics and returns improvement or expansion ideas.
    """
    suggestions_map = {
        # Improvement suggestions
        "audio": "Consider improving your microphone setup or sound quality.",
        "sound": "Enhancing sound quality can boost viewer engagement.",
        "mic": "Your microphone quality might need improvement.",
        "volume": "Ensure consistent volume levels in your video.",
        "editing": "Shorter cuts or dynamic transitions might help.",
        "lighting": "Better lighting can improve video quality.",
        "quality": "Improving resolution or stability can boost satisfaction.",
        "length": "Adjust video length based on audience retention.",
        "clarity": "Clearer visuals or audio can make content more accessible.",
        "speed": "Adjust pacing to retain viewers.",
        "engagement": "Encourage comments, likes, and shares.",
        "content": "Diversify your content for sustained interest.",
        "presentation": "Refine your presentation style (tone, pacing, clarity).",
        "graphics": "Use dynamic visuals to enhance storytelling.",

        # Expansion suggestions
        "funny": "Viewers enjoy your humor! Maybe add more comedic segments.",
        "tutorial": "People want more step-by-step guides or how-tos.",
        "collab": "Collaborate with other creators for fresh perspectives.",
        "music": "Your music choices resonate with viewers. Keep it up!",
        "engaging": "Your audience likes to engage—ask questions or run polls.",
        "creative": "Your creativity stands out. Explore new formats or ideas.",
        "informative": "Viewers value your info. Consider deeper dives.",
        "relatable": "Personal stories or anecdotes can strengthen connection.",
        "motivating": "Inspiration works! Include more motivational content.",
        "interactive": "Interactive content (challenges, Q&A) is a hit."
    }

    suggestions = set()

    for topic in topics:
        # Extract words from each topic using regex
        words_in_topic = re.findall(r'"(.*?)"', topic.lower())
        # Check if any known keywords are present
        for w in words_in_topic:
            if w in suggestions_map:
                suggestions.add(suggestions_map[w])

    return list(suggestions)

# ---------------------------------------------------------------------
# 6) EXECUTIVE SUMMARY
# ---------------------------------------------------------------------
def generate_executive_summary(sentiment_counts, topics_dict, content_suggestions):
    """
    Generates a structured executive summary based on the analysis results.

    :param sentiment_counts: dict with counts of each sentiment
    :param topics_dict: dict with words as keys and weights as values.
    :param content_suggestions: list of recommended actions
    :return: string summary
    """
    total_comments = sum(sentiment_counts.values())
    if total_comments == 0:
        return "No comments were available to generate an executive summary."

    # Calculate sentiment percentages
    positive_pct = (sentiment_counts['positive'] / total_comments) * 100
    negative_pct = (sentiment_counts['negative'] / total_comments) * 100
    neutral_pct = (sentiment_counts['neutral'] / total_comments) * 100
    mixed_pct = (sentiment_counts['mixed'] / total_comments) * 100

    dominant_sentiment = max(sentiment_counts, key=sentiment_counts.get).upper()

    sentiment_text = (
        f"The overall sentiment is {dominant_sentiment} "
        f"({positive_pct:.1f}% positive, {neutral_pct:.1f}% neutral, "
        f"{negative_pct:.1f}% negative, and {mixed_pct:.1f}% mixed)."
    )

    combined_topics = []
    for cat, words in topics_dict.items():
        if words:
            # ✅ Ensure words is a dictionary, if it's a list convert to a dictionary with default weight
            if isinstance(words, list):
                words = {word: 1 for word in words}  # Assign weight 1 if missing

            # ✅ Sort and take the top 5 most weighted words
            top_words = sorted(words.items(), key=lambda item: item[1], reverse=True)[:5]
            snippet = f"{cat}: {', '.join(word for word, _ in top_words)}"
            combined_topics.append(snippet)

    topics_text = f"Top discussion topics include -> {' | '.join(combined_topics)}." if combined_topics else "No dominant topics detected."

    suggestions_text = (
        "Recommended actions: " + "; ".join(content_suggestions)
        if content_suggestions
        else "No specific content suggestions generated."
    )

    return f"{sentiment_text} {topics_text} {suggestions_text}"



# ---------------------------------------------------------------------
# 7) MAIN ETL PIPELINE
# ---------------------------------------------------------------------
async def run_etl_pipeline(video_id: str) -> dict:
    """
    Executes the full ETL pipeline for YouTube comment sentiment analysis.

    Steps:
      1) Fetch comments
      2) Preprocess
      3) Analyze sentiment
      4) Tokenize & unify synonyms
      5) LDA topic modeling
      6) Word extraction for frontend
      7) Content suggestions
      8) Executive summary
    """
    try:
        logging.info(f"Starting ETL pipeline for video ID: {video_id}")

        # 1. Fetch comments
        comments = await get_detailed_comments(video_id)
        if not comments:
            logging.warning(f"No comments found for video ID: {video_id}")
            return {"status": "No comments found"}

        # 2. Preprocess comments
        df_comments = preprocess_comments([{'text': c} for c in comments])
        if df_comments.empty:
            logging.warning("No valid comments to preprocess.")
            return {"status": "No valid comments to preprocess"}

        # 3. Analyze sentiment
        sentiment_results = analyze_sentiment(df_comments["clean_text"].tolist())
        if not sentiment_results:
            logging.warning("No sentiment analysis results available.")
            return {"status": "No sentiment analysis results"}

        # 4. Compute sentiment breakdown
        sentiment_counts = {
            "positive": sum(1 for r in sentiment_results if r["sentiment"] == "POSITIVE"),
            "negative": sum(1 for r in sentiment_results if r["sentiment"] == "NEGATIVE"),
            "neutral": sum(1 for r in sentiment_results if r["sentiment"] == "NEUTRAL"),
            "mixed": sum(1 for r in sentiment_results if r["sentiment"] == "MIXED")
        }

        # 5. Tokenize & unify synonyms
        tokenized_comments = []
        for text in df_comments["clean_text"]:
            tokens = word_tokenize(text.lower())
            tokens = unify_synonyms(tokens)
            # remove custom stopwords
            tokens = [t for t in tokens if t not in CUSTOM_STOPWORDS]
            tokenized_comments.append(tokens)

        # 6. LDA Topic Modeling
        dictionary = corpora.Dictionary(tokenized_comments)
        # remove extremely rare or overly common tokens
        dictionary.filter_extremes(no_below=2, no_above=0.5, keep_n=10000)

        corpus = [dictionary.doc2bow(doc) for doc in tokenized_comments]
        lda_model = models.LdaModel(
            corpus=corpus,
            num_topics=10,
            id2word=dictionary,
            passes=5,
            random_state=42
        )
        top_topics = [lda_model.print_topic(i) for i in range(10)]

        # 7. Word extraction for the frontend
        formatted_topics = extract_words_from_topics(top_topics)

        # 8. Generate content suggestions
        content_suggestions = generate_content_suggestions(top_topics)

        # 9. Generate executive summary
        executive_summary = generate_executive_summary(sentiment_counts, formatted_topics, content_suggestions)

        return {
            "status": "Success",
            "sentiment_breakdown": sentiment_counts,
            "topics": formatted_topics,          # For the word cloud (dict with words by sentiment)
            "content_suggestions": content_suggestions,
            "executive_summary": executive_summary
        }

    except Exception as e:
        logging.error(f"Error during ETL pipeline execution: {e}", exc_info=True)
        return {"status": "Error", "message": str(e)}


def lambda_handler(event, context):
    video_link = event.get("queryStringParameters", {}).get("videoLink", "")
    video_id = extract_video_id(video_link)
    # print(f"video id: {video_id} and video link: {video_link}")
    if not video_id:
        logging.error("Invalid video link provided.")
        return {"status": "Invalid video link"}
    # TODO: Delete the following line if it's not needed
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
        "body": response
        # "body": json.dumps(response)
    }

# if name == 'main':
#     lambda_handler({
#         "queryStringParameters": {
#             "videoLink": "https://www.youtube.com/watch?v=T7M3PpjBZzw",
#             "outputFormat": "json"
#         }
#     }, None)
