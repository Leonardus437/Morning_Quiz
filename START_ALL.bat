@echo off
echo ========================================
echo TVET Quiz System - Phase 1 Launcher
echo ========================================
echo.
echo This will open 2 windows:
echo 1. Backend Server (keep running)
echo 2. Frontend Server (keep running)
echo.
echo Press any key to start...
pause >nul

echo.
echo Starting Backend Server...
start "Backend Server" cmd /k "cd /d %~dp0 && 1_START_BACKEND.bat"

echo Waiting 5 seconds for backend to start...
timeout /t 5 >nul

echo.
echo Starting Frontend Server...
start "Frontend Server" cmd /k "cd /d %~dp0 && 4_START_FRONTEND.bat"

echo.
echo ========================================
echo Both servers are starting!
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Keep both windows open!
echo.
echo Press any key to create test questions...
pause >nul

echo.
echo Creating test questions...
python test_advanced_questions.py

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Open browser: http://localhost:3000/teacher
echo Login: teacher001 / teacher123
echo.
pause
