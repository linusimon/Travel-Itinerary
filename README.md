# AI-Powered Travel Itinerary Assistant

## Overview
An AI-powered web application that generates personalized travel itineraries based on user preferences. Built for the TCS GenAI Lab Hackathon 2026.

## Features
- 🤖 **AI-Powered Itinerary Generation** - Uses GenAI Lab's DeepSeek-V3 model
- 💬 **Conversational Refinement** - Chat interface to adjust your plans
- 📅 **Day-by-Day Planning** - Detailed daily schedules with activities and timings
- 🎯 **Personalized Recommendations** - Based on interests, budget, and pace
- 📤 **Export Options** - Download itineraries in text or JSON format
- 🖨️ **Print Support** - Print-friendly itinerary views
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile

## Tech Stack

### Backend
- Python 3.12.8
- Flask (REST API)
- LangChain (AI orchestration)
- OpenAI API (via GenAI Lab)
- Pydantic (data validation)

### Frontend
- Angular 17
- TypeScript
- SCSS
- Reactive Forms
- HttpClient

## Project Structure
```
travel-itinerary-assistant/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── services/
│   │   │   ├── llm_service.py
│   │   │   ├── itinerary_service.py
│   │   │   └── tourism_api_service.py
│   │   └── routes/
│   │       └── itinerary_routes.py
│   ├── requirements.txt
│   ├── run.py
│   └── .env
└── frontend/
    ├── src/
    │   ├── app/
    │   │   ├── components/
    │   │   ├── services/
    │   │   └── models/
    │   └── environments/
    └── package.json
```

## Setup Instructions

### Prerequisites
- Python 3.12.8 (pre-installed in GenAI Lab)
- Node.js and npm (for local development)
- VS Code (pre-installed in GenAI Lab)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate on Windows
   venv\Scripts\activate
   
   # Activate on Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   - Copy `.env.example` to `.env`
   - Add your GenAI API key (will be provided during hackathon):
   ```
   GENAI_API_KEY=your_api_key_here
   ```

5. **Run the backend server:**
   ```bash
   python run.py
   ```
   
   The backend will start on `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   # or
   ng serve
   ```
   
   The frontend will start on `http://localhost:4200`

### Quick Start (Both Services)

**Terminal 1 (Backend):**
```bash
cd backend
venv\Scripts\activate
python run.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm start
```

## Configuration

### Backend Configuration (`backend/app/config.py`)
- **GENAI_BASE_URL**: GenAI Lab API endpoint
- **GENAI_API_KEY**: Your API key (set in .env file)
- **CHAT_MODEL**: AI model for generation (default: DeepSeek-V3)
- **FLASK_PORT**: Backend server port (default: 5000)

### Frontend Configuration (`frontend/src/environments/environment.ts`)
- **apiUrl**: Backend API URL (default: http://localhost:5000/api)

## Available Models (GenAI Lab)

### Chat Models
- `azure_ai/genailab-maas-DeepSeek-V3-0324` (Default)
- `azure/genailab-maas-gpt-4o`
- `azure_ai/genailab-maas-Llama-3.3-70B-Instruct`
- `azure_ai/genailab-maas-Phi-4-reasoning`

### Embedding Models
- `azure/genailab-maas-text-embedding-3-large`

## API Endpoints

### Health Check
```
GET /api/health
```

### Generate Itinerary
```
POST /api/generate
Body: {
  "destination": "Paris",
  "start_date": "2026-07-01",
  "end_date": "2026-07-05",
  "budget": "moderate",
  "interests": ["History & Culture", "Food & Dining"],
  "pace": "moderate"
}
```

### Chat Refinement
```
POST /api/chat
Body: {
  "message": "Add more museum visits",
  "conversation_history": [...],
  "trip_context": {...}
}
```

### Search Places
```
GET /api/places/search?destination=Paris&category=tourist_attraction
```

### Export Itinerary
```
POST /api/export
Body: {
  "itinerary": {...},
  "format": "text" // or "json"
}
```

## Usage Guide

1. **Fill in Trip Details:**
   - Enter destination
   - Select dates
   - Choose budget level (budget/moderate/luxury)
   - Select travel pace (relaxed/moderate/packed)
   - Pick your interests

2. **Generate Itinerary:**
   - Click "Generate Itinerary"
   - Wait for AI to create your personalized plan

3. **Refine Your Plan:**
   - Use the chat interface to make adjustments
   - Ask questions about activities
   - Request changes to timing or activities

4. **Export & Share:**
   - Export as text or JSON
   - Print for offline use

## Development Notes

### Adding API Key During Hackathon
When you receive your API key, update the `.env` file:
```
GENAI_API_KEY=your_actual_key_here
```

Then restart the backend server.

### Testing Without API Key
The application will run but AI features won't work until the API key is configured.

### Customizing the AI Model
Edit `backend/app/config.py` to change the model:
```python
CHAT_MODEL = "azure_ai/genailab-maas-Llama-3.3-70B-Instruct"
```

## Troubleshooting

### Backend Issues
- **Port 5000 already in use:** Change `FLASK_PORT` in config.py
- **Import errors:** Ensure virtual environment is activated
- **SSL warnings:** Normal for internal network, httpx client configured with `verify=False`

### Frontend Issues
- **Cannot connect to backend:** Ensure backend is running on port 5000
- **Port 4200 already in use:** Use `ng serve --port 4201`
- **Module not found:** Run `npm install`

### CORS Issues
If you encounter CORS errors, check that:
- Backend CORS is configured for `http://localhost:4200`
- Frontend is using the correct API URL

## Performance Optimization

- LangChain caching for repeated queries
- Optimized prompt engineering for faster responses
- Frontend lazy loading for components
- Efficient state management

## Future Enhancements

- [ ] Integration with Google Places API
- [ ] Real-time flight and hotel search
- [ ] Multi-destination trip planning
- [ ] Weather integration
- [ ] Collaborative trip planning
- [ ] Budget tracking
- [ ] Map visualization

## Team

Built for TCS GenAI Lab Hackathon 2026

## License

This project is for hackathon purposes only.

## Support

For issues or questions during the hackathon, contact your AI Lab SPOC.
