@echo off
echo TVET Quiz System - Final Starter
echo =================================
echo.

cd /d "f:\SIDE HUSTLE\Morning_Quiz"
echo Current directory: %cd%

echo.
echo Stopping any existing containers...
docker-compose down

echo.
echo Building and starting system (this may take a few minutes first time)...
docker-compose up -d --build

echo.
echo Checking container status...
docker-compose ps

echo.
echo System should be ready!
echo Teacher Panel: http://localhost:3000/teacher
echo Student Access: http://localhost:3000
echo Login: teacher001 / teacher123

echo.
pause