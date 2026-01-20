@echo off
echo Stopping Morning Quiz System...
echo.

docker-compose down

if %errorlevel% equ 0 (
    echo.
    echo ✅ Morning Quiz System stopped successfully!
) else (
    echo.
    echo ❌ Error stopping the system.
)

echo.
pause