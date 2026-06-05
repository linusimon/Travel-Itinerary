from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class TripPreferences(BaseModel):
    destination: str
    start_date: str
    end_date: str
    budget: Optional[str] = "moderate"
    interests: List[str] = []
    pace: Optional[str] = "moderate"  # relaxed, moderate, packed
    accommodation_location: Optional[str] = None
    dietary_restrictions: Optional[List[str]] = []
    transportation_preference: Optional[str] = "mixed"

class ChatMessage(BaseModel):
    message: str
    conversation_history: Optional[List[dict]] = []
    trip_context: Optional[TripPreferences] = None

class Activity(BaseModel):
    time: str
    title: str
    description: str
    duration: str
    location: str
    cost_estimate: Optional[str] = None
    tips: Optional[str] = None

class DayItinerary(BaseModel):
    day: int
    date: str
    theme: str
    activities: List[Activity]
    total_estimated_cost: Optional[str] = None

class TripItinerary(BaseModel):
    destination: str
    duration: str
    itinerary: List[DayItinerary]
    travel_tips: List[str]
    packing_suggestions: List[str]
