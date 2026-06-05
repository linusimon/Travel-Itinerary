@echo off
echo ========================================
echo  Starting Frontend Development Server
echo ========================================
echo.

if not exist node_modules (
    echo ERROR: node_modules not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

echo Starting Angular development server...
echo.
echo Frontend will be available at: http://localhost:4200
echo Backend must be running at: http://localhost:5000
echo.
call npm start

pause
