import asyncio
import pytest
import pandas as pd
from unittest.mock import patch, AsyncMock
from src.main import run_etl_pipeline
from pathlib import Path

# Define test file paths
BASE_PATH = Path.cwd() / 'data'
JSON_FILE = BASE_PATH / 'comments_test.json'
CSV_FILE = BASE_PATH / 'comments_test.csv'

# Mock data
MOCK_COMMENTS = ['Great video!', 'Nice content!', 'Very helpful!']
MOCK_PREPROCESSED = pd.DataFrame({'clean_text': ['great video', 'nice content', 'very helpful']})

@pytest.fixture(scope='module', autouse=True)
def setup_and_teardown():
    """Setup and teardown for the main ETL pipeline tests."""
    # Ensure the base directory exists
    BASE_PATH.mkdir(parents=True, exist_ok=True)
    yield
    # Cleanup test files after all tests run
    for file in [JSON_FILE, CSV_FILE]:
        if file.exists():
            file.unlink()

@pytest.mark.asyncio
@patch('src.main.get_detailed_comments', new_callable=AsyncMock)
@patch('src.main.preprocess_comments', return_value=MOCK_PREPROCESSED)
def test_etl_pipeline_json(mock_preprocess, mock_get_comments):
    """Test the full ETL pipeline with JSON output."""
    mock_get_comments.return_value = MOCK_COMMENTS
    video_id = 'test'
    output_format = 'json'
    
    # Run the ETL pipeline
    asyncio.run(run_etl_pipeline(video_id, output_format))
    
    # Check if the JSON file is created
    assert JSON_FILE.exists()
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = f.read()
        assert 'great video' in data

@pytest.mark.asyncio
@patch('src.main.get_detailed_comments', new_callable=AsyncMock)
@patch('src.main.preprocess_comments', return_value=MOCK_PREPROCESSED)
def test_etl_pipeline_csv(mock_preprocess, mock_get_comments):
    """Test the full ETL pipeline with CSV output."""
    mock_get_comments.return_value = MOCK_COMMENTS
    video_id = 'test'
    output_format = 'csv'
    
    # Run the ETL pipeline
    asyncio.run(run_etl_pipeline(video_id, output_format))
    
    # Check if the CSV file is created
    assert CSV_FILE.exists()
    df = pd.read_csv(CSV_FILE)
    assert 'great video' in df['clean_text'].values
