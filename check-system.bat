@echo off
echo ========================================
echo   SYSTEM CHECK - CHAT SYSTEM
echo ========================================
echo.

set "allGood=1"

echo Checking requirements...
echo.

REM Check Node.js
echo [1/5] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [X] Node.js NOT FOUND
    echo     Install from: https://nodejs.org
    set "allGood=0"
) else (
    for /f "tokens=*" %%i in ('node --version') do set nodeVersion=%%i
    echo [OK] Node.js found: %nodeVersion%
)

REM Check npm
echo [2/5] Checking npm...
npm --version >nul 2>&1
if errorlevel 1 (
    echo [X] npm NOT FOUND
    set "allGood=0"
) else (
    for /f "tokens=*" %%i in ('npm --version') do set npmVersion=%%i
    echo [OK] npm found: %npmVersion%
)

REM Check Python
echo [3/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python NOT FOUND
    echo     Install from: https://python.org
    set "allGood=0"
) else (
    for /f "tokens=*" %%i in ('python --version') do set pythonVersion=%%i
    echo [OK] Python found: %pythonVersion%
)

REM Check backend folder
echo [4/5] Checking backend folder...
if exist "backend" (
    echo [OK] Backend folder found
) else (
    echo [X] Backend folder NOT FOUND
    set "allGood=0"
)

REM Check frontend folder
echo [5/5] Checking frontend folder...
if exist "frontend" (
    echo [OK] Frontend folder found
) else (
    echo [X] Frontend folder NOT FOUND
    set "allGood=0"
)

echo.
echo ========================================

if "%allGood%"=="1" (
    echo   ALL CHECKS PASSED!
    echo ========================================
    echo.
    echo You're ready to start the chat system!
    echo.
    echo Run: start-chat-system.bat
    echo.
) else (
    echo   SOME CHECKS FAILED
    echo ========================================
    echo.
    echo Please install missing requirements
    echo before starting the chat system.
    echo.
)

pause
