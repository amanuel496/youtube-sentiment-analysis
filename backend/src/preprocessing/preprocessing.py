import logging
import re
from typing import List, Dict

import pandas as pd

# Gensim
from gensim.models import Phrases
from gensim.models.phrases import Phraser

# NLTK
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ---------------------------------------
# Global Objects & Configuration
# ---------------------------------------
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))

# Add any custom stopwords you want to remove
CUSTOM_STOPWORDS = {
    "text", "this", "is", "us", "at", "lots", "characters", "of", "amp"  # 'amp' from HTML decode
}

# Combine standard + custom stopwords
ALL_STOPWORDS = stop_words.union(CUSTOM_STOPWORDS)

# Whitelist words that you DON'T want lemmatized or removed, even if they're in stopwords
WHITELIST = {"this", "text", "us", "of"}


# ---------------------------------------
# 1) Vectorized Cleaning of Raw Text
# ---------------------------------------
def clean_raw_text(series: pd.Series) -> pd.Series:
    """
    Cleans and normalizes raw text using vectorized methods:
    1. Lowercase and fill missing values.
    2. Remove URLs, HTML tags, emails, and special characters.
    3. Remove extra whitespace.

    :param series: A pandas Series of raw text data.
    :return: A cleaned pandas Series.
    """
    try:
        logging.debug("Starting vectorized text cleaning.")

        # 1. Lowercase & fill NaNs
        series = series.fillna("").astype(str).str.lower()

        # 2. Regex replacements in a single pass
        series = series.str.replace(r"http\S+|www\.\S+", "", regex=True)  # remove URLs
        series = series.str.replace(r"<.*?>", "", regex=True)            # remove HTML tags
        series = series.str.replace(r"(\S+)@(\S+)\.(\S+)", r"\1 \2\3", regex=True)  # emails
        series = series.str.replace(r"[^a-zA-Z\s]", " ", regex=True)     # remove special chars
        series = series.str.replace(r"\s+", " ", regex=True).str.strip() # extra whitespace

        logging.debug("Vectorized text cleaning completed.")
        return series

    except Exception as e:
        logging.error(f"Error during raw text cleaning: {e}", exc_info=True)
        # Return an empty Series of the same length to avoid breaking downstream code
        return pd.Series([""] * len(series), index=series.index)


# ---------------------------------------
# 2) Token-Level Processing
# ---------------------------------------
def tokenize_remove_stopwords_lemmatize(text: str) -> List[str]:
    """
    Tokenizes a single string of text, removes stopwords, and lemmatizes each token.
    Whitelisted words are excluded from lemmatization and stopword removal.

    :param text: A cleaned string of text.
    :return: A list of processed tokens.
    """
    tokens = word_tokenize(text)

    processed_tokens = []
    for token in tokens:
        # If token is whitelisted, keep it exactly
        if token in WHITELIST:
            processed_tokens.append(token)
        # Otherwise, remove if it's in ALL_STOPWORDS
        elif token not in ALL_STOPWORDS:
            # Lemmatize the token
            lemma = lemmatizer.lemmatize(token)
            processed_tokens.append(lemma)

    return processed_tokens


# ---------------------------------------
# 3) Bigrams
# ---------------------------------------
def generate_bigrams(tokenized_docs: List[List[str]], min_count=5, threshold=10) -> List[List[str]]:
    """
    Generates bigrams from tokenized comments to improve topic modeling.

    :param tokenized_docs: List of token lists, e.g., [["this", "video"], ...]
    :param min_count: Minimum count of tokens to form a bigram.
    :param threshold: Phrase score threshold. Higher threshold means fewer phrases.
    :return: List of token lists with bigrams included where relevant.
    """
    bigram_model = Phrases(tokenized_docs, min_count=min_count, threshold=threshold)
    bigram_phraser = Phraser(bigram_model)

    return [bigram_phraser[doc] for doc in tokenized_docs]


# ---------------------------------------
# 4) Main Preprocessing Function
# ---------------------------------------
def preprocess_comments(comments: List[Dict[str, str]], 
                        min_count=5, 
                        threshold=10, 
                        use_bigrams=True) -> pd.DataFrame:
    """
    Preprocesses a list of comments by:
      1) Vectorized cleaning (remove URLs, HTML, etc.)
      2) Tokenization, stopword removal, and lemmatization
      3) (Optional) Bigram generation
      4) Re-joining tokens into a final 'clean_text'

    :param comments: List of dictionaries, each with a 'text' key.
    :param min_count: Bigram min_count parameter.
    :param threshold: Bigram threshold parameter.
    :param use_bigrams: Whether to generate bigrams.
    :return: A pandas DataFrame with columns ['text', 'clean_text', 'tokens'] (and optionally 'bigrams').
    """
    try:
        # Convert to DataFrame
        df = pd.DataFrame(comments)

        # Ensure we have a 'text' column
        if "text" not in df.columns:
            logging.error("The 'text' column is missing from the input data.")
            return pd.DataFrame()

        # 1. Vectorized cleaning
        df["raw_clean_text"] = clean_raw_text(df["text"])

        # 2. Token-level cleaning (stopwords, lemmatization)
        df["tokens"] = df["raw_clean_text"].apply(tokenize_remove_stopwords_lemmatize)

        # Remove rows where token list is empty
        df = df[df["tokens"].apply(len) > 0]

        # 3. (Optional) Generate bigrams
        if use_bigrams and not df.empty:
            tokens_list = df["tokens"].tolist()
            bigrams_list = generate_bigrams(tokens_list, min_count=min_count, threshold=threshold)
            df["tokens"] = bigrams_list

        # 4. Re-join tokens into 'clean_text' for final display/analysis
        df["clean_text"] = df["tokens"].apply(lambda x: " ".join(x))

        # Filter out empty strings in 'clean_text'
        df = df[df["clean_text"].str.strip() != ""]

        logging.info(f"Preprocessed {len(df)} comments successfully.")
        return df[["text", "clean_text", "tokens"]]

    except Exception as e:
        logging.error(f"Error preprocessing comments: {e}", exc_info=True)
        return pd.DataFrame()
