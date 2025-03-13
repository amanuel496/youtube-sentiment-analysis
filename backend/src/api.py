from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from src.main import run_etl_pipeline, extract_video_id
import asyncio
import logging

app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/run-etl")
async def run_etl(videoLink: str = Query(..., title="YouTube Video Link"), outputFormat: str = "json"):
    """API endpoint to trigger the ETL pipeline."""
    
    logging.info(f"Received videoLink: {videoLink}")

    # Extract video ID
    video_id = extract_video_id(videoLink)
    if not video_id:
        logging.error("Invalid video link provided.")
        return {"status": "Invalid video link"}

    try:
        # Run the ETL pipeline
        result = await run_etl_pipeline(video_id, outputFormat)  # Now returning a dictionary
        logging.info(f"ETL Pipeline Response: {result}")

        return result  # ✅ Directly return the dictionary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
