@echo off
cd /d "d:\Morning_Quiz-master"
echo [1/4] Fixing .gitignore...
git add .gitignore
echo [2/4] Force adding performance_reports.py...
git add -f backend/performance_reports.py
git add backend/ai_grader.py
git add backend/main.py
echo [3/4] Committing...
git commit -m "Fix: Add performance_reports.py and ai_grader.py to backend"
echo [4/4] Pushing to GitHub...
git push origin main
echo.
echo SUCCESS! Render will redeploy in 1-2 minutes.
pause
