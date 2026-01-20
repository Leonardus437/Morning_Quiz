@echo off
echo ========================================
echo COMPLETE MORNING QUIZ + RTB SYSTEM RESTART
echo ========================================
echo.

echo 1. Stopping all services...
taskkill /f /im python.exe 2>nul
taskkill /f /im node.exe 2>nul
taskkill /f /im uvicorn.exe 2>nul
echo    Services stopped

echo.
echo 2. Checking system health...
python system_health_check.py
if %errorlevel% neq 0 (
    echo    System health check failed - continuing anyway
)

echo.
echo 3. Initializing DOS teacher registration...
python dos_teacher_registration.py

echo.
echo 4. Starting backend services...
cd backend
start "Backend API" cmd /k "python main.py"
timeout /t 3 /nobreak >nul

echo.
echo 5. Starting RTB system...
start "RTB System" cmd /k "python rtb_complete_api.py"
timeout /t 3 /nobreak >nul

echo.
echo 6. Starting frontend...
cd ..\frontend
start "Frontend" cmd /k "npm run dev"
timeout /t 5 /nobreak >nul

echo.
echo 7. System URLs:
echo    Main System: http://localhost:3000
echo    Backend API: http://localhost:8000/docs
echo    RTB Generator: http://localhost:8000
echo    Admin Panel: http://localhost:3000/admin
echo.

echo 8. Testing system connectivity...
timeout /t 10 /nobreak >nul
curl -s http://localhost:8000/api/health >nul
if %errorlevel% equ 0 (
    echo    ✅ Backend API responding
) else (
    echo    ❌ Backend API not responding
)

curl -s http://localhost:3000 >nul
if %errorlevel% equ 0 (
    echo    ✅ Frontend responding
) else (
    echo    ❌ Frontend not responding
)

echo.
echo ========================================
echo SYSTEM RESTART COMPLETE
echo ========================================
echo.
echo Default Login Credentials:
echo Admin: admin / admin123
echo DOS Admin: dos_admin / dos123
echo.
echo Press any key to open system in browser...
pause >nul

start http://localhost:3000
start http://localhost:8000

echo System opened in browser
pause