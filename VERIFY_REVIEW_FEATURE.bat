@echo off
echo ========================================
echo   Review Feature Verification Test
echo ========================================
echo.

echo Testing Backend Health...
curl -s https://tvet-quiz-backend.onrender.com/health
echo.
echo.

echo Testing Backend Review Endpoints...
echo.

echo [1] Testing /teacher/pending-reviews endpoint...
curl -s -o nul -w "Status: %%{http_code}\n" https://tvet-quiz-backend.onrender.com/teacher/pending-reviews
echo.

echo [2] Testing /teacher/review/1 endpoint...
curl -s -o nul -w "Status: %%{http_code}\n" https://tvet-quiz-backend.onrender.com/teacher/review/1
echo.

echo [3] Testing /teacher/quiz/1/review-status endpoint...
curl -s -o nul -w "Status: %%{http_code}\n" https://tvet-quiz-backend.onrender.com/teacher/quiz/1/review-status
echo.

echo ========================================
echo   Frontend Verification
echo ========================================
echo.
echo Please manually verify the following:
echo.
echo 1. Go to: https://tsskwizi.pages.dev/teacher
echo 2. Login with teacher credentials
echo 3. Check if "Pending Reviews" button is visible
echo 4. Click "Pending Reviews" to see the list
echo 5. Try reviewing a submission (if available)
echo.
echo ========================================
echo   Expected Results
echo ========================================
echo.
echo Backend Health: Should show {"status":"healthy"}
echo Endpoint Status: Should show 401 (auth required) or 200 (success)
echo.
echo If you see 404 errors, the endpoints are missing!
echo If you see 401 errors, the endpoints exist but need auth!
echo If you see 200 errors, everything is working perfectly!
echo.
pause
