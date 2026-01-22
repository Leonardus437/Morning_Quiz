@echo off
echo ========================================
echo   TVET Quiz System - Quick Setup
echo ========================================
echo.

echo [1/3] Starting Docker containers...
docker-compose up -d --build

echo.
echo [2/3] Waiting for services to start...
timeout /t 10 /nobreak

echo.
echo [3/3] Setup complete!
echo.
echo ========================================
echo   ACCESS YOUR SYSTEM:
echo ========================================
echo.
echo   Student Portal:  http://localhost:3000
echo   Teacher Portal:  http://localhost:3000/teacher
echo   Admin Portal:    http://localhost:3000/admin
echo.
echo   Default Admin:   admin / admin123
echo   Default Teacher: teacher001 / teacher123
echo.
echo ========================================
echo.
pause
