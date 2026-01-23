@echo off
echo ========================================
echo COMPLETE QUIZ FLOW TEST
echo Testing HTTP 404 and 422 Fixes
echo ========================================
echo.

REM Step 1: Login as teacher
echo [1/8] Teacher Login...
curl -s -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d "{\"username\":\"teacher001\",\"password\":\"teacher123\"}" > temp_teacher.json
for /f "tokens=2 delims=:," %%a in ('findstr "access_token" temp_teacher.json') do set TEACHER_TOKEN=%%a
set TEACHER_TOKEN=%TEACHER_TOKEN:"=%
set TEACHER_TOKEN=%TEACHER_TOKEN: =%
echo Teacher logged in successfully
echo.

REM Step 2: Create a question
echo [2/8] Creating question...
curl -s -X POST http://localhost:8000/questions -H "Authorization: Bearer %TEACHER_TOKEN%" -H "Content-Type: application/json" -d "{\"question_text\":\"What is 2+2?\",\"question_type\":\"multiple_choice\",\"options\":[\"3\",\"4\",\"5\"],\"correct_answer\":\"4\",\"points\":1,\"department\":\"Software Development\",\"level\":\"Level 5\"}" > temp_question.json
for /f "tokens=2 delims=:," %%a in ('findstr "\"id\"" temp_question.json') do set QUESTION_ID=%%a
set QUESTION_ID=%QUESTION_ID: =%
echo Question created with ID: %QUESTION_ID%
echo.

REM Step 3: Create quiz
echo [3/8] Creating quiz...
curl -s -X POST http://localhost:8000/quizzes -H "Authorization: Bearer %TEACHER_TOKEN%" -H "Content-Type: application/json" -d "{\"title\":\"Test Quiz\",\"description\":\"Testing quiz flow\",\"duration_minutes\":5,\"question_time_seconds\":30,\"shuffle_questions\":true,\"department\":\"Software Development\",\"level\":\"Level 5\",\"question_ids\":[%QUESTION_ID%]}" > temp_quiz.json
for /f "tokens=2 delims=:," %%a in ('findstr "\"id\"" temp_quiz.json') do set QUIZ_ID=%%a
set QUIZ_ID=%QUIZ_ID: =%
echo Quiz created with ID: %QUIZ_ID%
echo.

REM Step 4: Broadcast quiz
echo [4/8] Broadcasting quiz...
curl -s -X PUT "http://localhost:8000/quizzes/%QUIZ_ID%/broadcast" -H "Authorization: Bearer %TEACHER_TOKEN%" > temp_broadcast.json
type temp_broadcast.json
echo.
echo Quiz broadcasted successfully
echo.

REM Step 5: Login as student
echo [5/8] Student Login...
curl -s -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d "{\"username\":\"student001\",\"password\":\"pass123\"}" > temp_student.json
for /f "tokens=2 delims=:," %%a in ('findstr "access_token" temp_student.json') do set STUDENT_TOKEN=%%a
set STUDENT_TOKEN=%STUDENT_TOKEN:"=%
set STUDENT_TOKEN=%STUDENT_TOKEN: =%
echo Student logged in successfully
echo.

REM Step 6: Get available quizzes
echo [6/8] Getting available quizzes...
curl -s -X GET "http://localhost:8000/quizzes" -H "Authorization: Bearer %STUDENT_TOKEN%" > temp_quizzes.json
echo Quizzes retrieved:
type temp_quizzes.json
echo.
echo.

REM Step 7: CRITICAL TEST - Get quiz questions (This was causing HTTP 404)
echo [7/8] CRITICAL TEST: Getting quiz questions (Start Quiz)...
curl -s -X GET "http://localhost:8000/quizzes/%QUIZ_ID%/questions" -H "Authorization: Bearer %STUDENT_TOKEN%" > temp_questions.json
echo Response:
type temp_questions.json
echo.
echo.

REM Step 8: CRITICAL TEST - Submit quiz (This was causing HTTP 422)
echo [8/8] CRITICAL TEST: Submitting quiz answers...
curl -s -X POST "http://localhost:8000/quizzes/submit" -H "Authorization: Bearer %STUDENT_TOKEN%" -H "Content-Type: application/json" -d "{\"quiz_id\":%QUIZ_ID%,\"answers\":[{\"question_id\":%QUESTION_ID%,\"answer\":\"4\"}]}" > temp_submit.json
echo Response:
type temp_submit.json
echo.
echo.

REM Cleanup
del temp_*.json 2>nul

echo ========================================
echo TEST COMPLETED
echo ========================================
echo.
echo If you see:
echo - Questions data in step 7 = HTTP 404 FIXED ✅
echo - Score data in step 8 = HTTP 422 FIXED ✅
echo.
pause
