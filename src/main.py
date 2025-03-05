import logging
from src.extraction.fetch_comments import get_detailed_comments
from src.utils.file_saver import save_to_csv, save_to_json
from src.preprocessing.preprocessing import preprocess_comments


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


import asyncio

async def run_etl_pipeline(video_id: str, output_format: str = 'json') -> None:
    """Executes the ETL pipeline for YouTube comment sentiment analysis."""
    try:
        logging.info(f"Starting ETL pipeline for video ID: {video_id}")
        
        # Step 1: Extract - Fetch comments from the YouTube video
        comments = await get_detailed_comments(video_id)
        if not comments:
            logging.warning(f"No comments found for video ID: {video_id}")
            return
        
        # Step 2: Transform - Preprocess the fetched comments
        preprocessed_comments = preprocess_comments([{'text': comment} for comment in comments])
        if preprocessed_comments.empty:
            logging.warning("No valid comments to preprocess.")
            return
        
        # Step 3: Load - Save the preprocessed comments to a file
        output_filename = f"comments_{video_id}.{output_format}"
        if output_format == 'json':
            save_to_json(preprocessed_comments['clean_text'].tolist(), output_filename)
        elif output_format == 'csv':
            save_to_csv(preprocessed_comments, output_filename)
        else:
            logging.error(f"Unsupported output format: {output_format}")
            return
        
        logging.info(f"ETL pipeline completed successfully. Output saved to {output_filename}")

    except Exception as e:
        logging.error(f"Error during ETL pipeline execution: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    video_id = input("Enter YouTube video ID: ")
    output_format = input("Enter output format (json/csv): ").lower()
    asyncio.run(run_etl_pipeline(video_id, output_format))