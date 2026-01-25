@echo off
echo ========================================
echo Checking Backend Status...
echo ========================================
curl http://localhost:8000/health
echo.
echo.
echo If you see JSON response above, backend is running!
echo If you see error, run 1_START_BACKEND.bat first
pause
