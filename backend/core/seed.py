"""
Offline Mode Seeding System
Auto-creates admin user when running in offline SQLite mode
"""

import os
import hashlib
import secrets
from sqlalchemy.orm import Session
from datetime import datetime

# Environment variables for seeding
SEED_ADMIN_EMAIL = os.getenv("SEED_ADMIN_EMAIL", "admin")
SEED_ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD", "admin123")
SEED_TEACHER_USERNAME = os.getenv("SEED_TEACHER_USERNAME", "teacher001")
SEED_TEACHER_PASSWORD = os.getenv("SEED_TEACHER_PASSWORD", "teacher123")


def hash_password_simple(password: str) -> str:
    """
    Simple password hashing compatible with existing system
    Uses bcrypt if available, falls back to SHA256+salt
    """
    try:
        import bcrypt
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    except ImportError:
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"


def seed_offline_users(db: Session, User):
    """
    Seed essential users for offline mode
    
    Args:
        db: SQLAlchemy session
        User: User model class
    """
    print("🌱 Seeding offline mode users...")
    
    # Check if admin exists
    admin = db.query(User).filter(User.username == SEED_ADMIN_EMAIL).first()
    if not admin:
        admin = User(
            username=SEED_ADMIN_EMAIL,
            password_hash=hash_password_simple(SEED_ADMIN_PASSWORD),
            role="admin",
            full_name="Offline Administrator",
            departments=["Software Development", "Computer System and Architecture"],
            created_at=datetime.utcnow()
        )
        db.add(admin)
        print(f"✅ Created admin user: {SEED_ADMIN_EMAIL}")
    else:
        print(f"ℹ️  Admin user already exists: {SEED_ADMIN_EMAIL}")
    
    # Check if default teacher exists
    teacher = db.query(User).filter(User.username == SEED_TEACHER_USERNAME).first()
    if not teacher:
        teacher = User(
            username=SEED_TEACHER_USERNAME,
            password_hash=hash_password_simple(SEED_TEACHER_PASSWORD),
            role="teacher",
            full_name="Default Teacher",
            departments=["Software Development"],
            created_at=datetime.utcnow()
        )
        db.add(teacher)
        print(f"✅ Created teacher user: {SEED_TEACHER_USERNAME}")
    else:
        print(f"ℹ️  Teacher user already exists: {SEED_TEACHER_USERNAME}")
    
    # Create sample student for testing
    student = db.query(User).filter(User.username == "student001").first()
    if not student:
        student = User(
            username="student001",
            password_hash=hash_password_simple("pass123"),
            role="student",
            full_name="Sample Student",
            department="Software Development",
            level="L5",
            created_at=datetime.utcnow()
        )
        db.add(student)
        print(f"✅ Created sample student: student001")
    else:
        print(f"ℹ️  Sample student already exists: student001")
    
    db.commit()
    print("🌱 Offline seeding completed!")


def seed_offline_data(db: Session, models_dict: dict):
    """
    Seed all necessary data for offline mode
    
    Args:
        db: SQLAlchemy session
        models_dict: Dictionary of model classes (User, Lesson, etc.)
    """
    User = models_dict.get('User')
    
    if User:
        seed_offline_users(db, User)
    
    # Add more seeding functions here as needed
    # seed_sample_lessons(db, models_dict.get('Lesson'))
    # seed_sample_questions(db, models_dict.get('Question'))


def initialize_offline_database(engine, Base, models_dict: dict):
    """
    Initialize database for offline mode
    Creates all tables and seeds initial data
    
    Args:
        engine: SQLAlchemy engine
        Base: Declarative base
        models_dict: Dictionary of model classes
    """
    print("🔧 Initializing offline database...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    # Seed initial data
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        seed_offline_data(db, models_dict)
    except Exception as e:
        print(f"⚠️  Seeding error: {e}")
        db.rollback()
    finally:
        db.close()
    
    print("✅ Offline database initialized!")


def get_offline_credentials():
    """
    Return default credentials for offline mode
    Useful for generating setup instructions
    """
    return {
        "admin": {
            "username": SEED_ADMIN_EMAIL,
            "password": SEED_ADMIN_PASSWORD,
            "role": "admin"
        },
        "teacher": {
            "username": SEED_TEACHER_USERNAME,
            "password": SEED_TEACHER_PASSWORD,
            "role": "teacher"
        },
        "student": {
            "username": "student001",
            "password": "pass123",
            "role": "student"
        }
    }
