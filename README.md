# Yonder AI Recommendation System Prototype

## Setup
Clone the repository and install dependencies.
git clone <repo_url>
cd yonder-prototype
pip install -r requirements.txt

## Running the API
uvicorn api.main:app --reload

## Environment Variables
OPENAI_API_KEY=your_api_key_here

## API Endpoints
- GET /recommendations/{user_id} – Fetch personalized experiences
- POST /reload-data – Reload JSON dataset
- GET /health – API health check
