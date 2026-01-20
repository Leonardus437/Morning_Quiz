@echo off
echo Starting backend and database only...
docker run -d --name tvet_quiz-db-1 --network morning_quiz_default -e POSTGRES_USER=tvetuser -e POSTGRES_PASSWORD=tvetpass123 -e POSTGRES_DB=tvetquiz -v tvet_quiz_postgres_data:/var/lib/postgresql/data postgres:15-alpine
timeout /t 5 /nobreak >nul
docker run -d --name tvet_quiz-backend-1 --network morning_quiz_default -p 8000:8000 -e DATABASE_URL=postgresql://tvetuser:tvetpass123@tvet_quiz-db-1:5432/tvetquiz morning_quiz-backend:latest
echo.
echo Backend started on http://localhost:8000
echo.
echo ========================================
echo IMPORTANT: Frontend has cache issues
echo ========================================
echo.
echo The upload feature works in backend!
echo Test it directly at: http://localhost:8000/docs
echo.
echo Or use this test page:
echo file:///c:/Users/PC/Music/Morning_Quiz/test_upload_fixed.html
echo.
pause
