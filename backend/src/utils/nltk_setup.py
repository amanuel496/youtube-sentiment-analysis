import nltk
import os

# Define the path to the NLTK data directory
NLTK_DATA_DIR = '/tmp/nltk_data'
nltk.data.path.append(NLTK_DATA_DIR)

# List of required NLTK resources
REQUIRED_RESOURCES = ['stopwords', 'wordnet']

def download_nltk_resources():
    """Downloads necessary NLTK resources if not already present."""
    for resource in REQUIRED_RESOURCES:
        try:
            nltk.data.find(f'corpora/{resource}')
        except LookupError:
            print(f"Downloading NLTK resource: {resource}")
            nltk.download(resource, download_dir=NLTK_DATA_DIR)

# Run the download function when the module is imported
download_nltk_resources()
