# Quick Setup Guide - TCS GenAI Lab Hackathon

## Complete Setup (Both Frontend and Backend)

### Step 1: Open VS Code
1. Launch VS Code from GenAI Lab desktop
2. Open folder: Navigate to where you want to create the project
3. Open Terminal (Ctrl + `)

### Step 2: Navigate to Project
```powershell
cd C:\Users\lsimon1\travel-itinerary-assistant
```

### Step 3: Backend Setup

**Option A: Automated Setup (Recommended)**
```powershell
cd backend
.\setup.bat
```

**Option B: Manual Setup**
```powershell
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env
```

**Configure API Key:**
1. Open `backend\.env` in VS Code
2. Replace `YOUR_KEY_HERE` with your actual API key from hackathon
3. Save the file

### Step 4: Start Backend Server

**Option A: Using Script**
```powershell
cd backend
.\start.bat
```

**Option B: Manual Start**
```powershell
cd backend
venv\Scripts\activate
python run.py
```

✅ Backend should be running on `http://localhost:5000`

### Step 5: Frontend Setup (New Terminal)

Open a NEW terminal (keep backend running):
```powershell
# Navigate to project root
cd C:\Users\lsimon1\travel-itinerary-assistant

# Go to frontend
cd frontend
```

**Option A: Automated Setup (Recommended)**
```powershell
.\setup.bat
```

**Option B: Manual Setup**
```powershell
# Install dependencies
npm install

# Verify Angular CLI
ng version
```

### Step 6: Start Frontend Server

**Option A: Using Script**
```powershell
.\start.bat
```

**Option B: Manual Start**
```powershell
npm start
```

✅ Frontend should be running on `http://localhost:4200`

### Step 7: Access the Application

1. Open browser (Chrome/Edge)
2. Navigate to: `http://localhost:4200`
3. You should see the Travel Itinerary Assistant homepage

## Quick Reference

### Terminal 1 (Backend)
```powershell
cd C:\Users\lsimon1\travel-itinerary-assistant\backend
venv\Scripts\activate
python run.py
```

### Terminal 2 (Frontend)
```powershell
cd C:\Users\lsimon1\travel-itinerary-assistant\frontend
npm start
```

## Verification Checklist

- [ ] Backend running on port 5000
- [ ] Frontend running on port 4200
- [ ] Browser shows application homepage
- [ ] No error messages in terminals
- [ ] API key configured in `.env`

## Health Check

### Test Backend
Open browser or PowerShell:
```powershell
curl http://localhost:5000/api/health
```

Expected response:
```json
{"status": "healthy", "service": "Travel Itinerary Assistant"}
```

### Test Frontend
Navigate to `http://localhost:4200` - you should see the form.

## Common Issues & Solutions

### Issue: "Port 5000 already in use"
**Solution:**
```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID)
taskkill /PID <PID> /F
```

### Issue: "Port 4200 already in use"
**Solution:**
```powershell
# Use different port
ng serve --port 4201
```

Then update `environment.ts` if needed.

### Issue: "Module not found" (Python)
**Solution:**
```powershell
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: "Cannot find module" (Node)
**Solution:**
```powershell
cd frontend
npm install
```

### Issue: "Cannot connect to backend"
**Solution:**
1. Verify backend is running (check Terminal 1)
2. Check `http://localhost:5000/api/health`
3. Verify no firewall blocking
4. Check CORS configuration in `backend/app/main.py`

### Issue: "API Key not working"
**Solution:**
1. Check `.env` file exists in backend folder
2. Verify no extra spaces or quotes around key
3. Restart backend server after adding key

## Development Workflow

### Starting Work
1. Start backend: `cd backend && .\start.bat`
2. Start frontend: `cd frontend && .\start.bat`
3. Open browser to `http://localhost:4200`

### Stopping Services
- Press `Ctrl+C` in each terminal
- Or close terminal windows

### Making Changes

**Backend Changes:**
- Edit files in `backend/app/`
- Flask auto-reloads in debug mode
- No restart needed (usually)

**Frontend Changes:**
- Edit files in `frontend/src/`
- Angular auto-reloads
- Changes appear in browser immediately

## Folder Backup

Remember to backup your code to the shared folder:
```
\\genailab-maas-hackathon\Hackathon\[Your-Region]\[Your-Team]
```

**Important:** Only backup source code, NOT:
- `node_modules/` folder
- `venv/` folder
- `dist/` folder
- `.angular/` folder

## Testing the Application

### 1. Fill the Form
- Destination: Paris
- Dates: July 1-5, 2026
- Budget: Moderate
- Interests: History & Culture, Food & Dining
- Pace: Moderate

### 2. Generate Itinerary
- Click "Generate Itinerary"
- Wait for AI response (5-15 seconds)

### 3. View Results
- Should display day-by-day itinerary
- Activities with timings
- Travel tips

### 4. Test Chat
- Click "Refine with Chat"
- Type: "Add more museum visits"
- Check AI response

### 5. Export
- Click "Export as Text"
- File should download

## Performance Tips

- Keep only 2 terminals open (backend + frontend)
- Close unused browser tabs
- Clear browser cache if UI issues
- Restart services if experiencing slowness

## Next Steps

Once setup is complete:
1. ✅ Test basic functionality
2. ✅ Customize prompts if needed
3. ✅ Add team-specific features
4. ✅ Prepare demo scenario
5. ✅ Backup code regularly

## Support

For issues during hackathon:
- Check this guide first
- Review error messages in terminal
- Ask your team members
- Contact AI Lab SPOC

## Quick Commands Reference

```powershell
# Backend
cd backend
venv\Scripts\activate          # Activate environment
python run.py                   # Start server
deactivate                      # Deactivate environment

# Frontend  
cd frontend
npm install                     # Install dependencies
npm start                       # Start dev server
ng serve --port 4201           # Use different port
ng build                        # Build for production

# Both
Ctrl+C                          # Stop server
```

Good luck with your hackathon! 🚀
