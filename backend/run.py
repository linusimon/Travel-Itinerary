from app.main import app
from app.config import Config

if __name__ == '__main__':
    print(f"Starting Travel Itinerary Assistant Backend...")
    print(f"Server running on http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    print(f"API Key configured: {'Yes' if Config.GENAI_API_KEY != 'YOUR_KEY_HERE' else 'No - Please set GENAI_API_KEY'}")
    
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.DEBUG
    )
