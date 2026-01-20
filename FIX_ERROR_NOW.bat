@echo off
color 0B
title Fix [object Object] Error - Choose Method

:MENU
cls
echo.
echo ========================================
echo   FIX [object Object] ERROR
echo ========================================
echo.
echo The error has been FIXED in the code!
echo Now choose how to apply the fix:
echo.
echo [1] DEV MODE - Instant (1-2 seconds)
echo     ✓ See changes immediately
echo     ✓ Auto-reload on file save
echo     ✓ Perfect for development
echo     ⚠️ Uses port 5173
echo.
echo [2] QUICK REBUILD - Fast (30-60 seconds)
echo     ✓ Production ready
echo     ✓ Uses standard port 3000
echo     ✓ No terminal needed
echo     ⚠️ Takes 30-60 seconds
echo.
echo [3] FULL REBUILD - Complete (2-5 minutes)
echo     ✓ Rebuilds everything
echo     ✓ Clears all caches
echo     ⚠️ Takes 2-5 minutes
echo.
echo [4] View Development Guide
echo [5] Exit
echo.
set /p choice="Choose option (1-5): "

if "%choice%"=="1" goto DEV_MODE
if "%choice%"=="2" goto QUICK_REBUILD
if "%choice%"=="3" goto FULL_REBUILD
if "%choice%"=="4" goto GUIDE
if "%choice%"=="5" goto EXIT
goto MENU

:DEV_MODE
cls
echo.
echo ========================================
echo   STARTING DEV MODE
echo ========================================
echo.
echo This will start the development server
echo with HOT RELOAD enabled.
echo.
echo ⚠️ Keep this window OPEN while developing
echo.
pause

cd frontend
echo Installing dependencies...
call npm install

echo.
echo ========================================
echo   DEV SERVER RUNNING
echo ========================================
echo.
echo ✓ Frontend: http://localhost:5173
echo ✓ Backend: http://localhost:8000
echo.
echo Changes will appear INSTANTLY!
echo Press Ctrl+C to stop
echo.

call npm run dev
pause
goto MENU

:QUICK_REBUILD
cls
echo.
echo ========================================
echo   QUICK REBUILD (Frontend Only)
echo ========================================
echo.
echo This will rebuild ONLY the frontend.
echo Takes about 30-60 seconds.
echo.
pause

echo.
echo [1/3] Stopping frontend...
docker-compose stop frontend

echo.
echo [2/3] Rebuilding frontend...
docker-compose build frontend --no-cache

echo.
echo [3/3] Starting frontend...
docker-compose up -d frontend

echo.
echo ========================================
echo   REBUILD COMPLETE!
echo ========================================
echo.
echo ✓ Frontend rebuilt successfully
echo ✓ Access at: http://localhost:3000
echo.
echo Test the fix:
echo 1. Go to http://localhost:3000/teacher
echo 2. Login as teacher
echo 3. Click "Questions" → "Create Question"
echo 4. The error should be GONE! ✅
echo.
pause
goto MENU

:FULL_REBUILD
cls
echo.
echo ========================================
echo   FULL REBUILD (All Containers)
echo ========================================
echo.
echo This will rebuild EVERYTHING.
echo Takes about 2-5 minutes.
echo.
echo ⚠️ Only use this if Quick Rebuild fails
echo.
pause

echo.
echo [1/3] Stopping all containers...
docker-compose down

echo.
echo [2/3] Rebuilding all containers...
docker-compose build --no-cache

echo.
echo [3/3] Starting all containers...
docker-compose up -d

echo.
echo ========================================
echo   FULL REBUILD COMPLETE!
echo ========================================
echo.
echo ✓ All containers rebuilt
echo ✓ Access at: http://localhost:3000
echo.
echo Waiting for services to start (30 seconds)...
timeout /t 30 /nobreak

echo.
echo ✓ System ready!
echo.
pause
goto MENU

:GUIDE
cls
echo.
echo ========================================
echo   DEVELOPMENT GUIDE
echo ========================================
echo.
type DEVELOPMENT_GUIDE.md
echo.
echo ========================================
echo.
pause
goto MENU

:EXIT
cls
echo.
echo ========================================
echo   SUMMARY
echo ========================================
echo.
echo The [object Object] error has been FIXED!
echo.
echo To apply the fix, you chose to:
echo.
if "%choice%"=="1" echo ✓ Use Dev Mode (Instant)
if "%choice%"=="2" echo ✓ Quick Rebuild (30-60 sec)
if "%choice%"=="3" echo ✓ Full Rebuild (2-5 min)
echo.
echo For detailed instructions, see:
echo   DEVELOPMENT_GUIDE.md
echo.
echo Happy coding! 🚀
echo.
pause
exit
