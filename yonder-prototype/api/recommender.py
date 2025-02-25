import json
import openai
from .models import User, Experience
from typing import List, Dict
from dotenv import load_dotenv
import os

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
You are an AI designed to recommend personalized experiences based on a user's profile, past experiences, and spending habits.

## Step 1: Create an Experience Persona
Based on the user's previous redemptions and spending habits, create:
1. **Experience Persona Name**: A catchy label summarizing the user's preferences (e.g., "Adventurous Traveler").
2. **Persona Description**: A detailed, human-like summary of the user's lifestyle, interests, and spending habits.

{user_profile}

{experience_list}

## Step 2: Experience Ranking and Recommendations
Rank each available experience out of 10 using the following criteria:
- **Relevance (50%)**: How well does this experience align with the user's past activities and interests?
- **Novelty (30%)**: How exciting or new is this experience for the user?
- **Diversity (20%)**: How well does this experience expand the user's interests without overwhelming them?

Provide a score for each category and calculate a final score for each experience, sorting the experiences from highest to lowest score. Recommend the top 3 experiences.

Additionally, explain how each experience was ranked based on the user's persona and preferences.

## Step 3: Serendipity Pick
Recommend one **Serendipity Pick**: an experience that the user is unlikely to try based on their past behaviors, but could align well with their persona profile. Explain why this experience fits the user and how it could be a surprising hit. It should introduce something new and unexpected but still offer value or joy that fits with their lifestyle.

## Step 4: Ranking Breakdown
Provide detailed rankings using the following methodology:
1. **Relevance** → Prioritize experiences closely related to the user's known interests (e.g., food, travel, culture).
2. **Novelty** → Include experiences that are new or slightly outside the user's usual activities to encourage discovery.
3. **Diversity** → Ensure a balance of categories, such as mixing low and high-cost experiences, different locations, and various types of activities.

## Step 5: Format the Response
Return the recommendations in a clear, structured format:
```
Experience Persona: [Persona Name] 
Persona Description: [Detailed description summarizing the user's interests, lifestyle, and spending habits]

Top 3 Recommendations:
[Experience Title] (Score: X/10): Explanation of why this experience was ranked high, including relevance, novelty, and diversity breakdown.
[Experience Title] (Score: X/10): Explanation of why this experience fits the user, with scoring breakdown.
[Experience Title] (Score: X/10): Explanation of why this experience adds diversity to the user's profile, with scoring breakdown.

Serendipity Pick:
[Experience Title]: Explanation of why this experience is outside the user’s usual preferences but could be a surprising and valuable addition to their life.
```
Ensure that each explanation includes how the ranking was influenced by the user's profile, interests, and lifestyle preferences.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content.strip().replace("\n", "<br>")

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