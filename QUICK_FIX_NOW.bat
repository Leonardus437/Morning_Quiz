@echo off
echo.
echo ========================================
echo   QUICK FIX - Credentials Generation
echo ========================================
echo.
echo This will:
echo 1. Restart the frontend container
echo 2. Show you the debug tool
echo 3. Guide you through testing
echo.
pause

echo.
echo [1/3] Restarting frontend container...
docker-compose restart frontend

echo.
echo Waiting for frontend to be ready...
timeout /t 10 /nobreak > nul

echo.
echo [2/3] Checking container status...
docker-compose ps

echo.
echo [3/3] Opening debug tool...
start DEBUG_LESSONS.html

echo.
echo ========================================
echo   NEXT STEPS:
echo ========================================
echo.
echo 1. Clear your browser cache:
echo    - Press Ctrl + Shift + Delete
echo    - Select "All time"
echo    - Check "Cached images and files"
echo    - Click "Clear data"
echo.
echo 2. Open NEW incognito window:
echo    - Press Ctrl + Shift + N
echo    - Go to: http://localhost:3000/admin
echo.
echo 3. Test credentials generation:
echo    - Login as admin
echo    - Go to Students tab
echo    - Click "Generate Credentials"
echo    - Select department and level
echo    - Click "Generate PDF"
echo.
echo 4. Use the debug tool that just opened to:
echo    - Check students data
echo    - Verify department/level names
echo    - Test credentials generation
echo.
echo ========================================
echo.
echo Read SOLUTION_APPLIED.md for full details
echo.
pause
