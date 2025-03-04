import pytest
import pandas as pd
from src.preprocessing.preprocessing import clean_text, preprocess_comments

# Mock data for testing
MOCK_COMMENTS = [
    {'text': 'Great video! Visit https://example.com for more info.'},
    {'text': '<p>This is <b>bold</b> text</p>'},
    {'text': 'Contact us at info@example.com!'},
    {'text': '    Lots of whitespace   '},
    {'text': ''},  # Empty comment
    {'text': None},  # None comment
    {'text': 'Special characters #@$&*(!'},
]

# Updated expected clean results
EXPECTED_CLEAN_TEXTS = [
    'great video visit info',
    'this is bold text',
    'contact us at info examplecom',
    'lots of whitespace',
    '',  # Empty comment
    '',  # None comment
    'special characters'
]

# Test the clean_text function
@pytest.mark.parametrize("input_text, expected", zip([comment['text'] for comment in MOCK_COMMENTS], EXPECTED_CLEAN_TEXTS))
def test_clean_text(input_text, expected):
    """Test the clean_text function with various inputs."""
    assert clean_text(input_text) == expected

# Test the preprocess_comments function
def test_preprocess_comments():
    """Test the preprocessing of comments and cleaning functionality."""
    df = preprocess_comments(MOCK_COMMENTS)
    assert isinstance(df, pd.DataFrame)
    assert 'clean_text' in df.columns
    assert len(df) == len([text for text in EXPECTED_CLEAN_TEXTS if text])  # Ensure empty comments are dropped
    assert df['clean_text'].tolist() == [text for text in EXPECTED_CLEAN_TEXTS if text]

# Run tests with pytest
# pytest -v test_preprocessing.py

