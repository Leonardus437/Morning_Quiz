@echo off
echo ========================================
echo  TVET Quiz - Deploy to Cloudflare Pages
echo ========================================
echo.

cd frontend

echo Installing dependencies...
call npm install
if errorlevel 1 (
    echo ERROR: npm install failed
    pause
    exit /b 1
)
echo.

echo Building frontend...
call npm run build
if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)
echo.

echo Deploying to Cloudflare Pages...
echo.
echo NOTE: You need to login to Cloudflare first if not already logged in.
echo Run: npx wrangler login
echo.
pause

call npx wrangler pages deploy build --project-name=tsskwizi

echo.
echo ========================================
echo  Deployment Complete!
echo ========================================
echo.
echo Your site should be live at:
echo https://tsskwizi.pages.dev
echo.
pause
