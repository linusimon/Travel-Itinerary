@echo off
echo ========================================
echo  Starting Capital Markets Frontend (Port 4203)
echo ========================================
echo.

if not exist node_modules (
    echo ERROR: node_modules not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

echo Starting Angular development server on port 4203...
echo Frontend: http://localhost:4203
echo Backend Target: http://localhost:5003
echo.
call npm start

pause
