@echo off
color 0A
echo.
echo ========================================
echo   DEPLOY TO PRODUCTION - CHECKLIST
echo ========================================
echo.
echo STEP 1: DEPLOY BACKEND
echo -----------------------
echo 1. Go to: https://render.com/
echo 2. Sign up (free account)
echo 3. New Web Service
echo 4. Settings:
echo    - Name: tsskwizi-backend
echo    - Build: pip install -r backend/requirements.txt
echo    - Start: cd backend ^&^& uvicorn main:app --host 0.0.0.0 --port $PORT
echo 5. Add Database (PostgreSQL - free)
echo 6. Copy backend URL (e.g., https://tsskwizi-backend.onrender.com)
echo.
pause
echo.
echo STEP 2: UPDATE FRONTEND CONFIG
echo -------------------------------
echo 1. Open: frontend\.env.production
echo 2. Replace with YOUR backend URL:
echo    PUBLIC_API_URL=https://YOUR-BACKEND-URL.onrender.com
echo.
pause
echo.
echo STEP 3: BUILD FRONTEND
echo ----------------------
cd frontend
echo Building frontend...
call npm install
call npm run build
echo.
echo ✅ Build complete! Folder: frontend\build
echo.
pause
echo.
echo STEP 4: DEPLOY TO CLOUDFLARE
echo -----------------------------
echo OPTION A - Wrangler CLI:
echo   npx wrangler pages deploy build --project-name=tsskwizi
echo.
echo OPTION B - Manual Upload:
echo   1. Go to: https://dash.cloudflare.com/
echo   2. Pages ^> tsskwizi ^> Create deployment
echo   3. Drag 'frontend\build' folder
echo.
echo DONE! Visit: https://tsskwizi.pages.dev/
echo.
pause
