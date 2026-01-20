@echo off
title TVET Quiz System - Auto Installer
color 0A

echo.
echo  ████████╗██╗   ██╗███████╗████████╗    ██████╗ ██╗   ██╗██╗███████╗
echo  ╚══██╔══╝██║   ██║██╔════╝╚══██╔══╝   ██╔═══██╗██║   ██║██║╚══███╔╝
echo     ██║   ██║   ██║█████╗     ██║      ██║   ██║██║   ██║██║  ███╔╝ 
echo     ██║   ╚██╗ ██╔╝██╔══╝     ██║      ██║▄▄ ██║██║   ██║██║ ███╔╝  
echo     ██║    ╚████╔╝ ███████╗   ██║      ╚██████╔╝╚██████╔╝██║███████╗
echo     ╚═╝     ╚═══╝  ╚══════╝   ╚═╝       ╚══▀▀═╝  ╚═════╝ ╚═╝╚══════╝
echo.
echo                    AUTO INSTALLER & DEPENDENCY CHECKER
echo                           After Computer Format
echo.
echo ================================================================================

:: Check admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] This installer must be run as Administrator
    echo.
    echo Please:
    echo 1. Right-click this file
    echo 2. Select "Run as administrator"
    echo 3. Click "Yes" when prompted
    echo.
    pause
    exit /b 1
)

echo [INFO] Running as Administrator ✓
echo.

:: Step 1: Check Docker
echo [STEP 1/4] Checking Docker Desktop...
docker --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [MISSING] Docker Desktop is not installed
    echo.
    echo Docker Desktop is REQUIRED for this system to work.
    echo.
    echo AUTOMATIC INSTALLATION:
    echo 1. Opening Docker Desktop download page...
    echo 2. Please download and install Docker Desktop
    echo 3. Restart your computer after installation
    echo 4. Run this script again
    echo.
    start https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
) else (
    echo [FOUND] Docker Desktop is installed ✓
    
    :: Check if Docker is running
    docker info >nul 2>&1
    if %errorLevel% neq 0 (
        echo [WARNING] Docker Desktop is installed but not running
        echo [ACTION] Starting Docker Desktop...
        start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
        echo [WAIT] Waiting for Docker to start (this may take 30-60 seconds)...
        
        :: Wait for Docker to start
        :wait_docker
        timeout /t 5 /nobreak >nul
        docker info >nul 2>&1
        if %errorLevel% neq 0 (
            echo [WAIT] Still waiting for Docker...
            goto wait_docker
        )
        echo [SUCCESS] Docker is now running ✓
    ) else (
        echo [SUCCESS] Docker is running ✓
    )
)

:: Step 2: Check Docker Compose
echo.
echo [STEP 2/4] Checking Docker Compose...
docker-compose --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Docker Compose not found
    echo [INFO] Docker Compose should come with Docker Desktop
    echo [ACTION] Please reinstall Docker Desktop
    pause
    exit /b 1
) else (
    echo [SUCCESS] Docker Compose is available ✓
)

:: Step 3: Check and free up ports
echo.
echo [STEP 3/4] Checking required ports...

:: Function to kill process on port
:kill_port
set port=%1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%port%"') do (
    if not "%%a"=="0" (
        echo [ACTION] Freeing up port %port% (PID: %%a)
        taskkill /PID %%a /F >nul 2>&1
    )
)
goto :eof

:: Check and free ports
call :kill_port 3000
call :kill_port 8000
call :kill_port 5432

echo [SUCCESS] Required ports are now available ✓

:: Step 4: Start the system
echo.
echo [STEP 4/4] Starting TVET Quiz System...

:: Stop any existing containers
echo [CLEANUP] Stopping any existing containers...
docker-compose down >nul 2>&1

:: Start the system
echo [START] Building and starting containers...
docker-compose up -d --build

if %errorLevel% == 0 (
    echo.
    echo ================================================================================
    echo                              🎉 SUCCESS! 🎉
    echo ================================================================================
    echo.
    echo Your TVET Quiz System is now running!
    echo.
    echo 📚 TEACHER ACCESS:
    echo    URL: http://localhost:3000/teacher
    echo    Username: teacher001
    echo    Password: teacher123
    echo.
    echo 👨‍🎓 STUDENT ACCESS:
    echo    URL: http://localhost:3000
    echo.
    echo 🌐 NETWORK ACCESS (for other devices):
    echo    Find your IP: run "ipconfig" in Command Prompt
    echo    Share: http://[YOUR-IP]:3000
    echo.
    echo 🔧 SYSTEM CONTROLS:
    echo    Stop system: docker-compose down
    echo    View logs: docker-compose logs
    echo    Restart: docker-compose restart
    echo.
    echo ================================================================================
    
    :: Open the teacher panel
    echo [AUTO] Opening teacher panel in your browser...
    timeout /t 3 /nobreak >nul
    start http://localhost:3000/teacher
    
) else (
    echo.
    echo ================================================================================
    echo                              ❌ ERROR ❌
    echo ================================================================================
    echo.
    echo Failed to start the system. Common solutions:
    echo.
    echo 1. Make sure Docker Desktop is fully started
    echo 2. Check if you have enough disk space
    echo 3. Try running: docker-compose down -v
    echo 4. Then run this installer again
    echo.
    echo For detailed logs, run: docker-compose logs
    echo.
)

echo.
echo Press any key to exit...
pause >nul