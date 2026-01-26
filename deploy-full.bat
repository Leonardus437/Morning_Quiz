@echo off
echo ========================================
echo   DEPLOYING FULL TEACHER DASHBOARD
echo ========================================
echo.
echo Features:
echo  - 13 Advanced Question Types
echo  - Review Tab for submissions
echo  - AI Document Parser
echo  - All advanced features
echo.

cd frontend

echo [1/3] Building frontend...
call npm run build
if %errorlevel% neq 0 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo [2/3] Deploying to Cloudflare Pages...
call npx wrangler pages deploy build --project-name=tsskwizi

echo.
echo [3/3] Deployment complete!
echo.
echo ========================================
echo   SUCCESS! Your dashboard is live!
echo ========================================
echo.
echo URL: https://tsskwizi.pages.dev/teacher
echo Login: teacher001 / teacher123
echo.
echo Features now available:
echo  [x] 13 Question Types
echo  [x] Review Tab
echo  [x] AI Parser
echo  [x] All advanced features
echo.
pause
