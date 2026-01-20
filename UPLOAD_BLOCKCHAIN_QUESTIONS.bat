@echo off
color 0A
title Upload Blockchain Questions - TVET Quiz System

echo.
echo ========================================
echo   BLOCKCHAIN QUESTIONS UPLOAD WIZARD
echo ========================================
echo.
echo This wizard will help you upload the 50
echo Blockchain Fundamentals questions.
echo.
pause

:MENU
cls
echo.
echo ========================================
echo   BLOCKCHAIN QUESTIONS UPLOAD
echo ========================================
echo.
echo What would you like to do?
echo.
echo [1] View Upload Instructions
echo [2] Open Upload Interface (HTML)
echo [3] Check if Backend is Running
echo [4] View Question File
echo [5] Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto INSTRUCTIONS
if "%choice%"=="2" goto OPEN_INTERFACE
if "%choice%"=="3" goto CHECK_BACKEND
if "%choice%"=="4" goto VIEW_FILE
if "%choice%"=="5" goto EXIT
goto MENU

:INSTRUCTIONS
cls
echo.
echo ========================================
echo   UPLOAD INSTRUCTIONS
echo ========================================
echo.
echo STEP 1: Ensure Backend is Running
echo   - Run: docker-compose up -d
echo   - Or: start.bat
echo.
echo STEP 2: Create Blockchain Lesson (if needed)
echo   - Login as DOS/Admin
echo   - Go to Lessons Management
echo   - Create: "Blockchain Fundamentals"
echo   - Code: BCFND301
echo   - Department: Software Development
echo   - Level: Level 5
echo.
echo STEP 3: Assign Lesson to Teacher
echo   - Go to Teacher Management
echo   - Select your teacher account
echo   - Assign "Blockchain Fundamentals" lesson
echo.
echo STEP 4: Upload Questions
echo   - Open upload_blockchain_questions.html
echo   - Login with teacher credentials
echo   - Select Department: Software Development
echo   - Select Level: Level 5
echo   - Select Lesson: Blockchain Fundamentals
echo   - Choose file: Blockchain_Fundamentals_50_Questions.txt
echo   - Click "Upload Questions"
echo.
echo STEP 5: Verify Upload
echo   - Login as teacher
echo   - Go to Questions section
echo   - Filter by Blockchain Fundamentals
echo   - Should see 50 questions
echo.
echo ========================================
echo.
pause
goto MENU

:OPEN_INTERFACE
cls
echo.
echo ========================================
echo   OPENING UPLOAD INTERFACE
echo ========================================
echo.
echo Opening upload_blockchain_questions.html...
echo.
start upload_blockchain_questions.html
echo.
echo ✓ Interface opened in your default browser
echo.
echo NEXT STEPS:
echo 1. Login with your teacher credentials
echo 2. Fill in the form
echo 3. Select Blockchain_Fundamentals_50_Questions.txt
echo 4. Click "Upload Questions"
echo.
pause
goto MENU

:CHECK_BACKEND
cls
echo.
echo ========================================
echo   CHECKING BACKEND STATUS
echo ========================================
echo.
echo Checking if backend is running...
echo.

curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel%==0 (
    echo ✓ Backend is RUNNING
    echo   URL: http://localhost:8000
    echo.
    echo Testing text upload endpoint...
    curl -s http://localhost:8000/docs >nul 2>&1
    if %errorlevel%==0 (
        echo ✓ API Documentation available at:
        echo   http://localhost:8000/docs
    )
) else (
    echo ✗ Backend is NOT RUNNING
    echo.
    echo Please start the backend:
    echo   docker-compose up -d
    echo   OR
    echo   start.bat
)
echo.
echo ========================================
echo.
pause
goto MENU

:VIEW_FILE
cls
echo.
echo ========================================
echo   BLOCKCHAIN QUESTIONS FILE
echo ========================================
echo.
echo File: Blockchain_Fundamentals_50_Questions.txt
echo.
echo First 20 lines:
echo ----------------------------------------
type Blockchain_Fundamentals_50_Questions.txt | more /E +0
echo ----------------------------------------
echo.
echo Total questions: 50
echo Format: Multiple Choice (A, B, C, D)
echo Topic: Blockchain Fundamentals
echo.
pause
goto MENU

:EXIT
cls
echo.
echo ========================================
echo   THANK YOU!
echo ========================================
echo.
echo For detailed instructions, see:
echo   BLOCKCHAIN_QUESTIONS_UPLOAD_GUIDE.md
echo.
echo For support, check:
echo   - Backend logs: docker-compose logs backend
echo   - Browser console (F12)
echo.
echo Happy Teaching! 🎓
echo.
pause
exit

