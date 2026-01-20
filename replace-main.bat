@echo off
echo ========================================
echo FIXING CORRUPTED MAIN.PY
echo ========================================
echo.

cd /d "f:\SIDE HUSTLE\Morning_Quiz"

echo Step 1: Backing up old main.py...
copy backend\main.py backend\main_corrupted_backup.py

echo Step 2: Replacing with clean main.py...
copy /Y backend\main_clean.py backend\main.py

echo Step 3: Removing test files from git...
git rm --cached backend/*test*.py 2>nul
git rm --cached backend/*debug*.py 2>nul

echo Step 4: Adding clean main.py to git...
git add backend/main.py

echo Step 5: Committing changes...
git commit -m "Fix: Replace corrupted main.py with clean version"

echo Step 6: Pushing to GitHub...
git push origin master

echo.
echo ========================================
echo DONE! Now go to Render and:
echo 1. Click "Manual Deploy"
echo 2. Select "Clear build cache & deploy"
echo ========================================
pause
