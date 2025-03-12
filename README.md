# Automated YouTube Comment Sentiment Analysis with AWS

## Overview
This project builds a fully automated ETL pipeline that extracts comments from YouTube videos, processes and analyzes sentiment using Amazon Comprehend, and presents insights through a public-facing website. The pipeline utilizes FastAPI, React for the frontend, and AWS services for sentiment analysis.

## Project Scope & Goals
1. **Data Extraction**: Scrape comments from YouTube videos using the YouTube Data API.
2. **Data Preprocessing**: Clean and transform data using custom preprocessing scripts.
3. **Sentiment Analysis**: Use AWS Comprehend for text classification.
4. **Data Storage**: Store raw and processed data in local files (JSON/CSV) or in the cloud (optional).
5. **Automation & Scalability**: Implement FastAPI as a backend server with an interactive frontend using React.
6. **Additional Features**:
   - Subscription-based notifications for new comments.
   - Like-to-dislike ratio estimation.

## Technology Stack
- **Frontend**: React, Tailwind CSS
- **Backend**: FastAPI
- **Data Processing**: Custom Python scripts
- **Sentiment Analysis**: Amazon Comprehend
- **Storage**: Local files (JSON/CSV) or AWS S3 (optional)
- **Notifications**: AWS SES (for subscription-based notifications)

## Setup Instructions
1. Clone the repository
```bash
git clone https://github.com/amanuel496/youtube-sentiment-analysis.git
cd youtube-sentiment-analysis
```

2. Install dependencies for both backend and frontend
```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

3. Set up environment variables
Create a `.env` file and add your API keys and AWS credentials:
```env
YOUTUBE_API_KEY=your_youtube_api_key
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=your_aws_region
```

4. Run the development servers
```bash
# Backend server
uvicorn src.api:app --reload

# Frontend server
cd frontend
npm run dev
```

5. Test the end-to-end pipeline
- Submit a YouTube link through the web app
- Verify data flow from extraction to sentiment analysis

## Next Steps
- Finalize website UI and improve user experience.
- Conduct performance testing and deploy the project.
- Gather user feedback and iterate based on insights.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.
