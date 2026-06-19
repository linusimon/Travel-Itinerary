@echo off
echo ========================================
echo  Starting Capital Markets Backend Server (Port 5003)
echo ========================================
echo.

if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate
echo.

echo Starting Flask server...
python app.py

pause
