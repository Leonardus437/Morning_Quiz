@echo off
echo ========================================
echo REMOVING NULL BYTES FROM MAIN.PY
echo ========================================
echo.

cd /d "f:\SIDE HUSTLE\Morning_Quiz"

echo Step 1: Running null byte remover...
python remove-null-bytes.py

if not exist backend\main_fixed.py (
    echo ERROR: Failed to create clean file
    pause
    exit /b 1
)

echo.
echo Step 2: Backing up corrupted main.py...
copy backend\main.py backend\main_corrupted.py

echo Step 3: Replacing with cleaned main.py...
copy /Y backend\main_fixed.py backend\main.py

echo Step 4: Verifying the fix...
python -c "import sys; sys.path.insert(0, 'backend'); import main; print('✅ main.py imports successfully!')"

if errorlevel 1 (
    echo.
    echo ❌ ERROR: main.py still has issues
    echo Restoring backup...
    copy /Y backend\main_corrupted.py backend\main.py
    pause
    exit /b 1
)

echo.
echo Step 5: Committing to git...
git add backend/main.py
git commit -m "Fix: Remove null bytes from main.py"

echo Step 6: Pushing to GitHub...
git push origin master

echo.
echo ========================================
echo ✅ SUCCESS! Your main.py is now clean!
echo ========================================
echo.
echo Now go to Render:
echo 1. Click "Manual Deploy"
echo 2. Select "Clear build cache & deploy"
echo ========================================
pause
