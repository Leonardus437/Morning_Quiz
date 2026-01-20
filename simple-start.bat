@echo off
echo TVET Quiz System - Simple Starter
echo ================================
echo.

echo Checking Docker...
docker --version
if %errorLevel% neq 0 (
    echo ERROR: Docker not found
    goto end
)

echo Docker found! Checking if running...
docker info
if %errorLevel% neq 0 (
    echo ERROR: Docker not running - please start Docker Desktop
    goto end
)

echo Docker is running! Starting system...
docker-compose down
docker-compose up -d

echo.
echo System should be starting...
echo Teacher Panel: http://localhost:3000/teacher
echo Student Access: http://localhost:3000
echo Login: teacher001 / teacher123
echo.

:end
echo.
echo Press any key to close...
pause