@echo off
echo ========================================
echo PUSH TO GITLAB
echo ========================================
echo.

cd /d "f:\SIDE HUSTLE\Morning_Quiz"

echo Step 1: Adding GitLab remote...
git remote add gitlab https://gitlab.com/Leonardus437/Morning_Quiz.git

echo Step 2: Pushing to GitLab...
git push -u gitlab master

echo.
echo ========================================
echo DONE! Project pushed to GitLab
echo ========================================
echo.
echo GitLab URL: https://gitlab.com/Leonardus437/Morning_Quiz
echo.
echo NEXT: Connect Cloudflare Pages to GitLab
echo 1. Go to Cloudflare Pages
echo 2. Click "Connect GitLab"
echo 3. Select "Morning_Quiz" repository
echo 4. Project name: tsskwizi
echo 5. Build command: cd frontend ^&^& npm install ^&^& npm run build
echo 6. Build output: frontend/build
echo 7. Environment variable: PUBLIC_API_URL = https://tvet-quiz-backend.onrender.com
echo 8. Deploy!
echo.
pause
