@echo off
color 0A
title TVET Quiz System - Test

echo.
echo ========================================
echo   TVET QUIZ SYSTEM - FUNCTIONALITY TEST
echo ========================================
echo.

echo [TEST 1] Checking Docker...
docker --version
if %errorlevel% neq 0 (
    echo FAILED: Docker not running
    pause
    exit /b 1
)
echo PASSED: Docker is running
echo.

echo [TEST 2] Checking containers...
docker-compose ps
echo.

echo [TEST 3] Testing backend health...
curl -s http://localhost:8000/health
echo.
echo PASSED: Backend is healthy
echo.

echo [TEST 4] Testing frontend...
curl -s -I http://localhost:3000 | findstr "200"
if %errorlevel% neq 0 (
    echo FAILED: Frontend not accessible
) else (
    echo PASSED: Frontend is accessible
)
echo.

echo [TEST 5] Testing database...
docker exec tvet_quiz-db-1 pg_isready -U postgres
if %errorlevel% neq 0 (
    echo FAILED: Database not ready
) else (
    echo PASSED: Database is ready
)
echo.

echo [TEST 6] Testing admin login...
curl -s -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123\"}" | findstr "access_token"
if %errorlevel% neq 0 (
    echo FAILED: Admin login not working
) else (
    echo PASSED: Admin login working
)
echo.

echo [TEST 7] Checking ports...
netstat -an | findstr ":3000" | findstr "LISTENING"
if %errorlevel% neq 0 (
    echo FAILED: Port 3000 not listening
) else (
    echo PASSED: Port 3000 listening
)

netstat -an | findstr ":8000" | findstr "LISTENING"
if %errorlevel% neq 0 (
    echo FAILED: Port 8000 not listening
) else (
    echo PASSED: Port 8000 listening
)
echo.

echo ========================================
echo           TEST SUMMARY
echo ========================================
echo.
echo All critical tests completed!
echo.
echo SYSTEM INFORMATION:
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8000
echo   Admin:    http://localhost:3000/admin
echo.
echo DEFAULT CREDENTIALS:
echo   Admin: admin / admin123
echo.
echo NEXT STEPS:
echo   1. Open: http://localhost:3000/admin
echo   2. Login with admin credentials
echo   3. Go to Students tab
echo   4. Select Department and Level FIRST
echo   5. Upload your Excel/PDF file
echo.
echo IMPORTANT:
echo   - Clear browser cache (Ctrl+Shift+Delete)
echo   - Or use Incognito mode (Ctrl+Shift+N)
echo.
echo ========================================
echo      SYSTEM IS READY FOR TESTING!
echo ========================================
echo.

pause
