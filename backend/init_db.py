#!/usr/bin/env python3
"""Initialize database with default users"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from main import Base, User, hash_password_simple

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://quiz_user:quiz_pass123@localhost:5432/morning_quiz")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    """Initialize database with default users"""
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    db = SessionLocal()
    
    try:
        # Create admin user
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                password_hash=hash_password_simple("admin123"),
                role="admin",
                full_name="DOS Administrator",
                departments=["Software Development", "Computer System and Architecture", "Land Surveying", "Building Construction"]
            )
            db.add(admin)
            print("✅ Created admin user: admin / admin123")
        
        # Create teachers
        teachers_data = [
            ("teacher001", "Prof. Sarah Connor", ["Software Development", "Computer System and Architecture"]),
            ("teacher002", "Dr. John Mitchell", ["Land Surveying", "Building Construction"]),
            ("teacher003", "Ms. Lisa Anderson", ["Computer System and Architecture"])
        ]
        
        for username, full_name, depts in teachers_data:
            teacher = db.query(User).filter(User.username == username).first()
            if not teacher:
                teacher = User(
                    username=username,
                    password_hash=hash_password_simple("teacher123"),
                    role="teacher",
                    full_name=full_name,
                    departments=depts
                )
                db.add(teacher)
                print(f"✅ Created teacher: {username} / teacher123")
        
        # Create sample students
        students_data = [
            ("student001", "Alice Johnson", "Software Development", "Level 3"),
            ("student002", "Bob Smith", "Computer System and Architecture", "Level 4"),
            ("student003", "Carol Davis", "Land Surveying", "Level 3")
        ]
        
        for username, full_name, dept, level in students_data:
            student = db.query(User).filter(User.username == username).first()
            if not student:
                student = User(
                    username=username,
                    password_hash=hash_password_simple("student123"),
                    role="student",
                    full_name=full_name,
                    department=dept,
                    level=level
                )
                db.add(student)
                print(f"✅ Created student: {username} / student123")
        
        db.commit()
        print("\n🎉 Database initialization complete!")
        print("\n📋 Login Credentials:")
        print("   Admin: admin / admin123")
        print("   Teacher: teacher001 / teacher123")
        print("   Student: student001 / student123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
