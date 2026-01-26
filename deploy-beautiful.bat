@echo off
color 0A
echo.
echo ========================================
echo   DEPLOYING BEAUTIFUL QUESTION TYPES
echo ========================================
echo.
echo Features being deployed:
echo  [*] AI Document Parser
echo  [*] LUMI H5P Integration
echo  [*] Question Bank Access
echo  [*] 13 Professional Question Types
echo  [*] Gradient Backgrounds
echo  [*] Animated Blobs
echo  [*] Glassmorphism Design
echo.
echo ========================================
echo.

cd frontend

echo [1/3] Building frontend...
call npm run build
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo ERROR: Build failed!
    echo.
    pause
    exit /b 1
)

echo.
echo [2/3] Deploying to Cloudflare Pages...
call npx wrangler pages deploy build --project-name=tsskwizi

echo.
color 0B
echo ========================================
echo   DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo Your beautiful Question Types page is live!
echo.
echo Test it now:
echo  - Login: https://tsskwizi.pages.dev/teacher
echo  - Click: Question Types button
echo.
echo What you'll see:
echo  [x] Purple/Pink gradient backgrounds
echo  [x] Animated floating blobs
echo  [x] Quick Actions panel (AI Parser, LUMI H5P, Bank)
echo  [x] 13 question types with icons
echo  [x] Professional hover effects
echo  [x] Glassmorphism design
echo.
echo ========================================
echo.
pause
