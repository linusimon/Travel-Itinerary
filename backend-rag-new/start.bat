@echo off
echo ========================================
echo  Starting Business Analysis Summarizer Backend
echo ========================================
echo.

if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate
echo.

echo Starting Flask server on port 5002...
@REM python app.py
flask run --port=5002

pause
