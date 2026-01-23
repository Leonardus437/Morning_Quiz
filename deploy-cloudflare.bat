@echo off
echo ========================================
echo Cloudflare Pages Manual Deployment
echo ========================================
echo.

cd frontend

echo [1/3] Building frontend...
call npm run build
if errorlevel 1 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo [2/3] Installing Wrangler CLI...
call npm install -g wrangler
if errorlevel 1 (
    echo ERROR: Wrangler installation failed!
    pause
    exit /b 1
)

echo.
echo [3/3] Deploying to Cloudflare Pages...
echo.
echo IMPORTANT: You will be asked to login to Cloudflare
echo.
cd ..
call wrangler pages deploy frontend/build --project-name=tsskwizi

echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Your site should be live at:
echo https://tsskwizi.pages.dev
echo.
pause
