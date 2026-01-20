@echo off
echo Stopping backend...
docker stop morning_quiz-backend-1

echo Removing old container...
docker rm morning_quiz-backend-1

echo Starting new backend with updated code...
docker run -d --name morning_quiz-backend-1 ^
  --network morning_quiz_default ^
  -p 8000:8000 ^
  -e DATABASE_URL=postgresql://quiz_user:quiz_pass123@db:5432/morning_quiz ^
  -e SECRET_KEY=your-secret-key-change-in-production ^
  -v "%cd%\backend:/app" ^
  morning_quiz-backend:latest

echo Backend updated!
timeout /t 5
docker logs morning_quiz-backend-1 --tail 20
