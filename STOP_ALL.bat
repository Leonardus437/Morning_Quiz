@echo off
echo ========================================
echo Stopping All Servers...
echo ========================================

echo Stopping Python (Backend)...
taskkill /F /IM python.exe 2>nul
if %errorlevel% equ 0 (
    echo Backend stopped
) else (
    echo No backend running
)

echo.
echo Stopping Node (Frontend)...
taskkill /F /IM node.exe 2>nul
if %errorlevel% equ 0 (
    echo Frontend stopped
) else (
    echo No frontend running
)

echo.
echo ========================================
echo All servers stopped!
echo ========================================
pause
