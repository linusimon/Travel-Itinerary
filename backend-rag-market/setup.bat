@echo off
echo ========================================
echo  Capital Markets Risk Summarizer - Backend Setup
echo ========================================
echo.

echo [1/4] Creating virtual environment...
python -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo Virtual environment created successfully!
echo.

echo [2/4] Activating virtual environment...
call venv\Scripts\activate
echo.

echo [3/4] Upgrading pip...
python -m pip install --upgrade pip
echo.

echo [4/4] Installing dependencies...
pip install -r requirement.txt
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully!
echo.

echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Run start.bat to spin up the Flask service on port 5003.
echo.
echo Press any key to exit...
pause > nul
