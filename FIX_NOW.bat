@echo off
cls
echo.
echo ================================================
echo   CREDENTIALS FIX - RESTART FRONTEND
echo ================================================
echo.
echo This will restart the frontend with the fix applied.
echo.
pause

echo.
echo Restarting frontend container...
docker-compose restart frontend

echo.
echo Waiting for frontend to start...
timeout /t 15 /nobreak > nul

echo.
echo ================================================
echo   FIX APPLIED! NOW DO THIS:
echo ================================================
echo.
echo 1. Close ALL browser windows
echo.
echo 2. Open NEW incognito window:
echo    Press: Ctrl + Shift + N
echo.
echo 3. Go to: http://localhost:3000/admin
echo.
echo 4. Login: admin / admin123
echo.
echo 5. Go to Students tab
echo    - Verify students are there
echo.
echo 6. Click "Generate Credentials"
echo    - Select department (EXACT name)
echo    - Select level (EXACT name)
echo    - Click "Generate PDF"
echo.
echo 7. PDF should download!
echo.
echo ================================================
echo.
echo Read SIMPLE_FIX_GUIDE.md for full instructions
echo.
pause
