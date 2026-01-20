@echo off
echo ========================================
echo TVET Quiz System - Verification Script
echo ========================================
echo.

echo [1/4] Checking Docker containers...
docker-compose ps
echo.

echo [2/4] Checking backend endpoint...
curl -X GET http://localhost:8000/health 2>nul
echo.
echo.

echo [3/4] Checking frontend...
curl -I http://localhost:3000 2>nul | findstr "200"
echo.

echo [4/4] Checking backend logs for upload endpoint...
docker logs tvet_quiz-backend-1 2>&1 | findstr "upload-students-file" | findstr "POST"
echo.

echo ========================================
echo Verification Complete!
echo ========================================
echo.
echo Next Steps:
echo 1. Open browser: http://localhost:3000/admin
echo 2. Login with DOS credentials
echo 3. Go to Students tab
echo 4. Click "Upload Students"
echo 5. Select your Excel or PDF file
echo 6. Upload and verify!
echo.
echo If browser shows old version:
echo - Press Ctrl+Shift+Delete to clear cache
echo - Or use Incognito mode (Ctrl+Shift+N)
echo.
pause
