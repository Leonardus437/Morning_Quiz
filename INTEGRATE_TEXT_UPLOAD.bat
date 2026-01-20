@echo off
echo ========================================
echo  INTEGRATING TEXT QUESTION UPLOAD
echo ========================================
echo.

echo Step 1: Adding text question parser to backend...
copy backend\text_question_parser.py backend\text_question_parser.py.backup 2>nul
echo ✓ Parser ready

echo.
echo Step 2: Adding endpoint to main.py...
echo.
echo Please add the following code to backend\main.py:
echo.
echo ----------------------------------------
type backend\text_question_endpoint.py
echo ----------------------------------------
echo.

echo Step 3: Restart the backend server
echo Run: docker-compose restart backend
echo.

echo Step 4: Access the upload interface
echo Open: upload_blockchain_questions.html in your browser
echo.

echo ========================================
echo  INTEGRATION INSTRUCTIONS COMPLETE
echo ========================================
echo.
echo NEXT STEPS:
echo 1. Add the endpoint code from text_question_endpoint.py to main.py
echo 2. Restart backend: docker-compose restart backend
echo 3. Open upload_blockchain_questions.html
echo 4. Login as teacher and upload Blockchain_Fundamentals_50_Questions.txt
echo.
pause
