@echo off
echo ========================================
echo   OPENING TEST PAGES
echo ========================================
echo.

echo Opening Student Login...
start http://localhost:3002
timeout /t 2 /nobreak >nul

echo Opening Teacher Login...
start http://localhost:3002/teacher
timeout /t 2 /nobreak >nul

echo Opening Admin Login...
start http://localhost:3002/admin

echo.
echo ========================================
echo   TEST CREDENTIALS
echo ========================================
echo.
echo Student:  student001 / pass123
echo Teacher:  teacher001 / teacher123
echo Admin:    admin / admin123
echo.
echo ========================================
echo   WHAT TO TEST
echo ========================================
echo.
echo 1. Login with each role
echo 2. Look for gradient chat button (bottom-right)
echo 3. Click button to open WhatsApp-style chat
echo 4. Create rooms (teachers/admin only)
echo 5. Send messages and test real-time updates
echo.
pause
