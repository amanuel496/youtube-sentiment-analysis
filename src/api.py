from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from main import run_etl_pipeline
import asyncio

app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/run-etl")
async def run_etl(videoId: str, outputFormat: str = 'json'):
    """API endpoint to trigger the ETL pipeline."""
    try:
        await run_etl_pipeline(videoId, outputFormat)
        return {
            "message": "ETL pipeline completed successfully.",
            "filePath": f"comments_{videoId}.{outputFormat}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
