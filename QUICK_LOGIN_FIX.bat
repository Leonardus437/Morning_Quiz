@echo off
echo ========================================
echo TVET Quiz System - Quick Login Fix
echo ========================================
echo.

echo 🔄 Step 1: Stopping any running containers...
docker-compose down

echo.
echo 🔄 Step 2: Clearing Docker cache...
docker system prune -f

echo.
echo 🔄 Step 3: Starting fresh containers...
docker-compose up -d

echo.
echo ⏳ Step 4: Waiting for services to start...
timeout /t 10 /nobreak

echo.
echo 🔐 Step 5: Verifying login system...
python verify_login.py

echo.
echo ========================================
echo Quick Fix Complete!
echo ========================================
echo.
echo 📋 Default Login Credentials:
echo    DOS/Admin:  admin / admin123
echo    Teacher:    teacher001 / teacher123
echo    Student:    student001 / pass123
echo.
echo 🌐 Access URLs:
echo    Student Portal: http://localhost:3000
echo    Teacher Portal: http://localhost:3000/teacher
echo    DOS Portal:     http://localhost:3000/admin
echo.
pause