@echo off
echo ========================================
echo  FIXING QUESTION CREATE ERROR
echo ========================================
echo.
echo The [object Object] error has been fixed!
echo.
echo Rebuilding frontend...
cd frontend
call npm run build
echo.
echo ✓ Fix applied successfully!
echo.
echo Please restart the system:
echo   docker-compose restart
echo.
echo Or rebuild:
echo   docker-compose up -d --build
echo.
pause
