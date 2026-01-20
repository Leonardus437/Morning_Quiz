@echo off
echo Testing Morning Quiz System...
echo.

echo Step 1: Checking Docker status...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running
    echo.
    echo Please:
    echo 1. Open Docker Desktop
    echo 2. Wait for it to fully start
    echo 3. Run this script again
    echo.
    pause
    exit /b 1
)

echo ✅ Docker is running
echo.

echo Step 2: Starting Morning Quiz System...
docker-compose up -d

if %errorlevel% equ 0 (
    echo.
    echo ✅ System started successfully!
    echo.
    echo 🌐 Access URLs:
    echo   Admin Panel: http://localhost:3000/admin
    echo   Student Access: http://localhost:3000
    echo   LAN Access: http://192.168.254.61:3000
    echo.
    echo 🔑 Default Logins:
    echo   Admin: admin / admin123
    echo   Student: student001 / pass123
    echo.
    echo Opening admin panel...
    timeout /t 3 >nul
    start http://localhost:3000/admin
) else (
    echo ❌ Failed to start system
    echo Check the error messages above
)

echo.
pause