@echo off
color 0A
title Quick Rebuild - TVET Quiz System

echo.
echo ========================================
echo   QUICK REBUILD (Frontend Only)
echo ========================================
echo.
echo This will rebuild ONLY the frontend container
echo (Much faster than full rebuild)
echo.
pause

echo.
echo Step 1: Stopping frontend container...
docker-compose stop frontend

echo.
echo Step 2: Rebuilding frontend...
docker-compose build frontend --no-cache

echo.
echo Step 3: Starting frontend...
docker-compose up -d frontend

echo.
echo ========================================
echo   REBUILD COMPLETE!
echo ========================================
echo.
echo ✓ Frontend rebuilt and restarted
echo.
echo Access your system at:
echo   http://localhost:3000
echo.
echo The [object Object] error should be FIXED now!
echo.
pause
