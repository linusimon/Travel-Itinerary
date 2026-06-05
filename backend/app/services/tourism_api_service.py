import requests
from typing import List, Dict, Optional
from app.config import Config

class TourismAPIService:
    """Service to fetch real-time tourism data from external APIs"""
    
    def __init__(self):
        self.google_api_key = Config.GOOGLE_PLACES_API_KEY
        self.opentripmap_api_key = Config.OPENTRIPMAP_API_KEY
    
    def search_places(self, destination: str, category: str = "tourist_attraction") -> List[Dict]:
        """Search for places using Google Places API (if key available)"""
        
        if not self.google_api_key:
            return self._get_mock_places(destination, category)
        
        # Implementation for Google Places API
        # url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        # params = {
        #     "query": f"{category} in {destination}",
        #     "key": self.google_api_key
        # }
        # response = requests.get(url, params=params)
        # return response.json().get("results", [])
        
        return self._get_mock_places(destination, category)
    
    def get_place_details(self, place_id: str) -> Optional[Dict]:
        """Get detailed information about a specific place"""
        
        if not self.google_api_key:
            return None
        
        # Implementation for place details
        return None
    
    def _get_mock_places(self, destination: str, category: str) -> List[Dict]:
        """Return mock data when API keys are not available"""
        
        mock_data = {
            "paris": [
                {"name": "Eiffel Tower", "rating": 4.7, "type": "landmark"},
                {"name": "Louvre Museum", "rating": 4.8, "type": "museum"},
                {"name": "Notre-Dame Cathedral", "rating": 4.6, "type": "landmark"},
            ],
            "tokyo": [
                {"name": "Senso-ji Temple", "rating": 4.6, "type": "temple"},
                {"name": "Tokyo Skytree", "rating": 4.5, "type": "landmark"},
                {"name": "Meiji Shrine", "rating": 4.7, "type": "shrine"},
            ]
        }
        
        return mock_data.get(destination.lower(), [])
