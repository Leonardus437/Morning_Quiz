@echo off
color 0E
echo.
echo ========================================
echo   DEPLOYMENT DIAGNOSTICS
echo ========================================
echo.

echo [1/6] Checking Node.js...
node --version
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found
) else (
    echo OK: Node.js installed
)

echo.
echo [2/6] Checking npm...
npm --version
if %errorlevel% neq 0 (
    echo ERROR: npm not found
) else (
    echo OK: npm installed
)

echo.
echo [3/6] Checking Wrangler...
cd frontend
call npx wrangler --version
if %errorlevel% neq 0 (
    echo ERROR: Wrangler not accessible
) else (
    echo OK: Wrangler accessible
)

echo.
echo [4/6] Checking Wrangler authentication...
call npx wrangler whoami
if %errorlevel% neq 0 (
    echo WARNING: Not authenticated with Cloudflare
    echo Run: npx wrangler login
) else (
    echo OK: Authenticated with Cloudflare
)

echo.
echo [5/6] Checking build directory...
if exist build (
    echo OK: Build directory exists
    dir build /b | find /c /v "" > temp.txt
    set /p filecount=<temp.txt
    del temp.txt
    echo Files in build: %filecount%
) else (
    echo WARNING: Build directory not found
    echo Run: npm run build
)

echo.
echo [6/6] Checking wrangler.toml...
cd ..
if exist frontend\wrangler.toml (
    echo OK: wrangler.toml exists
    echo.
    echo Contents:
    type frontend\wrangler.toml
) else (
    echo WARNING: wrangler.toml not found
)

echo.
echo ========================================
echo   DIAGNOSTIC COMPLETE
echo ========================================
echo.
echo Next steps based on results:
echo  - If not authenticated: npx wrangler login
echo  - If build missing: npm run build
echo  - If all OK: Try RETRY_DEPLOYMENT.bat
echo  - Alternative: Use DEPLOY_VIA_GIT.bat
echo.
echo ========================================
echo.
pause
