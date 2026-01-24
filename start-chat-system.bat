@echo off
echo ========================================
echo   MODERN CHAT SYSTEM - QUICK START
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "backend" (
    echo ERROR: backend folder not found!
    echo Please run this script from the Morning_Quiz-master directory
    pause
    exit /b 1
)

if not exist "frontend" (
    echo ERROR: frontend folder not found!
    echo Please run this script from the Morning_Quiz-master directory
    pause
    exit /b 1
)

echo [1/4] Installing frontend dependencies...
cd frontend
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install frontend dependencies
    pause
    exit /b 1
)
cd ..

echo.
echo [2/4] Starting Backend Server...
echo Backend will run on: http://localhost:8000
start "Backend Server" cmd /k "cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 /nobreak >nul

echo.
echo [3/4] Starting Frontend Server...
echo Frontend will run on: http://localhost:3002
start "Frontend Server" cmd /k "cd frontend && npm run dev"
timeout /t 5 /nobreak >nul

echo.
echo [4/4] Opening Browser...
timeout /t 3 /nobreak >nul
start http://localhost:3002

echo.
echo ========================================
echo   SERVERS STARTED SUCCESSFULLY!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3002
echo.
echo TEST CREDENTIALS:
echo.
echo Student:  student001 / pass123
echo Teacher:  teacher001 / teacher123
echo Admin:    admin / admin123
echo.
echo ========================================
echo   LOOK FOR THE CHAT BUTTON!
echo ========================================
echo.
echo After logging in, look for the beautiful
echo gradient chat button in the bottom-right
echo corner with pulse animation!
echo.
echo Press any key to close this window...
echo (Servers will keep running in background)
pause >nul
