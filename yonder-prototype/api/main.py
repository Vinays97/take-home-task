import json
import os
import shutil
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from .models import User, Experience, RecommendationRequest
from .recommender import get_recommendations, load_data

app = FastAPI()

users = []
experiences = []

# Initialize Jinja2 templates with absolute path
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), '../templates'))

@app.on_event("startup")
async def startup_event():
    global users, experiences
    shutil.rmtree(os.path.join(os.path.dirname(__file__), '__pycache__'), ignore_errors=True)
    users, experiences = load_data()

@app.get("/")
async def root(request: Request):
    users_list = await list_users()
    experiences_list = await list_experiences()
    return templates.TemplateResponse("users.html", {"request": request, "users": users_list, "experiences": experiences_list})

@app.get("/users")
async def list_users():
    return [{"user_id": user["member_id"], "name": user["name"]} for user in users]

@app.get("/users/html")
async def list_users_html(request: Request):
    users_list = await list_users()
    return templates.TemplateResponse("users.html", {"request": request, "users": users_list})

@app.get("/experiences")
async def list_experiences():
    return [{
        "title": exp["title"],
        "category": exp["category"],
        "location": exp["location"],
        "price_range": exp["price_range"].replace("Â", ""),
        "short_description": exp["short_description"]
    } for exp in experiences]

@app.get("/recommendations/{user_id}")
async def get_recommendations_endpoint(user_id: str):
    user_data = next((u for u in users if u["member_id"] == user_id), None)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    user = User(**user_data)
    recommendations = get_recommendations(user, experiences)
    return recommendations

@app.get("/health")
async def health_check():
    return {"status": "ok"}
