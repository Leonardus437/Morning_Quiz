@echo off
echo TVET Quiz System - Fixed Starter
echo =================================
echo.

echo Changing to project directory...
cd /d "f:\SIDE HUSTLE\Morning_Quiz"
echo Current directory: %cd%

echo.
echo Checking for docker-compose.yml...
if exist docker-compose.yml (
    echo Found docker-compose.yml!
) else (
    echo ERROR: docker-compose.yml not found in current directory
    goto end
)

echo.
echo Starting system...
docker-compose down
docker-compose up -d

echo.
echo System started!
echo Teacher Panel: http://localhost:3000/teacher
echo Student Access: http://localhost:3000
echo Login: teacher001 / teacher123

:end
echo.
pause