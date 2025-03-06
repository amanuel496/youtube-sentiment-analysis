import pytest
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

# Test the API with a valid YouTube video ID
def test_run_etl_success(mocker):
    """Test the /run-etl endpoint with a valid request."""
    # Mock the run_etl_pipeline function to avoid triggering the actual ETL
    mocker.patch("src.api.run_etl_pipeline", return_value=None)

    response = client.get("/run-etl", params={"videoId": "test_video_id", "outputFormat": "json"})
    
    assert response.status_code == 200
    assert response.json() == {
        "message": "ETL pipeline completed successfully.",
        "filePath": "comments_test_video_id.json"
    }

# Test the API with a missing YouTube video ID
def test_run_etl_missing_video_id():
    """Test the /run-etl endpoint with a missing video ID."""
    response = client.get("/run-etl", params={"outputFormat": "json"})
    
    assert response.status_code == 422  # Unprocessable Entity (Missing required parameter)

# # Test the API with an invalid output format
# def test_run_etl_invalid_output_format(mocker):
#     """Test the /run-etl endpoint with an invalid output format."""
#     mocker.patch("src.api.run_etl_pipeline", return_value=None)

#     response = client.get("/run-etl", params={"videoId": "test_video_id", "outputFormat": "invalid"})
    
#     assert response.status_code == 500
#     assert "Unsupported output format" in response.json()["detail"]

# Test the API when an internal error occurs
def test_run_etl_internal_error(mocker):
    """Test the /run-etl endpoint when an internal error is raised."""
    # Simulate an internal error in the ETL pipeline
    mocker.patch("src.api.run_etl_pipeline", side_effect=Exception("Internal Error"))

    response = client.get("/run-etl", params={"videoId": "test_video_id", "outputFormat": "json"})
    
    assert response.status_code == 500
    assert "Internal Error" in response.json()["detail"]
