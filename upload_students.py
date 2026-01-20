#!/usr/bin/env python3
"""
Simple script to upload students directly to database
No login required - works offline
"""
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from passlib.context import CryptContext
import random
import string

DATABASE_URL = "postgresql://tvetuser:tvetpass123@localhost:5432/tvetquiz"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_password(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def upload_students(file_path, department, level):
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Connect to database
        engine = create_engine(DATABASE_URL)
        
        students_added = 0
        students_updated = 0
        
        with engine.connect() as conn:
            for idx, row in df.iterrows():
                # Get student name (try different column names)
                name = None
                for col in ['Name', 'name', 'NAMES', 'Names', 'Student Name', 'Full Name']:
                    if col in df.columns:
                        name = str(row[col]).strip()
                        break
                
                if not name or name == 'nan':
                    continue
                
                # Generate username and password
                username = f"student{str(idx+1).zfill(3)}"
                password = generate_password()
                hashed_password = pwd_context.hash(password)
                
                # Check if student exists
                result = conn.execute(
                    text("SELECT id FROM users WHERE username = :username"),
                    {"username": username}
                )
                existing = result.fetchone()
                
                if existing:
                    # Update existing student
                    conn.execute(
                        text("""
                            UPDATE users 
                            SET full_name = :name, department = :dept, level = :level
                            WHERE username = :username
                        """),
                        {"name": name, "dept": department, "level": level, "username": username}
                    )
                    students_updated += 1
                else:
                    # Insert new student
                    conn.execute(
                        text("""
                            INSERT INTO users (username, password_hash, full_name, role, department, level, is_active)
                            VALUES (:username, :password, :name, 'student', :dept, :level, true)
                        """),
                        {
                            "username": username,
                            "password": hashed_password,
                            "name": name,
                            "dept": department,
                            "level": level
                        }
                    )
                    students_added += 1
                    print(f"✅ {name} -> {username} / {password}")
            
            conn.commit()
        
        print(f"\n✅ SUCCESS!")
        print(f"📊 Added: {students_added} students")
        print(f"📊 Updated: {students_updated} students")
        print(f"📊 Total: {students_added + students_updated} students")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python upload_students.py <excel_file> <department> <level>")
        print("Example: python upload_students.py students.xlsx LSV L5")
        sys.exit(1)
    
    file_path = sys.argv[1]
    department = sys.argv[2]
    level = sys.argv[3]
    
    upload_students(file_path, department, level)
