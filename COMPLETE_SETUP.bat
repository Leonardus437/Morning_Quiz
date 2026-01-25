@echo off
title TVET Quiz System - Complete Setup
color 0A

echo ========================================
echo    TVET Quiz System - Complete Setup
echo ========================================
echo.

echo [1/5] Stopping any running servers...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
netstat -ano | findstr :8000 >nul && (
    echo Killing process on port 8000...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do taskkill /f /pid %%a >nul 2>&1
)
netstat -ano | findstr :3000 >nul && (
    echo Killing process on port 3000...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do taskkill /f /pid %%a >nul 2>&1
)
echo Done.
echo.

echo [2/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8+
    pause
    exit /b 1
)
echo Python found.
echo.

echo [3/5] Installing backend dependencies...
cd /d "%~dp0backend"
pip install -r requirements.txt >nul 2>&1
echo Backend dependencies installed.
echo.

echo [4/5] Starting backend server...
start "Backend Server" cmd /k "echo Backend Server Running... && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 >nul
echo Backend server started on http://localhost:8000
echo.

echo [5/5] Starting frontend server...
cd /d "%~dp0frontend"
start "Frontend Server" cmd /k "echo Frontend Server Running... && npm run dev -- --host 0.0.0.0 --port 3000"
timeout /t 5 >nul
echo Frontend server starting on http://localhost:3000
echo.

echo ========================================
echo    SETUP COMPLETE!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo Teacher:  http://localhost:3000/teacher
echo.
echo Default Login:
echo Username: teacher001
echo Password: teacher123
echo.
echo Press any key to open teacher panel...
pause >nul
start http://localhost:3000/teacher