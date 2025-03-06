import pytest
from unittest import mock
from src.extraction.fetch_comments import get_detailed_comments
import logging

# Configure logging for test output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Mock data for testing
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

@pytest.mark.asyncio
async def test_get_detailed_comments(monkeypatch) -> None:
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
async def test_get_detailed_comments_pagination(monkeypatch, max_results: int, expected_count: int) -> None:
    """Test pagination logic in fetching comments."""
    async def mock_fetch_comments_page(session, video_id, page_token=None):
        return {'items': [{'snippet': {'topLevelComment': {'snippet': comment}}} for comment in MOCK_COMMENTS[:max_results]]}

    with mock.patch('src.extraction.fetch_comments.fetch_comments_page', mock_fetch_comments_page):
        comments = await get_detailed_comments('mock_video_id', max_results=max_results)
        assert len(comments) == expected_count
