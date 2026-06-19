@echo off
echo ========================================
echo  Capital Markets Risk Summarizer - Frontend Setup
echo ========================================
echo.

echo [1/2] Installing dependencies...
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install dependencies.
    echo Make sure Node.js and npm are installed.
    pause
    exit /b 1
)
echo Dependencies installed successfully!
echo.

echo [2/2] Verifying Angular CLI...
call ng version
echo.

echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Ensure the backend Flask server is running on port 5003
echo 2. Run: start.bat (to serve the app on port 4203)
echo.
echo Press any key to exit...
pause > nul
