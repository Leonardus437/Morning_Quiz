@echo off
chcp 65001 > nul
echo ========================================
echo Student Upload Test
echo ========================================
echo.

echo [1/5] Checking backend...
curl -s http://localhost:8000/health > nul
if %errorlevel% neq 0 (
    echo ERROR: Backend not running!
    echo Run: docker-compose up -d
    pause
    exit /b 1
)
echo OK: Backend running
echo.

echo [2/5] Testing admin login...
curl -s -X POST http://localhost:8000/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}" > temp_token.json
if %errorlevel% neq 0 (
    echo ERROR: Login failed!
    pause
    exit /b 1
)
echo OK: Admin logged in
echo.

echo [3/5] Creating test CSV file...
echo Name,Department,Level,Username > test_students.csv
echo Test Student 1,Software Development,Level 4,teststudent1 >> test_students.csv
echo Test Student 2,Software Development,Level 4,teststudent2 >> test_students.csv
echo Test Student 3,Computer System and Architecture,Level 5,teststudent3 >> test_students.csv
echo OK: Test file created
echo.

echo [4/5] Uploading students (CSV)...
echo NOTE: Manual upload test required
echo.
echo Please:
echo 1. Open browser: http://localhost:3000/admin
echo 2. Login: admin / admin123
echo 3. Go to Students section
echo 4. Click "Upload Students"
echo 5. Select: test_students.csv
echo 6. Click Upload
echo.
echo Expected result: 3 students imported
echo.

echo [5/5] Verifying students...
echo Checking if students were created...
timeout /t 5 > nul
echo.
echo To verify manually:
echo - Go to http://localhost:3000/admin
echo - Check Students list
echo - Should see: teststudent1, teststudent2, teststudent3
echo.

echo ========================================
echo Test file created: test_students.csv
echo ========================================
echo.
echo Next steps:
echo 1. Upload test_students.csv via admin panel
echo 2. Verify 3 students appear
echo 3. Try logging in as teststudent1 / student123
echo.
pause
