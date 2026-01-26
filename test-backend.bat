@echo off
echo ========================================
echo   Testing Backend Integration
echo ========================================
echo.

echo [1/2] Checking if backend is running...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Backend not running!
    echo Please start backend: cd backend ^&^& python main.py
    pause
    exit /b 1
)
echo ✅ Backend is running

echo.
echo [2/2] Testing database migration...
curl -s http://localhost:8000/questions?limit=1 >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Database not ready!
    pause
    exit /b 1
)
echo ✅ Database is ready

echo.
echo ========================================
echo   All Systems Ready! ✅
echo ========================================
echo.
echo Next steps:
echo 1. Run: deploy-frontend.bat
echo 2. Test at: https://tsskwizi.pages.dev
echo.
pause
