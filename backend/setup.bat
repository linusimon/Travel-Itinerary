@echo off
echo ========================================
echo  Travel Itinerary Assistant - Backend Setup
echo ========================================
echo.

echo [1/5] Creating virtual environment...
python -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo Virtual environment created successfully!
echo.

echo [2/5] Activating virtual environment...
call venv\Scripts\activate
echo.

echo [3/5] Upgrading pip...
python -m pip install --upgrade pip
echo.

echo [4/5] Installing dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully!
echo.

echo [5/5] Creating .env file...
if not exist .env (
    copy .env.example .env
    echo .env file created from template
    echo IMPORTANT: Please edit .env and add your GenAI API key
) else (
    echo .env file already exists
)
echo.

echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file and add your GENAI_API_KEY
echo 2. Run: python run.py
echo.
echo Press any key to exit...
pause > nul
