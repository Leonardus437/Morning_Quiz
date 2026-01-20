#!/usr/bin/env python3
"""
Initialize Complete Morning Quiz + RTB System
"""

import sqlite3
import hashlib
import os
from datetime import datetime

def initialize_database():
    """Initialize complete database with all tables"""
    
    print("Initializing complete database...")
    
    # Ensure backend directory exists
    os.makedirs("backend", exist_ok=True)
    
    conn = sqlite3.connect('backend/quiz.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student',
            full_name TEXT,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Create quizzes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            teacher_id INTEGER,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            duration INTEGER DEFAULT 30,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users (id)
        )
    ''')
    
    # Create questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER,
            question_text TEXT NOT NULL,
            question_type TEXT DEFAULT 'multiple_choice',
            options TEXT,
            correct_answer TEXT,
            points INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
        )
    ''')
    
    # Create student_answers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            quiz_id INTEGER,
            question_id INTEGER,
            answer TEXT,
            is_correct BOOLEAN,
            points_earned INTEGER DEFAULT 0,
            answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users (id),
            FOREIGN KEY (quiz_id) REFERENCES quizzes (id),
            FOREIGN KEY (question_id) REFERENCES questions (id)
        )
    ''')
    
    # Create DOS teacher registration table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dos_teacher_registration (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            school_name TEXT NOT NULL,
            district TEXT NOT NULL,
            sector TEXT NOT NULL,
            subject_specialization TEXT NOT NULL,
            qualification TEXT NOT NULL,
            experience_years INTEGER,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',
            approved_by TEXT,
            approval_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create RTB templates table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rtb_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_type TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            teacher_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users (id)
        )
    ''')
    
    # Insert default admin users
    admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
    dos_password = hashlib.sha256('dos123'.encode()).hexdigest()
    
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password, role, full_name, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', ('admin', admin_password, 'admin', 'System Administrator', datetime.now().isoformat()))
    
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password, role, full_name, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', ('dos_admin', dos_password, 'admin', 'DOS Administrator', datetime.now().isoformat()))
    
    # Insert sample students
    student_password = hashlib.sha256('pass123'.encode()).hexdigest()
    
    for i in range(1, 6):
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, password, role, full_name, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (f'student{i:03d}', student_password, 'student', f'Student {i:03d}', datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    print("Database initialized successfully!")
    return True

def verify_system_files():
    """Verify all required system files exist"""
    
    print("Verifying system files...")
    
    required_files = {
        'backend': [
            'backend/main.py',
            'backend/rtb_complete_api.py',
            'backend/rtb_complete_generator.py',
            'backend/rtb_scheme_generator.py'
        ],
        'frontend': [
            'frontend/package.json',
            'frontend/rtb_complete_interface.html'
        ],
        'scripts': [
            'COMPLETE_SYSTEM_RESTART.bat',
            'dos_teacher_registration.py'
        ]
    }
    
    all_good = True
    
    for category, files in required_files.items():
        print(f"\n{category.upper()} FILES:")
        for file in files:
            if os.path.exists(file):
                print(f"  OK: {file}")
            else:
                print(f"  MISSING: {file}")
                all_good = False
    
    return all_good

def create_sample_data():
    """Create sample quiz data for testing"""
    
    print("Creating sample data...")
    
    conn = sqlite3.connect('backend/quiz.db')
    cursor = conn.cursor()
    
    # Create sample quiz
    cursor.execute('''
        INSERT OR IGNORE INTO quizzes (title, description, teacher_id, duration)
        VALUES (?, ?, ?, ?)
    ''', ('Sample Quiz', 'Test quiz for system verification', 1, 30))
    
    quiz_id = cursor.lastrowid or 1
    
    # Create sample questions
    questions = [
        {
            'text': 'What is the capital of Rwanda?',
            'options': '["Kigali", "Butare", "Gisenyi", "Ruhengeri"]',
            'correct': 'Kigali'
        },
        {
            'text': 'Which programming language is used for web development?',
            'options': '["Python", "JavaScript", "Java", "C++"]',
            'correct': 'JavaScript'
        }
    ]
    
    for q in questions:
        cursor.execute('''
            INSERT OR IGNORE INTO questions (quiz_id, question_text, options, correct_answer)
            VALUES (?, ?, ?, ?)
        ''', (quiz_id, q['text'], q['options'], q['correct']))
    
    conn.commit()
    conn.close()
    
    print("Sample data created!")

def main():
    """Initialize complete system"""
    
    print("=== COMPLETE SYSTEM INITIALIZATION ===\n")
    
    # 1. Initialize database
    if initialize_database():
        print("✓ Database initialization complete")
    
    # 2. Verify files
    if verify_system_files():
        print("✓ All system files present")
    else:
        print("! Some files missing - system may not work properly")
    
    # 3. Create sample data
    create_sample_data()
    print("✓ Sample data created")
    
    print("\n=== SYSTEM READY ===")
    print("\nDefault Login Credentials:")
    print("Admin: admin / admin123")
    print("DOS Admin: dos_admin / dos123")
    print("Students: student001-005 / pass123")
    
    print("\nTo start the system:")
    print("Run: COMPLETE_SYSTEM_RESTART.bat")
    
    return True

if __name__ == "__main__":
    main()