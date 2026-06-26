@echo off
setlocal enabledelayedexpansion

echo ========================================
echo  Capital Markets Risk Summarizer - Backend Setup
echo ========================================
echo.

REM Remove existing virtual environment if it exists
if exist venv (
    echo Removing existing virtual environment...
    rmdir /s /q venv
    echo.
)

echo [1/4] Creating virtual environment...
echo Running: python -m venv venv
python -m venv venv
if not exist venv\Scripts\python.exe (
    echo ERROR: Virtual environment creation failed
    echo Please ensure Python 3.12 is properly installed
    echo.
    pause
    exit /b 1
)
echo Virtual environment created successfully!
echo.

echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat
if "!VIRTUAL_ENV!"=="" (
    echo Warning: Virtual environment activation may have issues, but continuing...
)
echo.

echo [3/4] Installing/Upgrading pip...
echo Downloading pip installer...
curl -s https://bootstrap.pypa.io/get-pip.py -o get-pip.py
if not exist get-pip.py (
    echo ERROR: Failed to download pip installer
    echo Please check your internet connection
    pause
    exit /b 1
)
echo Installing pip...
venv\Scripts\python.exe get-pip.py
del get-pip.py
echo Upgrading pip...
venv\Scripts\python.exe -m pip install --upgrade pip
echo.

echo [4/4] Installing dependencies...
echo Installing packages from requirement.txt...
venv\Scripts\pip.exe install -r requirement.txt
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
