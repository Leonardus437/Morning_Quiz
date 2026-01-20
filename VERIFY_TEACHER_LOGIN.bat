@echo off
echo ========================================
echo TEACHER LOGIN VERIFICATION
echo ========================================
echo.

echo Checking teacher001 account...
docker exec tvet_quiz-backend-1 python -c "import sys; sys.path.insert(0, '/app'); from main import SessionLocal, User, verify_password_simple; db = SessionLocal(); teacher = db.query(User).filter(User.username == 'teacher001').first(); print('Username:', teacher.username if teacher else 'NOT FOUND'); print('Full Name:', teacher.full_name if teacher else 'N/A'); print('Role:', teacher.role if teacher else 'N/A'); print('Departments:', teacher.departments if teacher else 'N/A'); print('Password test (teacher123):', verify_password_simple('teacher123', teacher.password_hash) if teacher else False); db.close()"

echo.
echo ========================================
echo TEACHER LOGIN CREDENTIALS
echo ========================================
echo URL: http://localhost:3000/teacher
echo Username: teacher001
echo Password: teacher123
echo ========================================
echo.

pause
