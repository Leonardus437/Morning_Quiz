@echo off
echo ========================================
echo TVET Quiz System - Login Verification
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python first.
    pause
    exit /b 1
)

REM Install required packages if needed
echo Installing required packages...
pip install requests >nul 2>&1

REM Run the verification script
echo Running login verification...
echo.
python verify_login.py

echo.
echo ========================================
echo Verification Complete
echo ========================================
pause