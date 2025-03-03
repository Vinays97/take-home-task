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
            user_profile += f"- **{exp['title']} ({exp['category']}, {exp['location']}, {exp['price_range']})** - Attended on {redeemed_offer.redeemed_date}\n"
        user_profile += f"*Description:* {exp['long_description']}\n\n"

    user_profile += "### Spending Habits (Recent Transactions)\n"
    for txn in user.card_transactions:
        user_profile += f"- **{txn.category}:** £{txn.amount} spent at **{txn.merchant_name}** ({txn.date})\n"

    experience_list = "### Available Experiences (Not Yet Redeemed)\n"
    for exp in not_redeemed_details:
        experience_list += f"""- **{exp['title']}** ({exp['category']}, {exp['location']}, {exp['price_range']})  
        *Description:* {exp['long_description']}\n\n"""
        
    prompt = f"""
    You are an AI designed to recommend personalized experiences based on a user's profile, past experiences, and spending habits. Your goal is to provide relevant, novel, and diverse recommendations, including a "Serendipity Pick" that might surprise and delight the user. **You must base your recommendations *solely* on the information provided below. Do not invent or assume any additional details about the user.**

    ## Explanation of Few-Shot Example (Internal Note)

    The following section provides a "few-shot" example. This demonstrates the expected input and output format, and illustrates how to apply the instructions to a sample user profile. Study this example carefully to understand the task's requirements, including the structure of the response, the scoring system, and the reasoning behind the recommendations. This example will help you generalize to new user profiles.

    These examples are illustrations of the task. Your recommendations for the user must be based *entirely* on the user's profile, not on similarities to Sarah or James' profile.

    ## Example Input and Output (Illustrative) - Example 1

    **Example User Profile:**

    - **Name:** Sarah
    - **Location:** London

    ### Past Experiences (Redeemed Offers)
    - **Pottery Workshop (Crafts, London, ££)** - Attended on 2024-10-28
    *Description:* Learn the basics of pottery wheel throwing and hand-building in a relaxed studio setting. Create your own unique ceramic pieces.

    ### Spending Habits (Recent Transactions)
    - **Dining:** £45 spent at **The Ivy (Restaurant)** (2024-12-15)
    - **Retail:** £12 spent at **Waterstones (Bookstore)** (2025-01-05)
    - **Entertainment:** £22 spent at **The National Gallery** (2025-01-12)

    ### Available Experiences (Not Yet Redeemed) - Example 1
    - **Gourmet Sushi Tasting** (Food, London, £££)
    *Description:* Indulge in an exquisite journey through the art of sushi-making.
    - **West End Theatre Show** (Entertainment, London, ££)
    *Description:* Enjoy a captivating performance of a hit musical or play in London's vibrant theatre district.
    - **Historical Walking Tour** (Culture, London, £)
    *Description:* Discover the hidden gems and historical landmarks of London with a knowledgeable guide.

    **Example Output:**

    Experience Persona: London Wanderer
    Persona Description: Sarah enjoys hands-on creative activities and culture. She appreciates both fine dining and budget options, suggesting a balanced lifestyle.

    Top 3 Recommendations:
    1. West End Theatre Show (Score: 9/10)
    - Relevance: 10/10
    - Novelty: 8/10
    - Diversity: 9/10
    - Justification: High relevance due to London location and entertainment spending. Novel, as its a different kind of entertainment.

    2. Gourmet Sushi Tasting (Score: 8/10)
    - Relevance: 8/10
    - Novelty: 7/10
    - Diversity: 8/10
    - Justification: High relevance due to London location and fine dining interest. It's novel and diverse as a different type of craft.

    3. Historical Walking Tour (Score: 7/10)
    -Relevance: 8/10
    - Novelty: 7/10
    - Diversity: 6/10
    - Justification: Relevant to location and cultural interests. Adds diversity in terms of price point.

    Serendipity Pick:
    Gourmet Sushi Tasting
    - Relevance: 8/10
    - Novelty: 7/10
    - Diversity: 8/10
    - Justification: While seemingly unrelated, surfing's hands-on nature might appeal to her creative side, offering a surprise.

    ## Example Input and Output (Illustrative) - Example 2

    **Example User Profile 2:**

    - **Name:** James
    - **Location:** Bristol

    ### Past Experiences (Redeemed Offers)
    - **Mountain Biking Day Trip (Adventure, Bristol, ££)** - Attended on 2024-10-15
    *Description:* Explore the challenging trails around Bristol with a guided mountain biking experience. All equipment provided. Suitable for intermediate to advanced riders.

    - **Craft Beer Tasting (Food & Drink, Bristol, £)** - Attended 2024-12-01
    *Description:* Sample a range of locally brewed craft beers in a relaxed pub setting. Learn about the brewing process and different beer styles.

    ### Spending Habits (Recent Transactions)
    - **Dining:** £15 spent at **Nando's (Restaurant)** (2024-12-28)
    - **Retail:** £40 spent at **Go Outdoors (Outdoor Gear Store)** (2025-01-08)
    - **Entertainment:** £10 spent at **Netflix Subscription** (2025-01-15)

    ### Available Experiences (Not Yet Redeemed) - Example 2
    - **Hot Air Balloon Ride** (Adventure, Bristol, £££)
    *Description:* Experience the breathtaking views of Bristol and the surrounding countryside from a hot air balloon.
    - **Escape Room Challenge** (Entertainment, Bristol, ££)
    *Description:* Test your problem-solving skills and teamwork in an immersive escape room experience.
    - **Cocktail Making Class** (Food & Drink, Bristol, ££)
    *Description:*Mix, muddle and shake your favorite cocktails.

    **Example Output 2:**

    Experience Persona: Active Explorer
    Persona Description: James enjoys active, outdoor adventures and local experiences. His spending is moderate, with a focus on practical gear and casual dining.

    Top 3 Recommendations:
    1. Escape Room Challenge (Score: 8/10)
    - Relevance: 9/10
    - Novelty: 8/10
    - Diversity: 7/10
    - Justification: Relevant to his location, and appeals to problem solving skills that may be used in his other hobbies.

    2. Hot Air Balloon Ride (Score: 8/10)
    - Relevance: 8/10
    - Novelty: 9/10
    - Diversity: 7/10
    - Justification: High relevance due to past adventure experience. Good diversity as it is a different type of adventure.

    3. Cocktail Making Class (Score: 7/10)
    - Relevance: 7/10
    - Novelty: 8/10
    - Diversity: 8/10
    - Justification: Relevant to his enjoyment of craft beer. Adds another string to his bow of Food & Drink.

    Serendipity Pick:
    Hot Air Balloon Ride
    - Relevance: 8/10
    - Novelty: 9/10
    - Diversity: 7/10
    - Justification: While this is an adventure experience, it is also a luxury experience which James does not usually go for.

    {user_profile}
    {experience_list}
    ## Recommendation Process

    *Note: Relevance is weighted most heavily as it is most important the recommendation aligns to the user. Novelty and Diversity have lower weightings, but are included to encourage a breadth of recommendations.*

    Follow these steps to generate personalized experience recommendations:

    **Step 1: Create an Experience Persona**

    Based *only* on the above profile, create:

    1.  **Experience Persona Name:** A highly creative and catchy label summarizing the user's preferences (e.g., "Adventurous Traveler"), ideally relating to the categories they spend most on. The persona name must be exactly two words. Be as imaginative as possible with this name, while still reflecting the user profile.
    2.  **Persona Description:** A detailed, human-like summary (maximum 50 words) of the user's lifestyle, interests, and spending habits, using only the provided data (past experiences, spending, and location).

    **Step 2: Analyze Spending Habits and Categorize**
    Categorize the spending habits into broad categories (e.g., Dining, Retail, Entertainment) and note the approximate price level (£, ££, £££) for each. Use these categories and price preferences to inform the Experience Persona and the Relevance scoring in Step 3. **Include these spending categories and price levels explicitly in the Persona Description.**

    *Rationale: This clarifies that the categorization is NOT just for internal processing but should be visible in the output, helping to understand the reasoning.*

    **Step 3: Experience Ranking and Recommendations**

    Rank each available experience out of 10 using the following criteria, using only the provided data:

    *   **Relevance (50%):** How well does this experience align with the user's past activities, location, and inferred interests (including spending categories)?  *Consider past experiences and spending habits, and nothing else.* **If the experience is in a different location than the user's stated location, calculate the relevance as if it were in the user's location, and then halve that score (round up to the nearest whole number).**
    *   **Novelty (30%):** How new or different is this experience for the user?  *Consider experiences in different categories or locations than those previously enjoyed. A novel experience should be in a different category (Food, Adventure, Wellness) or a significantly different location than past experiences, based on the provided data only.* *While striving for objectivity, acknowledge that some subjective judgment is inherent in assessing novelty.*
    *   **Diversity (20%):** How well does this experience broaden the user's horizons without being jarringly inconsistent with their profile?  *Consider a mix of price points (£, ££, £££) and activity types, avoiding overly similar recommendations.  A diverse experience might be in a new category but still align with an underlying interest (e.g., relaxation, culture, physical activity) inferable from the provided data.* *While striving for objectivity, acknowledge that some subjective judgment is inherent in assessing diversity.*
    *   **Location Mismatch:** Applied in the relevance score.

    Provide a score (out of 10, *whole numbers only*) for each category (Relevance, Novelty, Diversity) and calculate a final weighted score:  `(Relevance * 0.5) + (Novelty * 0.3) + (Diversity * 0.2)`. Sort the experiences from highest to lowest score. Recommend the top 3 experiences.

    **Step 4: Serendipity Pick**

    Recommend *one* **Serendipity Pick**: an experience the user is *unlikely* to choose based on their explicit past behavior but could align well with a *potential* interest derived *solely* from their persona, *by considering connections between their existing activities and spending categories*. Explain why this pick is both surprising *and* potentially valuable. *For example, if a user frequently attends concerts (Music), a Serendipity Pick could be a workshop related to creating music (Crafts), as it connects to the underlying theme of artistic expression.*

    This should be an experience **not** already recommended in the top 3. **However, if no other available experiences exist outside of the Top 3 recommendations, select the *lowest-scoring* experience from the Top 3 as the Serendipity Pick. In this case, clearly state that this is happening and explain why, given the constraints, this is the best possible Serendipity Pick. Focus your justification on why it is *still* the most surprising and potentially valuable *relative to the other Top 3 options*, even if it's not ideal.**

    **Step 5: Ranking Breakdown & Explanation**

    For *each* recommendation (Top 3 and Serendipity Pick), provide a detailed explanation (maximum 50 words per explanation section) including:

    1.  **Scoring Breakdown:** Show the scores for Relevance, Novelty, and Diversity.
    2.  **Justification:** Explain *why* those scores were assigned, referencing *only* specific aspects of the user's provided profile (past experiences, spending habits, location, and persona). Do not make any assumptions beyond the provided data.

    **Step 6: Output Format**

    Use the following structured format for your response:

    ```
    Experience Persona: [Persona Name]
    Persona Description: [Detailed description summarizing the user's interests, lifestyle, and spending habits, max 50 words]

    Top 3 Recommendations:
    1. [Experience Title] (Score: X.X/10)
    - Relevance: X.X/10
    - Novelty: X.X/10
    - Diversity: X.X/10
    - Justification: [Explanation of why this experience was ranked high, including relevance, novelty, and diversity breakdown, max 50 words]

    2. [Experience Title] (Score: X.X/10)
    - Relevance: X.X/10
    - Novelty: X.X/10
    - Diversity: X.X/10
    - Justification: [Explanation of why this experience fits the user, with scoring breakdown, max 50 words]

    3.[Experience Title] (Score: X.X/10)
    - Relevance: X.X/10
    - Novelty: X.X/10
    - Diversity: X.X/10
    - Justification: [Explanation of why this experience adds diversity to the user's profile, with scoring breakdown, max 50 words]

    Serendipity Pick:
    [Experience Title]
    - Relevance: X.X/10
    - Novelty: X.X/10
    - Diversity: X.X/10
    - Justification: [Explanation of why this experience is outside the user's usual preferences but could be a surprising and valuable addition to their life, max 50 words]
    ```

    **Key Definitions:**

    *   **£:** Budget-friendly
    *   **££:** Mid-range
    *   **£££:** Luxury

    **Step 7: Iteration (Internal)**
    If, upon internal review, the recommendations do not sufficiently meet the above criteria (especially regarding the justification and scoring, and the exclusive use of provided data), revise the persona and re-rank the experiences. Repeat this process until a satisfactory and well-justified set of recommendations is achieved. This is an internal instruction for the AI, not part of the output. *This step is considered implicit in the overall task and can be omitted from the explicit instructions.*

    **Step 8: Edge Case Handling (Internal)**
    **If all available experiences receive the same final score, select the top experiences alphabetically for the Top 3 Recommendations. This is an internal instruction for the AI and should not be explicitly stated in the output.**

    **FAILURE TO BASE YOUR RECOMMENDATIONS *SOLELY* ON THE PROVIDED DATA WILL RESULT IN AN UNSUCCESSFUL RESPONSE.**
    """

    response = client.chat.completions.create(
        model="gpt-4o-2024-11-20",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }   
        ],
        response_format={"type": "text"},
        temperature=0.7,
        max_completion_tokens=1000,
        frequency_penalty=0.5,
        presence_penalty=0.5
    )

    return prompt.replace("\n", "<br>"), response.choices[0].message.content.strip().replace("\n", "<br>")

    # return prompt.replace("\n", "<br>"), prompt.replace("\n", "<br>")

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