@echo off
color 0E
title Development Mode - Auto Reload

echo.
echo ========================================
echo   DEVELOPMENT MODE (Auto-Reload)
echo ========================================
echo.
echo This mode allows you to edit files and see
echo changes INSTANTLY without rebuilding!
echo.
echo ⚠️ IMPORTANT: Keep this window open while developing
echo.
pause

echo.
echo Starting development mode...
echo.

cd frontend

echo Installing dependencies (if needed)...
call npm install

echo.
echo ========================================
echo   DEV SERVER STARTING...
echo ========================================
echo.
echo ✓ Frontend will auto-reload on file changes
echo ✓ Access at: http://localhost:5173
echo ✓ Backend still at: http://localhost:8000
echo.
echo Press Ctrl+C to stop dev server
echo.

call npm run dev

pause
