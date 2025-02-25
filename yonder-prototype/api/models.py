from pydantic import BaseModel
from typing import List, Optional

class Experience(BaseModel):
    experience_id: str
    title: str
    category: str
    short_description: str
    long_description: str
    location: str
    price_range: str
    rating: float
    images: List[str]
    available_dates: List[str]

class PastRedeemedOffer(BaseModel):
    experience_id: str
    redeemed_date: str

class CardTransaction(BaseModel):
    transaction_id: str
    date: str
    merchant_name: str
    category: str
    amount: float

class User(BaseModel):
    member_id: str
    name: str
    location: str
    past_redeemed_offers: List[PastRedeemedOffer]
    card_transactions: List[CardTransaction]