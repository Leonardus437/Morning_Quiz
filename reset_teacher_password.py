"""
Reset Teacher Password Script
Run this to reset a teacher's password if they can't login
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

def reset_teacher_password(username, new_password):
    """Reset a teacher's password"""
    db = SessionLocal()
    try:
        # Find teacher
        teacher = db.query(User).filter(User.username == username).first()
        
        if not teacher:
            print(f"❌ Teacher '{username}' not found")
            return False
        
        if teacher.role != "teacher":
            print(f"❌ User '{username}' is not a teacher (role: {teacher.role})")
            return False
        
        # Hash new password
        new_hash = hash_password_simple(new_password)
        
        # Update password
        teacher.password_hash = new_hash
        db.commit()
        
        print(f"✅ Password reset successful for teacher: {username}")
        print(f"   Full Name: {teacher.full_name}")
        print(f"   New Password: {new_password}")
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
    print("TEACHER PASSWORD RESET TOOL")
    print("=" * 60)
    print()
    
    # Get username
    username = input("Enter teacher username (e.g., UWAMARIYA): ").strip()
    
    if not username:
        print("❌ Username cannot be empty")
        sys.exit(1)
    
    # Get new password
    new_password = input("Enter new password (e.g., teacher123): ").strip()
    
    if not new_password:
        print("❌ Password cannot be empty")
        sys.exit(1)
    
    print()
    print(f"Resetting password for: {username}")
    print(f"New password: {new_password}")
    print()
    
    confirm = input("Continue? (yes/no): ").strip().lower()
    
    if confirm == "yes":
        reset_teacher_password(username, new_password)
    else:
        print("❌ Cancelled")
