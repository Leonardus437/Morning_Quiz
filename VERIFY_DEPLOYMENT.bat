@echo off
echo ========================================
echo TVET QUIZ SYSTEM - DEPLOYMENT VERIFICATION
echo ========================================
echo.

echo [1/3] Checking Backend (Render)...
echo URL: https://tvet-quiz-backend.onrender.com/health
echo Opening in browser...
start https://tvet-quiz-backend.onrender.com/health
timeout /t 3 >nul
echo.

echo [2/3] Checking Frontend (Cloudflare Pages)...
echo URL: https://tsskwizi.pages.dev
echo Opening in browser...
start https://tsskwizi.pages.dev
timeout /t 3 >nul
echo.

echo [3/3] Checking Teacher Panel...
echo URL: https://tsskwizi.pages.dev/teacher
echo Opening in browser...
start https://tsskwizi.pages.dev/teacher
timeout /t 2 >nul
echo.

echo ========================================
echo VERIFICATION COMPLETE
echo ========================================
echo.
echo Please verify in your browser:
echo.
echo 1. Backend health check shows:
echo    - status: "healthy"
echo    - version: "2.0-ANTI-CHEAT"
echo.
echo 2. Frontend homepage shows:
echo    - Professional carousel with 4 slides
echo    - Modern gradient buttons
echo    - 3-column footer
echo.
echo 3. Teacher panel loads correctly
echo.
echo ========================================
echo.
echo Default Login Credentials:
echo.
echo ADMIN:
echo   Username: admin
echo   Password: admin123
echo.
echo TEACHER:
echo   Username: teacher001
echo   Password: teacher123
echo.
echo STUDENT:
echo   Username: student001
echo   Password: pass123
echo.
echo ========================================
pause
