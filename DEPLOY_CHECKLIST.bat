@echo off
color 0E
echo.
echo ========================================
echo   PRODUCTION DEPLOYMENT CHECKLIST
echo ========================================
echo.
echo YOUR LIVE SYSTEM:
echo   Frontend: https://tsskwizi.pages.dev
echo   Backend:  https://tvet-quiz-backend.onrender.com
echo.
echo ========================================
echo   STEP 1: VERIFY RENDER BACKEND
echo ========================================
echo.
echo 1. Go to: https://dashboard.render.com/web/srv-d5drg0p5pdvs73dgmbe0
echo 2. Check "Environment" tab has:
echo    - DATABASE_URL (PostgreSQL connection string)
echo    - SECRET_KEY (any random string)
echo 3. If missing, add them now
echo.
pause
echo.
echo ========================================
echo   STEP 2: PUSH BACKEND CHANGES
echo ========================================
echo.
git add backend/main.py
git commit -m "Update CORS for tsskwizi.pages.dev"
git push origin main
echo.
echo ✅ Pushed! Render will auto-deploy in 2-3 minutes
echo    Watch: https://dashboard.render.com/web/srv-d5drg0p5pdvs73dgmbe0
echo.
pause
echo.
echo ========================================
echo   STEP 3: BUILD AND DEPLOY FRONTEND
echo ========================================
echo.
cd frontend
echo Building...
call npm install
call npm run build
echo.
echo Deploying to Cloudflare...
npx wrangler pages deploy build --project-name=tsskwizi
echo.
echo ✅ Deployed to: https://tsskwizi.pages.dev
echo.
cd ..
pause
echo.
echo ========================================
echo   STEP 4: VERIFY EVERYTHING WORKS
echo ========================================
echo.
echo 1. Backend Health:
echo    https://tvet-quiz-backend.onrender.com/health
echo.
echo 2. Frontend:
echo    https://tsskwizi.pages.dev
echo.
echo 3. Login Test:
echo    Teacher: teacher001 / teacher123
echo    Student: student001 / pass123
echo.
echo ========================================
echo   DEPLOYMENT COMPLETE!
echo ========================================
echo.
pause
