@echo off
echo ========================================
echo   Deploying Frontend to Cloudflare Pages
echo ========================================
echo.

cd frontend

echo [1/3] Checking build folder...
if not exist "build" (
    echo ERROR: Build folder not found!
    echo Please run: npm run build
    pause
    exit /b 1
)

echo [2/3] Deploying to Cloudflare Pages...
npx wrangler pages deploy build --project-name=tsskwizi

echo.
echo [3/3] Deployment complete!
echo.
echo Your app is live at: https://tsskwizi.pages.dev
echo.
pause
