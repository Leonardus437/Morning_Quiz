@echo off
echo ========================================
echo STUDENT UPLOAD TOOL
echo ========================================
echo.

if "%~1"=="" (
    echo Usage: UPLOAD_STUDENTS.bat ^<excel_file^> ^<department^> ^<level^>
    echo.
    echo Example:
    echo   UPLOAD_STUDENTS.bat students.xlsx LSV L5
    echo.
    echo Departments: LSV, ICT, ENG, etc.
    echo Levels: L3, L4, L5, L6
    echo.
    pause
    exit /b
)

echo Uploading students from: %~1
echo Department: %2
echo Level: %3
echo.

docker exec -i tvet_quiz-backend-1 python -c "
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from passlib.context import CryptContext
import random
import string

DATABASE_URL = 'postgresql://tvetuser:tvetpass123@tvet_quiz-db-1:5432/tvetquiz'
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def generate_password(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# Read from stdin
df = pd.read_excel('/tmp/upload.xlsx')
engine = create_engine(DATABASE_URL)

students_added = 0
credentials = []

with engine.connect() as conn:
    for idx, row in df.iterrows():
        name = None
        for col in ['Name', 'name', 'NAMES', 'Names', 'Student Name', 'Full Name']:
            if col in df.columns:
                name = str(row[col]).strip()
                break
        
        if not name or name == 'nan':
            continue
        
        username = f'student{str(idx+1).zfill(3)}'
        password = generate_password()
        hashed_password = pwd_context.hash(password)
        
        result = conn.execute(
            text('SELECT id FROM users WHERE username = :username'),
            {'username': username}
        )
        
        if not result.fetchone():
            conn.execute(
                text('''
                    INSERT INTO users (username, password_hash, full_name, role, department, level, is_active)
                    VALUES (:username, :password, :name, 'student', :dept, :level, true)
                '''),
                {
                    'username': username,
                    'password': hashed_password,
                    'name': name,
                    'dept': '%2',
                    'level': '%3'
                }
            )
            students_added += 1
            credentials.append(f'{name} -> {username} / {password}')
    
    conn.commit()

print(f'\n✅ SUCCESS! Added {students_added} students\n')
for cred in credentials:
    print(cred)
" < "%~1"

echo.
echo ========================================
echo Upload complete!
echo ========================================
pause
