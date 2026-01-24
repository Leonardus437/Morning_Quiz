@echo off
echo ========================================
echo  Git Initial Setup
echo ========================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed!
    echo.
    echo Please install Git from: https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

echo Git is installed!
echo.

REM Configure git user
echo Setting up Git user configuration...
echo.
set /p GIT_NAME="Enter your name: "
set /p GIT_EMAIL="Enter your email: "

git config --global user.name "%GIT_NAME%"
git config --global user.email "%GIT_EMAIL%"

echo.
echo Git configured successfully!
echo Name: %GIT_NAME%
echo Email: %GIT_EMAIL%
echo.

REM Initialize repository
if not exist .git (
    echo Initializing Git repository...
    git init
    echo.
)

echo Creating .gitattributes for Windows...
echo * text=auto eol=lf > .gitattributes
echo *.bat text eol=crlf >> .gitattributes
echo *.cmd text eol=crlf >> .gitattributes

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo Next step: Run PUSH_TO_GITHUB.bat
echo.
pause
