@echo off
setlocal enabledelayedexpansion

echo ========================================
echo EXCEL STUDENT UPLOAD TOOL
echo ========================================
echo.

if "%~1"=="" (
    echo Drag and drop your Excel file onto this script
    echo.
    echo Or run: UPLOAD_EXCEL.bat "path\to\file.xlsx" DEPARTMENT LEVEL
    echo Example: UPLOAD_EXCEL.bat "students.xlsx" LSV L5
    echo.
    pause
    exit /b
)

set "FILE=%~1"
set "DEPT=%~2"
set "LEVEL=%~3"

if "%DEPT%"=="" set "DEPT=LSV"
if "%LEVEL%"=="" set "LEVEL=L5"

echo File: %FILE%
echo Department: %DEPT%
echo Level: %LEVEL%
echo.
echo Processing...
echo.

REM Copy file to container
docker cp "%FILE%" tvet_quiz-backend-1:/tmp/upload.xlsx

REM Run Python script in container
docker exec tvet_quiz-backend-1 python -c "
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

try:
    df = pd.read_excel('/tmp/upload.xlsx')
    engine = create_engine(DATABASE_URL)
    
    students_added = 0
    students_updated = 0
    credentials = []
    
    with engine.connect() as conn:
        for idx, row in df.iterrows():
            name = None
            for col in ['Name', 'name', 'NAMES', 'Names', 'Student Name', 'Full Name', 'FULL NAME']:
                if col in df.columns:
                    name = str(row[col]).strip()
                    if name and name != 'nan':
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
            
            if result.fetchone():
                conn.execute(
                    text('''UPDATE users SET full_name = :name, department = :dept, level = :level 
                            WHERE username = :username'''),
                    {'name': name, 'dept': '%DEPT%', 'level': '%LEVEL%', 'username': username}
                )
                students_updated += 1
            else:
                conn.execute(
                    text('''INSERT INTO users (username, password_hash, full_name, role, department, level)
                            VALUES (:username, :password, :name, 'student', :dept, :level)'''),
                    {'username': username, 'password': hashed_password, 'name': name, 
                     'dept': '%DEPT%', 'level': '%LEVEL%'}
                )
                students_added += 1
                credentials.append(f'{name} -> {username} / {password}')
        
        conn.commit()
    
    print(f'\n✅ SUCCESS!')
    print(f'📊 Added: {students_added} students')
    print(f'📊 Updated: {students_updated} students')
    print(f'📊 Total: {students_added + students_updated} students\n')
    
    if credentials:
        print('🔑 NEW STUDENT CREDENTIALS:')
        print('=' * 60)
        for cred in credentials:
            print(cred)
        print('=' * 60)
        
        # Save to file
        with open('/tmp/credentials.txt', 'w') as f:
            f.write('STUDENT CREDENTIALS\n')
            f.write('Department: %DEPT%\n')
            f.write('Level: %LEVEL%\n')
            f.write('=' * 60 + '\n')
            for cred in credentials:
                f.write(cred + '\n')
        print('\n📄 Credentials saved to: credentials.txt')

except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
"

REM Copy credentials file back
docker cp tvet_quiz-backend-1:/tmp/credentials.txt "%~dp0credentials.txt" 2>nul

echo.
echo ========================================
echo Upload Complete!
echo ========================================
echo.
echo Credentials saved to: credentials.txt
echo.
pause
