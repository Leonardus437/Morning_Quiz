@echo off
echo ========================================
echo   TVET Quiz - Deployment Preparation
echo ========================================
echo.

echo [1/5] Checking Git status...
git status

echo.
echo [2/5] Installing frontend dependencies...
cd frontend
call npm install @sveltejs/adapter-static --save-dev

echo.
echo [3/5] Updating svelte config...
copy svelte.config.cloudflare.js svelte.config.js

echo.
echo [4/5] Creating .env files...
cd ..
if not exist "backend\.env" copy "backend\.env.example" "backend\.env"
if not exist "frontend\.env" copy "frontend\.env.example" "frontend\.env"

echo.
echo [5/5] Ready to commit and push!
echo.
echo ========================================
echo   NEXT STEPS:
echo ========================================
echo.
echo 1. Update backend\.env with your values
echo 2. Update frontend\.env with your backend URL
echo 3. Run: git add .
echo 4. Run: git commit -m "Add deployment configs"
echo 5. Run: git push origin main
echo.
echo Then follow DEPLOYMENT_GUIDE.md
echo.
pause
