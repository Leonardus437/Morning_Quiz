@echo off
title TVET Quiz - Docker Setup
color 0A

echo.
echo  ╔════════════════════════════════════════╗
echo  ║   TVET Quiz System - Docker Setup     ║
echo  ║        One-Click Installation          ║
echo  ╚════════════════════════════════════════╝
echo.

REM Check Docker
docker info >nul 2>&1
if errorlevel 1 (
    color 0C
    echo  [X] Docker is not running!
    echo.
    echo  Please:
    echo  1. Open Docker Desktop
    echo  2. Wait for it to start
    echo  3. Run this script again
    echo.
    pause
    exit /b 1
)

echo  [√] Docker is running
echo.

REM Clean up
echo  Cleaning old containers...
docker-compose down -v >nul 2>&1
docker system prune -f >nul 2>&1
echo  [√] Cleanup complete
echo.

REM Build
echo  Building images (this may take 5-10 minutes)...
docker-compose build --no-cache
if errorlevel 1 (
    color 0C
    echo  [X] Build failed!
    pause
    exit /b 1
)
echo  [√] Build complete
echo.

REM Start
echo  Starting services...
docker-compose up -d
if errorlevel 1 (
    color 0C
    echo  [X] Failed to start!
    pause
    exit /b 1
)
echo  [√] Services started
echo.

REM Wait
echo  Waiting for services to initialize...
timeout /t 15 /nobreak >nul
echo  [√] Ready
echo.

REM Test
echo  Testing system...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo  [!] Backend may need more time
) else (
    echo  [√] Backend is healthy
)
echo.

color 0A
echo  ╔════════════════════════════════════════╗
echo  ║          Setup Complete!               ║
echo  ╚════════════════════════════════════════╝
echo.
echo  Your system is running at:
echo.
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo.
echo  Login with:
echo   Username: admin
echo   Password: admin123
echo.
echo  Press any key to open the system...
pause >nul

start http://localhost:3000
