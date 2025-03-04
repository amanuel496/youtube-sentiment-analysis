# Test cases for fetch_comments and file_saver modules

import pytest
from unittest import mock
from src.extraction.fetch_comments import get_detailed_comments
from src.extraction.file_saver import save_comments_to_files
import json
import pandas as pd
import logging

# Configure logging for test output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Mock data
MOCK_COMMENTS = [
    {
        'textDisplay': 'Great video!',
        'authorDisplayName': 'User1',
        'likeCount': 10,
        'publishedAt': '2023-01-01T00:00:00Z'
    },
    {
        'textDisplay': 'Very informative.',
        'authorDisplayName': 'User2',
        'likeCount': 5,
        'publishedAt': '2023-01-02T00:00:00Z'
    }
]

# Test for the comment_fetcher module
@pytest.mark.asyncio
async def test_get_detailed_comments(monkeypatch):
    """Test fetching comments from a video ID."""
    async def mock_fetch_comments_page(session, video_id, page_token=None):
        return {'items': [{'snippet': {'topLevelComment': {'snippet': MOCK_COMMENTS[0]}}}]}

    with mock.patch('src.extraction.fetch_comments.fetch_comments_page', mock_fetch_comments_page):
        comments = await get_detailed_comments('mock_video_id', max_results=1)
        assert len(comments) == 1
        assert comments[0]['text'] == 'Great video!'
        assert comments[0]['author'] == 'User1'
        assert comments[0]['likes'] == 10
        assert comments[0]['published_at'] == '2023-01-01T00:00:00Z'

@pytest.mark.parametrize("max_results, expected_count", [(1, 1), (2, 2), (10, 2)])
@pytest.mark.asyncio
async def test_get_detailed_comments_pagination(monkeypatch, max_results, expected_count):
    """Test pagination logic in fetching comments."""
    async def mock_fetch_comments_page(session, video_id, page_token=None):
        return {'items': [{'snippet': {'topLevelComment': {'snippet': comment}}} for comment in MOCK_COMMENTS[:max_results]]}

    with mock.patch('src.extraction.fetch_comments.fetch_comments_page', mock_fetch_comments_page):
        comments = await get_detailed_comments('mock_video_id', max_results=max_results)
        assert len(comments) == expected_count

# Test for the file_saver module
def test_save_comments_to_files(tmp_path):
    """Test saving comments to JSON and CSV files."""
    json_filename = tmp_path / 'comments.json'
    csv_filename = tmp_path / 'comments.csv'

    save_comments_to_files(MOCK_COMMENTS, json_filename=str(json_filename), csv_filename=str(csv_filename))

    # Check JSON file
    assert json_filename.exists()
    with open(json_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
        assert len(data) == 2
        assert data[0]['textDisplay'] == 'Great video!'
        assert data[1]['textDisplay'] == 'Very informative.'

    # Check CSV file
    assert csv_filename.exists()
    df = pd.read_csv(csv_filename)
    assert len(df) == 2
    assert df.iloc[0]['textDisplay'] == 'Great video!'
    assert df.iloc[1]['textDisplay'] == 'Very informative.'

# Test for logging in file_saver module
def test_logging_in_file_saver(tmp_path):
    """Test that logging is called when saving files."""
    json_filename = tmp_path / 'comments.json'
    csv_filename = tmp_path / 'comments.csv'

    with mock.patch('logging.info') as mock_logging:
        save_comments_to_files(MOCK_COMMENTS, json_filename=str(json_filename), csv_filename=str(csv_filename))
        mock_logging.assert_called_with(f"Comments saved to {json_filename} and {csv_filename}")