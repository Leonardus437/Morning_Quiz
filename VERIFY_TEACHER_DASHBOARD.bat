@echo off
echo ========================================
echo Teacher Dashboard Verification
echo ========================================
echo.

echo [1/3] Checking containers...
docker ps --filter "name=tvet_quiz" --format "table {{.Names}}\t{{.Status}}"
echo.

echo [2/3] Checking frontend...
timeout /t 2 /nobreak >nul
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Frontend is accessible at http://localhost:3000
) else (
    echo ❌ Frontend is not accessible
)
echo.

echo [3/3] Checking backend...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend is accessible at http://localhost:8000
) else (
    echo ❌ Backend is not accessible
)
echo.

echo ========================================
echo Verification Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Clear browser cache (Ctrl + Shift + Delete)
echo 2. Hard refresh (Ctrl + Shift + R)
echo 3. Go to http://localhost:3000/teacher
echo 4. Login and test all features
echo.
echo Expected features:
echo ✅ Dashboard with statistics
echo ✅ Notifications with real-time updates
echo ✅ Advanced Question Builder (AI Parser, Templates, Manual)
echo ✅ Create Quiz with filters
echo ✅ My Quizzes with broadcast
echo ✅ My Courses
echo ✅ Students management
echo ✅ Results with download
echo.
pause
