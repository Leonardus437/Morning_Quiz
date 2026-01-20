@echo off
echo ========================================
echo  Docker System Verification
echo ========================================
echo.

echo Checking Docker installation...
docker --version
if errorlevel 1 (
    echo [ERROR] Docker not found! Please install Docker Desktop.
    pause
    exit /b 1
)
echo.

echo Checking Docker Compose...
docker-compose --version
if errorlevel 1 (
    echo [ERROR] Docker Compose not found!
    pause
    exit /b 1
)
echo.

echo Checking if Docker is running...
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo Please start Docker Desktop.
    pause
    exit /b 1
)
echo [OK] Docker is running
echo.

echo Checking containers...
docker-compose ps
echo.

echo Checking images...
docker images | findstr tvet
echo.

echo Testing backend...
curl -s http://localhost:8000/health
echo.
echo.

echo Testing frontend...
curl -s -o nul -w "Frontend Status: %%{http_code}\n" http://localhost:3000
echo.

echo ========================================
echo  Verification Complete
echo ========================================
pause
