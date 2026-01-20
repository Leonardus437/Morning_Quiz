@echo off
echo ========================================
echo  TVET Quiz System - Docker Setup
echo  Complete Rebuild for New PC
echo ========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo [OK] Docker is running
echo.

echo Step 1: Cleaning up old containers and images...
echo ================================================
docker-compose down -v 2>nul
docker system prune -af --volumes
echo [OK] Cleanup complete
echo.

echo Step 2: Building Docker images...
echo ==================================
docker-compose build --no-cache
if errorlevel 1 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)
echo [OK] Images built successfully
echo.

echo Step 3: Starting containers...
echo ===============================
docker-compose up -d
if errorlevel 1 (
    echo [ERROR] Failed to start containers!
    pause
    exit /b 1
)
echo [OK] Containers started
echo.

echo Step 4: Waiting for services to be ready...
echo ============================================
timeout /t 10 /nobreak >nul
echo [OK] Services should be ready
echo.

echo Step 5: Checking container status...
echo =====================================
docker-compose ps
echo.

echo Step 6: Testing backend health...
echo ==================================
timeout /t 5 /nobreak >nul
curl -s http://localhost:8000/health
echo.
echo.

echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo Your TVET Quiz System is now running:
echo.
echo  Frontend: http://localhost:3000
echo  Backend:  http://localhost:8000
echo  API Docs: http://localhost:8000/docs
echo  Database: localhost:5432
echo.
echo Default Login:
echo  Admin:    admin / admin123
echo  Teacher:  teacher001 / teacher123
echo  Student:  student001 / pass123
echo.
echo To view logs:    docker-compose logs -f
echo To stop system:  docker-compose down
echo To restart:      docker-compose restart
echo.
pause
