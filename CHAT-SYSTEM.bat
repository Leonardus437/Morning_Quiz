@echo off
title Modern Chat System - Control Panel
color 0B

:menu
cls
echo.
echo  ╔════════════════════════════════════════════════════════╗
echo  ║                                                        ║
echo  ║        MODERN CHAT SYSTEM - CONTROL PANEL             ║
echo  ║                                                        ║
echo  ║        Professional WhatsApp-Style Messaging          ║
echo  ║                                                        ║
echo  ╚════════════════════════════════════════════════════════╝
echo.
echo  ┌────────────────────────────────────────────────────────┐
echo  │  MAIN MENU                                             │
echo  └────────────────────────────────────────────────────────┘
echo.
echo   [1] 🚀 START Chat System (Backend + Frontend)
echo   [2] 🧪 OPEN Test Pages (Student/Teacher/Admin)
echo   [3] 🛑 STOP All Servers
echo   [4] ✅ CHECK System Requirements
echo   [5] 📚 VIEW Documentation
echo   [6] 🌐 OPEN URLs Manually
echo   [7] ❌ EXIT
echo.
echo  ┌────────────────────────────────────────────────────────┐
echo  │  TEST CREDENTIALS                                      │
echo  └────────────────────────────────────────────────────────┘
echo.
echo   Student:  student001 / pass123
echo   Teacher:  teacher001 / teacher123
echo   Admin:    admin / admin123
echo.
echo  ════════════════════════════════════════════════════════
echo.

set /p choice="  Enter your choice (1-7): "

if "%choice%"=="1" goto start
if "%choice%"=="2" goto test
if "%choice%"=="3" goto stop
if "%choice%"=="4" goto check
if "%choice%"=="5" goto docs
if "%choice%"=="6" goto urls
if "%choice%"=="7" goto exit

echo.
echo  Invalid choice! Please try again.
timeout /t 2 /nobreak >nul
goto menu

:start
cls
echo.
echo  ════════════════════════════════════════════════════════
echo   STARTING CHAT SYSTEM...
echo  ════════════════════════════════════════════════════════
echo.
call start-chat-system.bat
goto menu

:test
cls
echo.
echo  ════════════════════════════════════════════════════════
echo   OPENING TEST PAGES...
echo  ════════════════════════════════════════════════════════
echo.
call test-chat-system.bat
goto menu

:stop
cls
echo.
echo  ════════════════════════════════════════════════════════
echo   STOPPING SERVERS...
echo  ════════════════════════════════════════════════════════
echo.
call stop-chat-system.bat
goto menu

:check
cls
echo.
echo  ════════════════════════════════════════════════════════
echo   CHECKING SYSTEM REQUIREMENTS...
echo  ════════════════════════════════════════════════════════
echo.
call check-system.bat
goto menu

:docs
cls
echo.
echo  ════════════════════════════════════════════════════════
echo   DOCUMENTATION FILES
echo  ════════════════════════════════════════════════════════
echo.
echo   [1] QUICK_START_MODERN_CHAT.md - Quick testing guide
echo   [2] MODERN_CHAT_SYSTEM.md - Full documentation
echo   [3] TRANSFORMATION_SUMMARY.md - What changed
echo   [4] VISUAL_GUIDE.md - Interface layout
echo   [5] DEPLOYMENT_CHECKLIST.md - Deploy to production
echo   [6] BATCH_FILES_README.md - Batch files guide
echo.
echo   Opening documentation folder...
start explorer .
echo.
pause
goto menu

:urls
cls
echo.
echo  ════════════════════════════════════════════════════════
echo   MANUAL URL ACCESS
echo  ════════════════════════════════════════════════════════
echo.
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:3002
echo.
echo   Student:  http://localhost:3002
echo   Teacher:  http://localhost:3002/teacher
echo   Admin:    http://localhost:3002/admin
echo.
echo   Opening URLs...
echo.
start http://localhost:8000
timeout /t 1 /nobreak >nul
start http://localhost:3002
echo.
pause
goto menu

:exit
cls
echo.
echo  ════════════════════════════════════════════════════════
echo   Thank you for using Modern Chat System!
echo  ════════════════════════════════════════════════════════
echo.
echo   Your amazing chat system is ready to amaze everyone! 🎉
echo.
timeout /t 2 /nobreak >nul
exit
