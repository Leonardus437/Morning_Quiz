@echo off
echo Checking Morning Quiz System Requirements...
echo.

REM Check Docker Desktop
echo [1/2] Checking Docker Desktop...
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Docker is installed
    docker --version
) else (
    echo ❌ Docker is NOT installed
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop/
    goto :end
)

echo.

REM Check Docker Compose
echo [2/2] Checking Docker Compose...
docker-compose --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Docker Compose is available
    docker-compose --version
) else (
    echo ❌ Docker Compose is NOT available
    goto :end
)

echo.

REM Check if Docker is running
echo Checking if Docker is running...
docker info >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Docker is running
) else (
    echo ❌ Docker is not running
    echo Please start Docker Desktop and wait for it to fully load
    goto :end
)

echo.
echo ✅ All requirements met! You can run the Morning Quiz System.
echo.
echo Next steps:
echo 1. Run: start.bat
echo 2. Wait for "System started successfully" message
echo 3. Open: http://localhost:3000/admin

:end
echo.
pause