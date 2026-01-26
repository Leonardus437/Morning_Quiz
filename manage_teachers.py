"""
Teacher Management Script
List all teachers and register new ones
"""

import sys
sys.path.append('backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Import from main
from main import User, hash_password_simple

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///backend/quiz.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def list_all_teachers():
    """List all teachers in the database"""
    db = SessionLocal()
    try:
        teachers = db.query(User).filter(User.role == "teacher").all()
        
        if not teachers:
            print("❌ No teachers found in database")
            return []
        
        print(f"✅ Found {len(teachers)} teacher(s):")
        print()
        for i, teacher in enumerate(teachers, 1):
            print(f"{i}. Username: {teacher.username}")
            print(f"   Full Name: {teacher.full_name}")
            print(f"   Departments: {teacher.departments}")
            print(f"   Created: {teacher.created_at}")
            print()
        
        return teachers
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []
    finally:
        db.close()

def register_teacher(username, password, full_name, departments):
    """Register a new teacher"""
    db = SessionLocal()
    try:
        # Check if username exists
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            print(f"❌ Username '{username}' already exists")
            return False
        
        # Create teacher
        teacher = User(
            username=username,
            password_hash=hash_password_simple(password),
            role="teacher",
            full_name=full_name,
            departments=departments
        )
        
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
        
        print(f"✅ Teacher registered successfully!")
        print(f"   Username: {teacher.username}")
        print(f"   Password: {password}")
        print(f"   Full Name: {teacher.full_name}")
        print(f"   Departments: {teacher.departments}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("TEACHER MANAGEMENT TOOL")
    print("=" * 60)
    print()
    
    # List existing teachers
    print("Current Teachers in Database:")
    print("-" * 60)
    teachers = list_all_teachers()
    
    print()
    print("=" * 60)
    print()
    
    # Ask if user wants to register a new teacher
    action = input("Do you want to register a new teacher? (yes/no): ").strip().lower()
    
    if action != "yes":
        print("Exiting...")
        sys.exit(0)
    
    print()
    print("Register New Teacher")
    print("-" * 60)
    
    # Get teacher details
    username = input("Username (e.g., UWAMARIYA): ").strip()
    if not username:
        print("❌ Username cannot be empty")
        sys.exit(1)
    
    password = input("Password (e.g., 12345678): ").strip()
    if not password:
        print("❌ Password cannot be empty")
        sys.exit(1)
    
    full_name = input("Full Name (e.g., UWAMARIYA Jean): ").strip()
    if not full_name:
        print("❌ Full name cannot be empty")
        sys.exit(1)
    
    print()
    print("Available Departments:")
    print("1. Software Development")
    print("2. Computer System and Architecture")
    print("3. Land Surveying")
    print("4. Building Construction")
    print()
    
    dept_input = input("Enter department numbers (comma-separated, e.g., 1,2): ").strip()
    
    dept_map = {
        "1": "Software Development",
        "2": "Computer System and Architecture",
        "3": "Land Surveying",
        "4": "Building Construction"
    }
    
    departments = []
    for num in dept_input.split(","):
        num = num.strip()
        if num in dept_map:
            departments.append(dept_map[num])
    
    if not departments:
        print("❌ At least one department must be selected")
        sys.exit(1)
    
    print()
    print("Summary:")
    print(f"  Username: {username}")
    print(f"  Password: {password}")
    print(f"  Full Name: {full_name}")
    print(f"  Departments: {departments}")
    print()
    
    confirm = input("Register this teacher? (yes/no): ").strip().lower()
    
    if confirm == "yes":
        register_teacher(username, password, full_name, departments)
    else:
        print("❌ Cancelled")
