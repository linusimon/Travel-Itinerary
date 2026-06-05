# AI-Powered Travel Itinerary Assistant
# TCS GenAI Lab Hackathon 2026

## Quick Start

This project contains both backend (Python/Flask) and frontend (Angular) for an AI-powered travel planning assistant.

### Prerequisites
- Python 3.12.8
- Node.js & npm
- GenAI Lab API Key (will be provided)

### Setup

1. **Backend Setup**
   ```powershell
   cd backend
   .\setup.bat
   # Edit .env and add your API key
   .\start.bat
   ```

2. **Frontend Setup** (in new terminal)
   ```powershell
   cd frontend
   .\setup.bat
   .\start.bat
   ```

3. **Access Application**
   - Open browser to http://localhost:4200
   - Backend runs on http://localhost:5000

### Full Documentation
- [Complete Setup Guide](SETUP.md) - Step-by-step instructions
- [Main README](README.md) - Full project documentation
- [Backend README](backend/README.md) - Backend specific docs
- [Frontend README](frontend/README.md) - Frontend specific docs

### Architecture
```
Frontend (Angular) → Backend (Flask) → GenAI Lab API (DeepSeek-V3)
   Port 4200            Port 5000        https://genailab.tcs.in
```

### Key Features
✅ AI-powered itinerary generation
✅ Conversational refinement
✅ Day-by-day planning
✅ Export & print functionality
✅ Responsive design

### Support
See [SETUP.md](SETUP.md) for troubleshooting and common issues.

---
Built for TCS GenAI Lab Hackathon 2026 🚀
