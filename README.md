# Automated YouTube Comment Sentiment Analysis with AWS

## Overview
This project aims to build a fully automated ETL pipeline that extracts comments from YouTube videos, processes and analyzes sentiment, and presents insights through a public-facing website. AWS services will be used for cloud storage, event-driven processing, and visualization.

## Project Scope & Goals
1. **Data Extraction**: Scrape comments from YouTube videos using the YouTube Data API.
2. **Data Storage**: Store raw and processed data in Amazon S3.
3. **Data Preprocessing**: Clean and transform data using AWS Lambda.
4. **Sentiment Analysis**: Use AWS Comprehend for text classification.
5. **Data Visualization**: Present insights using Amazon QuickSight or a custom web dashboard.
6. **Automation & Scalability**: Implement AWS Lambda & API Gateway for event-driven processes.
7. **Additional Features**:
   - Subscription-based notifications for new comments.
   - Like-to-dislike ratio estimation.

## Technology Stack
- **Frontend**: HTML/CSS, React or Angular
- **Backend**: AWS Lambda, API Gateway, Flask (for web interface)
- **Data Processing**: AWS Lambda, Amazon Comprehend
- **Storage**: Amazon S3, DynamoDB
- **Visualization**: Amazon QuickSight, Custom Dashboard
- **Notifications**: Amazon SES

## Setup Instructions
1. Clone the repository
```bash
git clone https://github.com/amanuel496/youtube-sentiment-analysis.git
cd youtube-sentiment-analysis
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up environment variables
Create a `.env` file and add your API keys and AWS credentials:
```env
YOUTUBE_API_KEY=your_youtube_api_key
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
S3_BUCKET_NAME=your_s3_bucket_name
```

4. Run the data extraction script
```bash
python src/extraction/fetch_comments.py
```

5. Deploy Lambda functions
- Zip the function code
- Upload to AWS Lambda
- Configure triggers and permissions

6. Test the pipeline
- Submit a YouTube link through the web app
- Verify data flow from extraction to visualization

## Next Steps
- Finalize website UI and improve user experience.
- Conduct performance testing and deploy the project.
- Gather user feedback and iterate based on insights.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.