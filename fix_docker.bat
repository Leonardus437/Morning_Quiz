@echo off
<<<<<<< HEAD
title TVET Quiz - Docker Troubleshooter
color 0E

:MENU
cls
echo.
echo  ╔════════════════════════════════════════╗
echo  ║   TVET Quiz - Docker Troubleshooter   ║
echo  ╚════════════════════════════════════════╝
echo.
echo  1. Check Docker Status
echo  2. View Container Logs
echo  3. Restart All Services
echo  4. Rebuild Everything (Clean)
echo  5. Fix Port Conflicts
echo  6. Reset Database
echo  7. Open System URLs
echo  8. Exit
echo.
set /p choice="Select option (1-8): "

if "%choice%"=="1" goto CHECK
if "%choice%"=="2" goto LOGS
if "%choice%"=="3" goto RESTART
if "%choice%"=="4" goto REBUILD
if "%choice%"=="5" goto PORTS
if "%choice%"=="6" goto RESETDB
if "%choice%"=="7" goto URLS
if "%choice%"=="8" exit
goto MENU

:CHECK
cls
echo Checking Docker Status...
echo.
docker --version
echo.
docker-compose --version
echo.
docker info | findstr "Server Version"
echo.
echo Container Status:
docker-compose ps
echo.
echo Images:
docker images | findstr "morning_quiz\|postgres"
echo.
pause
goto MENU

:LOGS
cls
echo Select logs to view:
echo 1. All services
echo 2. Backend only
echo 3. Frontend only
echo 4. Database only
echo.
set /p logchoice="Select (1-4): "

if "%logchoice%"=="1" docker-compose logs --tail=50
if "%logchoice%"=="2" docker-compose logs backend --tail=50
if "%logchoice%"=="3" docker-compose logs frontend --tail=50
if "%logchoice%"=="4" docker-compose logs db --tail=50
echo.
pause
goto MENU

:RESTART
cls
echo Restarting all services...
docker-compose restart
echo.
echo Waiting for services...
timeout /t 10 /nobreak >nul
echo.
echo Status:
docker-compose ps
echo.
pause
goto MENU

:REBUILD
cls
echo WARNING: This will rebuild everything from scratch!
echo All data will be preserved in volumes.
echo.
set /p confirm="Continue? (Y/N): "
if /i not "%confirm%"=="Y" goto MENU

echo.
echo Stopping containers...
docker-compose down
echo.
echo Removing old images...
docker-compose rm -f
echo.
echo Rebuilding...
docker-compose build --no-cache
echo.
echo Starting...
docker-compose up -d
echo.
echo Waiting...
timeout /t 15 /nobreak >nul
echo.
echo Done!
pause
goto MENU

:PORTS
cls
echo Checking port usage...
echo.
echo Port 3000 (Frontend):
netstat -ano | findstr :3000
echo.
echo Port 8000 (Backend):
netstat -ano | findstr :8000
echo.
echo Port 5432 (Database):
netstat -ano | findstr :5432
echo.
echo.
set /p killports="Kill processes on these ports? (Y/N): "
if /i not "%killports%"=="Y" goto MENU

echo.
echo Stopping Docker containers first...
docker-compose down
echo.
echo Killing port processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5432') do taskkill /PID %%a /F 2>nul
echo.
echo Ports cleared! Starting services...
docker-compose up -d
echo.
pause
goto MENU

:RESETDB
cls
echo WARNING: This will delete ALL data!
echo - All quizzes will be deleted
echo - All students will be deleted
echo - All results will be deleted
echo.
set /p confirm="Are you sure? Type YES to confirm: "
if /i not "%confirm%"=="YES" goto MENU

echo.
echo Stopping services...
docker-compose down -v
echo.
echo Starting fresh...
docker-compose up -d
echo.
echo Database reset complete!
echo Default accounts restored:
echo   Admin: admin / admin123
echo   Teacher: teacher001 / teacher123
echo   Student: student001 / pass123
echo.
pause
goto MENU

:URLS
cls
echo Opening system URLs...
start http://localhost:3000
timeout /t 2 /nobreak >nul
start http://localhost:8000/docs
echo.
echo URLs opened in browser!
pause
goto MENU
=======
echo Fixing Docker issues...
echo.
echo 1. Stopping any running containers...
docker-compose down
echo.
echo 2. Removing old images...
docker system prune -f
echo.
echo 3. Building fresh images...
docker-compose build --no-cache
echo.
echo 4. Starting system...
docker-compose up -d
echo.
echo Done! System should be running now.
pause
>>>>>>> a6f256911bd91da0b979b46a8d9484a08d4142a9
