import pytest
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

def test_run_etl_success(mocker) -> None:
    """Test the /run-etl endpoint with a valid request."""
    mocker.patch("src.api.run_etl_pipeline", return_value=None)

    response = client.get("/run-etl", params={"videoId": "test_video_id", "outputFormat": "json"})
    
    assert response.status_code == 200
    assert response.json() == {
        "message": "ETL pipeline completed successfully.",
        "filePath": "comments_test_video_id.json"
    }

def test_run_etl_missing_video_id() -> None:
    """Test the /run-etl endpoint with a missing video ID."""
    response = client.get("/run-etl", params={"outputFormat": "json"})
    assert response.status_code == 422

def test_run_etl_internal_error(mocker) -> None:
    """Test the /run-etl endpoint when an internal error is raised."""
    mocker.patch("src.api.run_etl_pipeline", side_effect=Exception("Internal Error"))

    response = client.get("/run-etl", params={"videoId": "test_video_id", "outputFormat": "json"})
    
    assert response.status_code == 500
    assert "Internal Error" in response.json()["detail"]
