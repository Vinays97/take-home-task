import json
import openai
from .models import User, Experience
from typing import List, Dict
from dotenv import load_dotenv
import os

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#openai.api_key = os.getenv("OPENAI_API_KEY")

# Load data

def load_data():
    with open(os.path.join(os.path.dirname(__file__), '../data/input.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)
    users = data['members']
    experiences = data['experiences']
    return users, experiences

# Get user info

def get_user_info(user_id: str) -> Dict:
    users, experiences = load_data()
    user_data = next((u for u in users if u["member_id"] == user_id), None)
    if not user_data:
        return {}
    user = User(**user_data)
    user_info = {
        "user": user,
        "experiences": experiences,
        "redeemed_experiences": [exp for exp in experiences if exp["experience_id"] in [offer.experience_id for offer in user.past_redeemed_offers]]
    }
    return user_info

def generate_recommendations(user_data: Dict) -> str:
    user = user_data['user']
    redeemed_details = user_data['redeemed_details']
    not_redeemed_details = user_data['not_redeemed_details']

    user_profile = f"""## User Profile
- **Name:** {user.name}
- **Location:** {user.location}

### Past Experiences (Redeemed Offers)
"""
    for exp in redeemed_details:
        redeemed_offer = next((offer for offer in user.past_redeemed_offers if offer.experience_id == exp['experience_id']), None)
        if redeemed_offer:
            user_profile += f"- **{exp['title']} ({exp['category']}, {exp['location']}, {exp['price_range']})** – Attended on {redeemed_offer.redeemed_date}\n"
        user_profile += f"  *Description:* {exp['long_description']}\n\n"

    user_profile += "### Spending Habits (Recent Transactions)\n"
    for txn in user.card_transactions:
        user_profile += f"- **{txn.category}:** £{txn.amount} spent at **{txn.merchant_name}** ({txn.date})\n"

    experience_list = "### Available Experiences (Not Yet Redeemed)\n"
    for exp in not_redeemed_details:
        experience_list += f"""- **{exp['title']}** ({exp['category']}, {exp['location']}, {exp['price_range']})  
  *Description:* {exp['long_description']}\n\n"""
        
    prompt = f"""
You are an AI specializing in personalized experience recommendations. Your task is to analyze a user's past experiences, spending habits, and lifestyle preferences to generate the best new experiences for them.

## Step 1: Create an Experience Persona
Based on the user’s previous redemptions and spending habits, create:
1. **Experience Persona Name** → A short, catchy label that defines the user’s preferences (e.g., “Cultural Foodie”).
2. **Persona Description** → A detailed, human-like description summarizing their lifestyle, interests, and spending habits.

{user_profile}

{experience_list}

## Step 2: Recommend New Experiences
Recommend the top 3 experiences based on relevance, novelty, and diversity.

## Step 3: Ranking Criteria
1. **Relevance** → Prioritize experiences matching the user’s interests (e.g., food, lifestyle, or cultural events).
2. **Novelty** → Introduce at least one experience outside their comfort zone.
3. **Diversity** → Ensure variety in category and price range.

## Step 4: Format the Response
Return the response in structured format like this:
```
**Experience Persona:** [Persona Name]
**Persona Description:** [Detailed description summarizing interests, habits, and spending behavior]

**Recommended Experiences:**
- [Experience Title]: Short explanation of why this matches the user.
```
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content.strip()

def get_recommendations(user_id: str) -> str:
    user_info = get_user_info(user_id)
    if not user_info:
        return "User not found"
    user = user_info["user"]
    redeemed_experiences = user_info["redeemed_experiences"]
    redeemed_details = [{
        "experience_id": exp["experience_id"],
        "title": exp["title"],
        "category": exp["category"],
        "location": exp["location"],
        "price_range": exp["price_range"],
        "long_description": exp["long_description"]
    } for exp in redeemed_experiences]
    not_redeemed_details = [{
        "experience_id": exp["experience_id"],
        "title": exp["title"],
        "category": exp["category"],
        "location": exp["location"],
        "price_range": exp["price_range"],
        "long_description": exp["long_description"]
    } for exp in user_info["experiences"] if exp not in redeemed_experiences]

    user_data = {
        "user": user,
        "redeemed_details": redeemed_details,
        "not_redeemed_details": not_redeemed_details
    }

    return generate_recommendations(user_data)
    #return user_data