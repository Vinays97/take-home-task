import json
import os
import shutil
import html
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from .models import User, Experience, PastRedeemedOffer, CardTransaction
from .recommender import get_recommendations, load_data

app = FastAPI()

users = []
experiences = []

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), '../templates'))

@app.on_event("startup")
async def startup_event():
    global users, experiences
    shutil.rmtree(os.path.join(os.path.dirname(__file__), '__pycache__'), ignore_errors=True)
    print("Current working directory:", os.getcwd())
    users, experiences = load_data()

@app.get("/")
async def root(request: Request):
    users_list = await list_users()
    experiences_list = await list_experiences()
    print("Users List:", users_list)
    print("Experiences List:", experiences_list)
    return templates.TemplateResponse("users.html", {"request": request, "users": users_list, "experiences": experiences_list})

@app.get("/users")
async def list_users():
    return [{"user_id": user["member_id"], "name": user["name"]} for user in users]

@app.get("/users/{member_id}")
async def get_user(member_id: str):
    user = next((usr for usr in users if usr["member_id"] == member_id), None)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/experiences")
async def list_experiences():
    return [{
        "title": exp["title"],
        "category": exp["category"],
        "location": exp["location"],
        "price_range": html.escape(exp["price_range"]),
        "short_description": exp["short_description"]
    } for exp in experiences]

@app.get("/experiences/{experience_id}")
async def get_experience(experience_id: str):
    experience = next((exp for exp in experiences if exp["experience_id"] == experience_id), None)
    if experience is None:
        raise HTTPException(status_code=404, detail="Experience not found")
    experience["price_range"] = html.escape(experience["price_range"])
    return experience

@app.get("/recommendations/{user_id}", response_class=HTMLResponse)
async def get_recommendations_endpoint(request: Request, user_id: str):
    details = get_recommendations(user_id)
    if details == "User not found":
        raise HTTPException(status_code=404, detail="User not found")
    return HTMLResponse(content=details, status_code=200)

@app.get("/health")
async def health_check():
    return {"status": "ok"}