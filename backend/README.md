# Backend Setup Guide

## Prerequisites
- Python 3.12.8 (pre-installed in GenAI Lab)
- pip (Python package manager)
- Virtual environment support

## Installation Steps

### 1. Create Virtual Environment
```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Verify Installation
```bash
pip freeze
```

You should see packages like:
- flask==3.0.0
- langchain==0.1.0
- langchain-openai==0.0.5
- pydantic==2.5.0
- httpx==0.25.2

### 5. Configure Environment

Create `.env` file (copy from `.env.example`):
```bash
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

Edit `.env` and add your API key:
```
GENAI_API_KEY=your_api_key_here
```

### 6. Test the Backend

Run the server:
```bash
python run.py
```

You should see:
```
Starting Travel Itinerary Assistant Backend...
Server running on http://0.0.0.0:5000
API Key configured: Yes
```

### 7. Test Health Endpoint

Open browser or use curl:
```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Travel Itinerary Assistant"
}
```

## Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/generate` | POST | Generate itinerary |
| `/api/chat` | POST | Chat refinement |
| `/api/places/search` | GET | Search places |
| `/api/export` | POST | Export itinerary |

## Configuration Options

Edit `app/config.py` to customize:

```python
# Change AI model
CHAT_MODEL = "azure_ai/genailab-maas-Llama-3.3-70B-Instruct"

# Change port
FLASK_PORT = 5001

# Enable/disable debug mode
DEBUG = True
```

## Troubleshooting

### Issue: Module not found
**Solution:** Ensure virtual environment is activated
```bash
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### Issue: Port already in use
**Solution:** Change port in `config.py` or kill process:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill
```

### Issue: SSL warnings
**Solution:** This is normal for GenAI Lab internal network. The httpx client is configured with `verify=False`.

### Issue: API key not working
**Solution:** 
1. Check `.env` file exists
2. Restart the server after adding API key
3. Verify key format (no quotes or extra spaces)

## Development Tips

### Hot Reload
Flask debug mode enables auto-reload on code changes:
```python
DEBUG = True  # in config.py
```

### Logging
Add logging for debugging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Testing API with Postman/Curl

**Generate Itinerary:**
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Paris",
    "start_date": "2026-07-01",
    "end_date": "2026-07-05",
    "budget": "moderate",
    "interests": ["History & Culture", "Food & Dining"],
    "pace": "moderate"
  }'
```

**Chat:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add more museums",
    "conversation_history": []
  }'
```

## Production Deployment

For production, consider:
1. Set `DEBUG = False`
2. Use a production WSGI server (Gunicorn)
3. Add rate limiting
4. Implement caching
5. Add authentication

## Next Steps

Once backend is running:
1. Set up the frontend
2. Test the integration
3. Start developing features
