@echo off
echo ========================================
echo  Starting Backend Server
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

echo Starting Flask server...
@REM python app.py
flask run --port=5001

pause

