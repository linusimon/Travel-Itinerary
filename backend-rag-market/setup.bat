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
echo Running: python -m venv venv --clear
echo This may take 1-2 minutes. Please wait...
echo.

REM Create venv with timeout protection
set "VENV_CMD=python -m venv venv --clear"
echo Starting venv creation...
START /B "" cmd /c "%VENV_CMD% 2>&1"

REM Wait with progress indicator (max 120 seconds)
set /a counter=0
:wait_loop
timeout /t 2 /nobreak >nul
set /a counter+=2
if exist venv\Scripts\python.exe goto venv_success
if %counter% GEQ 120 goto venv_timeout
echo Still creating virtual environment... (%counter%s elapsed)
goto wait_loop

:venv_timeout
echo.
echo ERROR: Virtual environment creation timed out after 120 seconds
echo This might be caused by:
echo - Antivirus software scanning files
echo - Slow disk I/O
echo - Python installation issues
echo.
echo Try running this command manually: python -m venv venv --clear
echo.
pause
exit /b 1

:venv_success
timeout /t 2 /nobreak >nul
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
