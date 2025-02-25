# Yonder AI Recommendation System Prototype

# Overview
This project is a prototype for a recommendation system for Yonder. It consists of several modules that work together to provide personalised experience recommendations based on user data.

# Modules
1. **main.py**: This is the entry point of the FastAPI application. It defines the API endpoints and handles requests related to users and experiences.
2. **models.py**: This module defines the data models for users, experiences, past redeemed offers, and card transactions using Pydantic.
3. **recommender.py**: This module contains the logic for generating personalised recommendations. It loads user and experience data, processes user information, and interacts with the OpenAI API to generate recommendations.
4. **input.json**: This file contains sample data for users and experiences, which is used by the recommender system.
5. **users.html**: This is a Jinja2 template used to render the list of users and experiences in the web interface.

# API Endpoints
- `GET /health` – API health check
- `GET /users` – List all users
- `GET /users/{member_id}` – Get details of a specific user
- `GET /experiences` – List all experiences
- `GET /experiences/{experience_id}` – Get details of a specific experience
- `GET /recommendations/{user_id}` – Get recommendations for a specific user

# Prerequisites
- Python 3.8+
- pip (Python package installer)

# Setup
Clone the repository and install dependencies.
 git clone <repo_url>
 cd yonder-prototype
 pip install -r requirements.txt

### Environment Variables
In the `.env` file in the root directory and add your OpenAI API key:
OPENAI_API_KEY="your_openai_api_key"

### Running the API
In the terminal enter the following command:
 uvicorn yonder-prototype.api.main:app --reload

Open a web browser and navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000) to see the app running.