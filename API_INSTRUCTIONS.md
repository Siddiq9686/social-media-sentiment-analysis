# Social Media Sentiment Analysis API Instructions

## Overview
This document provides instructions for setting up and running the Twitter Sentiment Analysis API, which connects the sentiment analysis model to the web interface.

## Prerequisites
- Python 3.7 or higher
- Required Python packages (install using `pip install -r api_requirements.txt`)

## Setup Instructions

1. **Install Dependencies**
   ```
   pip install -r api_requirements.txt
   ```

2. **Run the API Server**
   ```
   python api.py
   ```
   This will start the Flask API server on http://127.0.0.1:8001

3. **Run the Web Interface**
   ```
   python -m http.server 8010
   ```
   This will serve the web interface on http://127.0.0.1:8010

4. **Access the Application**
   Open your browser and navigate to http://127.0.0.1:8010/index.html

## API Endpoints

### Analyze Sentiment
- **URL**: `/api/analyze`
- **Method**: POST
- **Request Body** (either key is accepted):
  ```json
  {
    "text": "Your post text here"
  }
  ```
  or
  ```json
  {
    "tweet": "Your post text here"
  }
  ```
- **Response**:
  ```json
  {
    "sentiment": "positive",
    "scores": {
      "positive": 75,
      "negative": 10,
      "neutral": 10,
      "irrelevant": 5
    }
  }
  ```

## How It Works

1. The API uses a pre-trained Logistic Regression model to analyze the sentiment of posts.
2. If the model doesn't exist, it will automatically train a new model using the training data.
3. The web interface sends the post text to the API and displays the results.
4. If the API is not available, the web interface will fall back to demo mode with simulated results.

## Troubleshooting

- If you see a warning about using demo mode, make sure the API server is running on port 8001.
- If the model training fails, check that the training data file (`text.csv`) is in the correct location.
- For CORS issues, ensure that both servers are running on the specified ports (API on 8001, web interface on 8010).

## Extending the API

To improve the API, consider:

1. Adding authentication for secure access
2. Implementing rate limiting to prevent abuse
3. Adding more endpoints for batch processing or model retraining
4. Deploying to a production server with proper error handling and logging