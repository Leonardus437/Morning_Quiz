@echo off
color 0A
echo.
echo ========================================
echo   FINAL FIX - Error Display
echo ========================================
echo.
echo Fixed: [object Object] error display
echo.
echo Rebuilding frontend...
cd frontend
call npm run build
cd ..

echo.
echo Restarting frontend container...
docker-compose stop frontend
docker-compose up -d frontend

echo.
echo ========================================
echo   DONE!
echo ========================================
echo.
echo The error should now show properly!
echo Test at: http://localhost:3000/teacher
echo.
pause
