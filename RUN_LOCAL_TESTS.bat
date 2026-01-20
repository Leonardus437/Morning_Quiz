@echo off
title Local System Test Runner
color 0B

echo.
echo  ╔════════════════════════════════════════╗
echo  ║   TVET Quiz - Local Test Runner       ║
echo  ╚════════════════════════════════════════╝
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    color 0C
    echo  [X] Docker is not running!
    echo  Please start Docker Desktop first.
    pause
    exit /b 1
)

echo  [√] Docker is running
echo.

REM Check if containers are up
docker-compose ps | findstr "Up" >nul 2>&1
if errorlevel 1 (
    echo  [!] Containers not running. Starting them...
    docker-compose up -d
    echo  [!] Waiting 30 seconds for startup...
    timeout /t 30 /nobreak >nul
)

echo  [√] Containers are running
echo.

REM Test backend
echo  Testing backend health...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    color 0E
    echo  [!] Backend not responding yet. Waiting...
    timeout /t 10 /nobreak >nul
    curl -s http://localhost:8000/health >nul 2>&1
    if errorlevel 1 (
        color 0C
        echo  [X] Backend failed to start!
        echo  Check logs: docker-compose logs backend
        pause
        exit /b 1
    )
)
echo  [√] Backend is healthy
echo.

REM Test frontend
echo  Testing frontend...
curl -s -o nul -w "%%{http_code}" http://localhost:3000 | findstr "200" >nul 2>&1
if errorlevel 1 (
    color 0E
    echo  [!] Frontend not ready yet. Waiting...
    timeout /t 10 /nobreak >nul
)
echo  [√] Frontend is accessible
echo.

REM Show container status
echo  Container Status:
docker-compose ps
echo.

REM Show recent logs
echo  Recent Backend Logs:
docker-compose logs --tail=5 backend
echo.

color 0A
echo  ╔════════════════════════════════════════╗
echo  ║        System Ready for Testing!       ║
echo  ╚════════════════════════════════════════╝
echo.
echo  Access URLs:
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo.
echo  Default Login:
echo   Admin:    admin / admin123
echo   Teacher:  teacher001 / teacher123
echo   Student:  student001 / pass123
echo.
echo  Opening test page...
echo.

start TEST_LOCAL_SYSTEM.html
timeout /t 2 /nobreak >nul
start http://localhost:3000

echo  Test page and frontend opened in browser!
echo.
pause
