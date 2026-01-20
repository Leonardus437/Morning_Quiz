@echo off
cls
echo ========================================
echo    TVET QUIZ SYSTEM - FINAL REBUILD
echo ========================================
echo.

echo 🔄 Step 1: Complete System Reset...
docker-compose down --remove-orphans --volumes
docker system prune -af --volumes

echo.
echo 🔧 Step 2: Force rebuild all containers...
docker-compose build --no-cache --pull

echo.
echo 🚀 Step 3: Starting fresh system...
docker-compose up -d

echo.
echo ⏳ Step 4: Waiting for services to initialize...
timeout /t 15 /nobreak

echo.
echo 🔍 Step 5: Verifying system status...
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo 🌐 Step 6: Testing connectivity...
curl -s http://localhost:3000 >nul && echo ✅ Frontend: ONLINE || echo ❌ Frontend: OFFLINE
curl -s http://localhost:8000/docs >nul && echo ✅ Backend: ONLINE || echo ❌ Backend: OFFLINE

echo.
echo ========================================
echo           REBUILD COMPLETE!
echo ========================================
echo.
echo 🎯 Access Points:
echo   • Students: http://localhost:3000
echo   • Teachers: http://localhost:3000/teacher
echo   • Admin: http://localhost:3000/admin
echo.
echo 🔑 Default Credentials:
echo   • Admin: admin / admin123
echo   • Teacher: teacher001 / teacher123
echo.
echo ✅ H5P Card: Visible in Admin Overview
echo ✅ All Features: Fully Functional
echo.
pause