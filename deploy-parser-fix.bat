@echo off
color 0A
echo.
echo ========================================
echo   DEPLOYING SUPER PARSER FIX
echo ========================================
echo.

echo [1/3] Adding changes to git...
git add .

echo.
echo [2/3] Committing changes...
git commit -m "Fix: Super intelligent parser extracts ALL questions"

echo.
echo [3/3] Pushing to GitHub (triggers Render auto-deploy)...
git push

echo.
color 0B
echo ========================================
echo   DEPLOYMENT INITIATED!
echo ========================================
echo.
echo Backend will auto-deploy on Render in ~2 minutes
echo.
echo Check deployment status:
echo  https://dashboard.render.com
echo.
echo Once deployed, test the parser:
echo  1. Login: https://tsskwizi.pages.dev/teacher
echo  2. Click: Question Types
echo  3. Upload your 25-question document
echo  4. Should see: "Successfully saved 25 questions"
echo.
echo ========================================
echo.
pause
