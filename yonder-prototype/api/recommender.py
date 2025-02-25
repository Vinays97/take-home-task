import json
import openai
from .models import User, Experience
from typing import List, Dict
from dotenv import load_dotenv
import os

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# Preprocess user data

def preprocess_user_data(user_data: Dict):
    return {
        "member_id": user_data["member_id"],
        "name": user_data["name"],
        "location": user_data["location"],
        "past_redeemed_offers": user_data["past_redeemed_offers"],
        "card_transactions": user_data["card_transactions"]
    }

# Preprocess experience data

def preprocess_experience_data(experiences_data: List[Dict]):
    return [
        {
            "experience_id": exp["experience_id"],
            "title": exp["title"],
            "category": exp["category"],
            "short_description": exp["short_description"],
            "location": exp["location"],
            "price_range": exp["price_range"],
            "rating": exp["rating"]
        }
        for exp in experiences_data
    ]

# Load data

def load_data():
    with open("yonder-prototype/data/input.json", "r") as f:
        data = json.load(f)
    users = data["members"]
    experiences = data["experiences"]
    return users, experiences

# Get recommendations

def get_recommendations(user: User, experiences: List[Experience]) -> str:
    """Generates personalized recommendations using GPT-4o."""
    
    # Create structured prompt for GPT-4o
    prompt = f"""
    You are an AI recommendation assistant providing experience suggestions.
    
    ## User Profile:
    - Name: {user.name}
    - Location: {user.location}
    - Spending Categories: {", ".join(user.spending_habits)}
    - Past Experiences: {", ".join(user.past_experiences) if user.past_experiences else "None"}
    
    ## Available Experiences:
    Below is a list of experiences. Recommend the top 3 most suitable options based on the user's location, preferences, and spending habits:
    
    {chr(10).join([f"- {exp.title} ({exp.category}, {exp.location}): {exp.description} [Price: {exp.price_range}, Rating: {exp.rating}]" for exp in experiences])}
    
    ## Recommendation Criteria:
    1. **Relevance**: Experiences that match the user's persona, past activities, and spending habits.
    2. **Novelty**: At least one new category they haven't explored before.
    3. **Diversity**: Suggestions should be from different price ranges and experience types.
    
    Provide recommendations in the format:
    - [Experience Title]: Short reason why this matches the user.
    """

    response = openai.Completion.create(
        engine="gpt-4o",
        prompt=prompt,
        max_tokens=200,
        temperature=0.7
    )

    recommendations = response.choices[0].text.strip()
    return recommendations
