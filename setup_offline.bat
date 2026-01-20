@echo off
echo ================================================
echo MORNING QUIZ SYSTEM - OFFLINE SETUP
echo ================================================
echo.

echo [1/5] Checking Docker installation...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not running
    echo Please install Docker Desktop and try again
    pause
    exit /b 1
)
echo Docker is installed and running

echo.
echo [2/5] Stopping any existing containers...
docker-compose down >nul 2>&1

echo.
echo [3/5] Starting system with offline configuration...
docker-compose -f docker-compose.offline.yml up -d

echo.
echo [4/5] Waiting for services to initialize...
timeout /t 15 /nobreak >nul

echo.
echo [5/5] Testing offline functionality...
python test_offline_working.py

echo.
echo ================================================
echo SETUP COMPLETE!
echo ================================================
echo.
echo Your Morning Quiz System is now ready for offline use!
echo.
echo Access URLs:
echo   Student Portal: http://localhost:3000
echo   Teacher Portal: http://localhost:3000/teacher  
echo   Admin Portal:   http://localhost:3000/admin
echo.
echo For LAN access, replace 'localhost' with your PC's IP address
echo To find your IP: ipconfig
echo.
echo Default Login:
echo   Admin: admin / admin123
echo   Student: student001 / pass123
echo.
echo OFFLINE FEATURES:
echo   - Works without internet after first setup
echo   - PWA installable on mobile devices
echo   - Automatic data sync when back online
echo   - Cached quiz questions and results
echo   - Local answer storage
echo.
pause