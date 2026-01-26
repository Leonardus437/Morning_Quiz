@echo off
color 0B
echo.
echo ========================================
echo   TEACHER DASHBOARD - ALL 5 FIXES
echo ========================================
echo.
echo Fixes included:
echo  [1] Remove "Add Question" button from navigation
echo  [2] All 13 question types working manually
echo  [3] Enhanced AI Parser (handles all formats)
echo  [4] Auto-show "My Questions" after creation
echo  [5] Smart notifications (only on NEW events)
echo.
echo ========================================
echo.

cd frontend

echo [1/3] Building frontend with all fixes...
call npm run build
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo ERROR: Build failed!
    echo.
    pause
    exit /b 1
)

echo.
echo [2/3] Deploying to Cloudflare Pages...
call npx wrangler pages deploy build --project-name=tsskwizi

echo.
color 0A
echo ========================================
echo   ALL 5 FIXES DEPLOYED!
echo ========================================
echo.
echo Test the fixes:
echo  1. Go to: https://tsskwizi.pages.dev/teacher
echo  2. Login: teacher001 / teacher123
echo.
echo What's Fixed:
echo  [x] "Add Question" button removed from main nav
echo  [x] All 13 question types work in Question Types page
echo  [x] AI Parser handles all document formats better
echo  [x] After creating question, auto-redirects to My Questions
echo  [x] Notifications only popup on NEW events, not on refresh
echo.
echo Navigation now shows:
echo  - Dashboard
echo  - Notifications
echo  - My Questions (NEW!)
echo  - Create Quiz
echo  - My Quizzes
echo  - My Courses
echo  - Question Types
echo  - Review
echo.
echo ========================================
echo.
pause
