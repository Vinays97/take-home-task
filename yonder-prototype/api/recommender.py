import json
import openai
from .models import User, Experience
from typing import List
from dotenv import load_dotenv
import os

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def load_data():
    with open("data/users.json", "r") as f:
        users = json.load(f)
    with open("data/experiences.json", "r") as f:
        experiences = json.load(f)
    return users, experiences


def get_recommendations(user: User, experiences: List[Experience]):
    prompt = f"Generate personalized recommendations for user {user.name} based on their past experiences and transactions."
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    recommendations = response.choices[0].text.strip()
    return recommendations
