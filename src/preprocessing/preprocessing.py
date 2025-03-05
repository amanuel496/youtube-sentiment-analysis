import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from typing import List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize lemmatizer and stop words
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# Whitelist to avoid over-lemmatization
whitelist = {'this', 'is', 'us', 'at', 'lots', 'characters', 'of'}


def clean_text(text: pd.Series) -> pd.Series:
    """Cleans and normalizes the input text using vectorized methods."""
    try:
        logging.debug("Starting vectorized text cleaning")

        # Convert to lowercase and handle non-string values safely
        text = text.fillna('').astype(str).str.lower()

        # Remove URLs
        text = text.str.replace(r'http\S+|www\.\S+', '', regex=True)

        # Remove HTML tags
        text = text.str.replace(r'<.*?>', '', regex=True)

        # Handle email addresses specifically (remove special characters but avoid extra spaces)
        text = text.str.replace(r'(\S+)@(\S+)\.(\S+)', r'\1 \2\3', regex=True)

        # Replace remaining special characters with a space
        text = text.str.replace(r'[^a-zA-Z\s]', ' ', regex=True)

        # Remove extra whitespace
        text = text.str.replace(r'\s+', ' ', regex=True).str.strip()

        # Remove stop words and apply lemmatization
        text = text.apply(lambda x: ' '.join([
            word if word in whitelist else lemmatizer.lemmatize(word)
            for word in x.split() if word in whitelist or word not in stop_words
        ]))

        logging.debug("Vectorized text cleaning completed")
        return text

    except Exception as e:
        logging.error(f"Error during vectorized text cleaning: {e}", exc_info=True)
        return pd.Series()


def preprocess_comments(comments: List[Dict[str, str]]) -> pd.DataFrame:
    """Preprocesses a list of comments by cleaning and preparing them for analysis using vectorized methods."""
    try:
        # Create a DataFrame from comments
        df = pd.DataFrame(comments)

        # Ensure 'text' column exists
        if 'text' not in df.columns:
            logging.error("The 'text' column is missing from the input data.")
            return pd.DataFrame()

        # Clean the 'text' column using vectorized methods
        df['clean_text'] = clean_text(df['text'])

        # Remove rows where 'clean_text' is empty after cleaning
        df = df[df['clean_text'].str.strip() != '']

        logging.info(f"Preprocessed {len(df)} comments using vectorized methods.")
        return df

    except Exception as e:
        logging.error(f"Error preprocessing comments: {e}", exc_info=True)
        return pd.DataFrame()
