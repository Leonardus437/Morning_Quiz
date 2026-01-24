@echo off
echo ========================================
echo   STOPPING CHAT SYSTEM SERVERS
echo ========================================
echo.

echo Stopping Backend Server (port 8000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /F /PID %%a 2>nul

echo Stopping Frontend Server (port 3002)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3002') do taskkill /F /PID %%a 2>nul

echo.
echo ========================================
echo   ALL SERVERS STOPPED
echo ========================================
echo.
pause
