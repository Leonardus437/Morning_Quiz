@echo off
echo ========================================
echo   TVET Quiz System - Local IP Address
echo ========================================
echo.
echo Share this address with your students:
echo.
ipconfig | findstr /i "IPv4"
echo.
echo Students should access: http://[YOUR-IP]:3000
echo Example: http://10.11.248.208:3000
echo.
echo ========================================
pause
