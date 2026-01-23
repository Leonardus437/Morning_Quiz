@echo off
echo ========================================
echo   DEPLOY TO CLOUDFLARE PAGES
echo ========================================
echo.

cd frontend

echo [1/3] Installing dependencies...
call npm install

echo.
echo [2/3] Building for production...
call npm run build

echo.
echo [3/3] Deploying to Cloudflare Pages...
echo.
echo OPTION A - Using Wrangler CLI:
echo   npx wrangler pages deploy build --project-name=tsskwizi
echo.
echo OPTION B - Manual Upload:
echo   1. Go to: https://dash.cloudflare.com/
echo   2. Pages ^> tsskwizi ^> Upload
echo   3. Drag the 'build' folder
echo.

pause
