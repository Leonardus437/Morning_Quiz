@echo off
echo ========================================
echo TVET Quiz System - Dependency Checker
echo ========================================
echo.

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [✓] Running as Administrator
) else (
    echo [✗] ERROR: This script must be run as Administrator
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo.
echo Checking system dependencies...
echo.

:: 1. Check Docker Desktop
echo [1/5] Checking Docker Desktop...
docker --version >nul 2>&1
if %errorLevel% == 0 (
    echo [✓] Docker is installed
    docker info >nul 2>&1
    if %errorLevel% == 0 (
        echo [✓] Docker is running
    ) else (
        echo [!] Docker is installed but not running
        echo Please start Docker Desktop and try again
        pause
        exit /b 1
    )
) else (
    echo [✗] Docker Desktop is NOT installed
    echo.
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop/
    echo After installation, restart your computer and run this script again
    pause
    exit /b 1
)

:: 2. Check Docker Compose
echo [2/5] Checking Docker Compose...
docker-compose --version >nul 2>&1
if %errorLevel% == 0 (
    echo [✓] Docker Compose is available
) else (
    echo [✗] Docker Compose is NOT available
    echo Docker Compose should come with Docker Desktop
    echo Please reinstall Docker Desktop
    pause
    exit /b 1
)

:: 3. Check Python (for optional local development)
echo [3/5] Checking Python...
python --version >nul 2>&1
if %errorLevel% == 0 (
    echo [✓] Python is installed
) else (
    echo [!] Python is NOT installed (optional for local development)
    echo You can install Python from: https://www.python.org/downloads/
)

:: 4. Check Node.js (for optional frontend development)
echo [4/5] Checking Node.js...
node --version >nul 2>&1
if %errorLevel% == 0 (
    echo [✓] Node.js is installed
) else (
    echo [!] Node.js is NOT installed (optional for frontend development)
    echo You can install Node.js from: https://nodejs.org/
)

:: 5. Check network ports
echo [5/5] Checking required ports...
netstat -an | findstr ":3000" >nul 2>&1
if %errorLevel% == 0 (
    echo [!] Port 3000 is in use - will need to stop existing service
) else (
    echo [✓] Port 3000 is available
)

netstat -an | findstr ":8000" >nul 2>&1
if %errorLevel% == 0 (
    echo [!] Port 8000 is in use - will need to stop existing service
) else (
    echo [✓] Port 8000 is available
)

netstat -an | findstr ":5432" >nul 2>&1
if %errorLevel% == 0 (
    echo [!] Port 5432 is in use - will need to stop existing service
) else (
    echo [✓] Port 5432 is available
)

echo.
echo ========================================
echo DEPENDENCY CHECK COMPLETE
echo ========================================
echo.

:: Check if all critical dependencies are met
docker --version >nul 2>&1 && docker info >nul 2>&1 && docker-compose --version >nul 2>&1
if %errorLevel% == 0 (
    echo [✓] ALL CRITICAL DEPENDENCIES ARE READY!
    echo.
    echo You can now start the TVET Quiz System with:
    echo   docker-compose up -d
    echo.
    echo Or use the quick start script:
    echo   start.bat
    echo.
    set /p choice="Would you like to start the system now? (y/n): "
    if /i "%choice%"=="y" (
        echo.
        echo Starting TVET Quiz System...
        docker-compose up -d
        echo.
        echo System started! Access at:
        echo - Teacher Panel: http://localhost:3000/teacher
        echo - Student Access: http://localhost:3000
        echo - Default login: teacher001 / teacher123
    )
) else (
    echo [✗] MISSING CRITICAL DEPENDENCIES
    echo Please install the missing components and run this script again
)

echo.
pause