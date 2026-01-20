@echo off
echo Starting Morning Quiz System...
echo.

REM Check if Docker is running
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running or not installed.
    echo Please install Docker Desktop and make sure it's running.
    pause
    exit /b 1
)

echo Docker is running. Starting services...
echo.

REM Start the services
docker-compose up -d

if %errorlevel% equ 0 (
    echo.
    echo ✅ Morning Quiz System started successfully!
    echo.
    echo 📚 Student Access: http://localhost:3000
    echo 👨‍🏫 Admin Panel: http://localhost:3000/admin
    echo.
    echo Default admin login: admin / admin123
    echo Default student login: student001 / pass123
    echo.
    echo To find your PC's IP address for LAN access:
    ipconfig | findstr "IPv4"
    echo.
    echo Press any key to open the admin panel...
    pause >nul
    start http://localhost:3000/admin
) else (
    echo.
    echo ❌ Failed to start the system. Please check the error messages above.
    pause
)