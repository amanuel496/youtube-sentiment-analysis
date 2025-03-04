import re
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


def clean_text(text: str) -> str:
    """Cleans and normalizes the input text."""
    try:
        if not isinstance(text, str) or text is None:
            logging.warning(f"Input is not a valid string: {text}")
            return ''

        # Convert to lowercase
        text = text.lower()

        # Remove URLs
        text = re.sub(r'http\S+|www\.\S+', '', text)

        # Remove HTML tags
        text = re.sub(r'<.*?>', '', text)

        # Handle email addresses specifically (remove special characters but avoid extra spaces)
        text = re.sub(r'(\S+)@(\S+)\.(\S+)', r'\1 \2\3', text)

        # Replace remaining special characters with a space
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # Remove stop words and apply lemmatization
        cleaned_text = []
        for word in text.split():
            if word in whitelist or word not in stop_words:
                cleaned_text.append(word if word in whitelist else lemmatizer.lemmatize(word))

        return ' '.join(cleaned_text)

    except Exception as e:
        logging.error(f"Error cleaning text: {e}", exc_info=True)
        return ''


def preprocess_comments(comments: List[Dict[str, str]]) -> pd.DataFrame:
    """Preprocesses a list of comments by cleaning and preparing them for analysis."""
    try:
        # Create a DataFrame from comments
        df = pd.DataFrame(comments)

        # Clean the 'text' column
        df['clean_text'] = df['text'].apply(clean_text)

        # Drop empty comments
        df = df[df['clean_text'].str.strip() != '']

        logging.info(f"Preprocessed {len(df)} comments.")
        return df

    except Exception as e:
        logging.error(f"Error preprocessing comments: {e}", exc_info=True)
        return pd.DataFrame()
