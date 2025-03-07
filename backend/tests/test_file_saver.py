import json
import pandas as pd
import pytest
from pathlib import Path
from src.utils.file_saver import save_to_json, save_to_csv

# Define test file paths
BASE_PATH = Path(__file__).parent / 'data'
BASE_PATH.mkdir(parents=True, exist_ok=True)
JSON_FILE = BASE_PATH / 'test_comments.json'
CSV_FILE = BASE_PATH / 'test_comments.csv'

# Mock data for testing
MOCK_DATA = ["comment1", "comment2", "comment3"]
MOCK_DF = pd.DataFrame({"clean_text": MOCK_DATA})

@pytest.fixture(scope='module', autouse=True)
def setup_and_teardown() -> None:
    """Setup and teardown for file tests."""
    BASE_PATH.mkdir(parents=True, exist_ok=True)
    yield
    for file in [JSON_FILE, CSV_FILE]:
        if file.exists():
            file.unlink()

def test_save_to_json() -> None:
    """Test saving data to a JSON file."""
    save_to_json(MOCK_DATA, 'test_comments.json')
    assert JSON_FILE.exists()

    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        assert MOCK_DATA == data

def test_save_to_csv() -> None:
    """Test saving data to a CSV file."""
    save_to_csv(MOCK_DF, 'test_comments.csv')
    assert CSV_FILE.exists()

    df = pd.read_csv(CSV_FILE)
    assert 'comment1' in df['clean_text'].values
