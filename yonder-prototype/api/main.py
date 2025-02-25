import json
from fastapi import FastAPI, HTTPException
from .models import User, Experience, RecommendationRequest
from .recommender import get_recommendations, load_data

app = FastAPI()

users = []
experiences = []

@app.on_event("startup")
async def startup_event():
    global users, experiences
    users, experiences = load_data()

@app.get("/recommendations/{user_id}")
async def get_recommendations_endpoint(user_id: str):
    user = next((u for u in users if u.member_id == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    recommendations = get_recommendations(user, experiences)
    return recommendations

@app.post("/reload-data")
async def reload_data_endpoint():
    global users, experiences
    users, experiences = load_data()
    return {"message": "Data reloaded successfully"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
