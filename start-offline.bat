@echo off
title Morning Quiz System - Offline Mode
echo Starting Morning Quiz System (Offline Mode)
echo ==========================================

echo Stopping any running containers...
docker-compose -f docker-compose.offline.yml down

echo Building and starting system in offline mode...
docker-compose -f docker-compose.offline.yml up -d --build

echo Waiting for services to start...
timeout /t 15 /nobreak >nul

echo Checking service status...
docker-compose -f docker-compose.offline.yml ps

echo.
echo System Status:
docker-compose -f docker-compose.offline.yml ps --format "table {{.Names}}\t{{.Status}}"

echo.
echo 📱 Morning Quiz System is now running in FULL OFFLINE MODE!
echo.
echo Access URLs:
echo - Students: http://localhost:3000
echo - Teachers: http://localhost:3000/teacher  
echo - Admin:    http://localhost:3000/admin
echo.
echo Login Credentials:
echo - Student Login: student001 / student123
echo - Teacher Login: NGEZAHAYO / 12345678
echo - Admin Login:   admin / admin123
echo.
echo ✅ System Features in Offline Mode:
echo    - All quizzes and content accessible
echo    - Full functionality without internet
echo    - Data automatically syncs when online
echo    - Installable as standalone app
echo    - Works on any device without internet
echo.
echo 🔧 Technical Details:
echo    - Database container: Running locally
echo    - Backend container: Running locally
echo    - Frontend container: Running locally
echo    - No external internet dependencies
echo    - All assets bundled with application
echo.
echo To stop the system, run: stop.bat
echo.
echo Press any key to continue...
pause >nul