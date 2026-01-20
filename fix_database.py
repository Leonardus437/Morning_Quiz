#!/usr/bin/env python3
"""
Database migration script to fix field length issues
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def fix_database():
    """Fix database field length issues"""
    
    # Database setup
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///quiz.db")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    
    try:
        print("Fixing database field lengths...")
        
        # For SQLite, we need to recreate the table with new schema
        if "sqlite" in DATABASE_URL.lower():
            print("Detected SQLite database - recreating users table...")
            
            # Create backup table
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS users_backup AS 
                SELECT * FROM users
            """))
            
            # Drop existing table
            db.execute(text("DROP TABLE IF EXISTS users"))
            
            # Create new table with proper field lengths
            db.execute(text("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255),
                    role VARCHAR(20) DEFAULT 'student',
                    full_name VARCHAR(100),
                    department VARCHAR(100),
                    level VARCHAR(50),
                    departments JSON,
                    is_class_teacher BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Restore data from backup
            db.execute(text("""
                INSERT INTO users (id, username, password_hash, role, full_name, department, level, departments, is_class_teacher, created_at)
                SELECT id, username, password_hash, role, full_name, department, level, departments, is_class_teacher, created_at
                FROM users_backup
            """))
            
            # Drop backup table
            db.execute(text("DROP TABLE users_backup"))
            
        else:
            # For PostgreSQL, alter column lengths
            print("Detected PostgreSQL database - altering column lengths...")
            
            db.execute(text("ALTER TABLE users ALTER COLUMN username TYPE VARCHAR(50)"))
            db.execute(text("ALTER TABLE users ALTER COLUMN password_hash TYPE VARCHAR(255)"))
            db.execute(text("ALTER TABLE users ALTER COLUMN role TYPE VARCHAR(20)"))
            db.execute(text("ALTER TABLE users ALTER COLUMN full_name TYPE VARCHAR(100)"))
            db.execute(text("ALTER TABLE users ALTER COLUMN department TYPE VARCHAR(100)"))
            db.execute(text("ALTER TABLE users ALTER COLUMN level TYPE VARCHAR(50)"))
        
        db.commit()
        print("Database field lengths fixed successfully!")
        
        # Verify the fix by checking current users
        result = db.execute(text("SELECT COUNT(*) as count FROM users")).fetchone()
        print(f"Total users in database: {result[0] if result else 0}")
        
        # Check admin user
        admin = db.execute(text("SELECT username, role, full_name FROM users WHERE username = 'admin'")).fetchone()
        if admin:
            print(f"Admin user found: {admin[0]} ({admin[1]}) - {admin[2]}")
        else:
            print("Admin user not found - will be created on next startup")
            
    except Exception as e:
        print(f"Error fixing database: {e}")
        db.rollback()
        return False
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    print("Starting database migration...")
    success = fix_database()
    if success:
        print("Database migration completed successfully!")
        print("You can now run the student upload test again.")
    else:
        print("Database migration failed!")
        sys.exit(1)