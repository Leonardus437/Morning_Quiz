"""
Pillar A: Dual-Mode Database (SQLite ↔ PostgreSQL)
Auto-switches based on OFFLINE_MODE and DATABASE_URL
"""
import os
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "")
OFFLINE_MODE = os.getenv("OFFLINE_MODE", "false").lower() == "true"
SQLITE_PATH = os.getenv("SQLITE_PATH", "./data/exam_local.db")

# Determine database engine
if OFFLINE_MODE and not DATABASE_URL.startswith("postgresql"):
    # SQLite mode for offline
    os.makedirs(os.path.dirname(SQLITE_PATH) or ".", exist_ok=True)
    DATABASE_URL = f"sqlite:///{SQLITE_PATH}"
    database_type = "sqlite"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    print(f"🔒 OFFLINE MODE: Using SQLite at {SQLITE_PATH}")
else:
    # PostgreSQL mode for cloud/LAN
    database_type = "postgresql"
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)
    print(f"☁️  ONLINE MODE: Using PostgreSQL")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency for FastAPI routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database and seed admin if offline"""
    Base.metadata.create_all(bind=engine)
    
    if OFFLINE_MODE:
        seed_admin_user()

def seed_admin_user():
    """Seed admin user for offline mode"""
    from passlib.context import CryptContext
    
    email = os.getenv("SEED_ADMIN_EMAIL", "admin@offline.local")
    password = os.getenv("SEED_ADMIN_PASSWORD", "admin123")
    
    db = SessionLocal()
    try:
        # Check if admin exists (import here to avoid circular dependency)
        from sqlalchemy import text
        result = db.execute(text("SELECT COUNT(*) FROM users WHERE email = :email"), {"email": email})
        if result.scalar() == 0:
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            hashed = pwd_context.hash(password)
            db.execute(text(
                "INSERT INTO users (email, username, password_hash, role, is_active) "
                "VALUES (:email, :username, :password, 'teacher', true)"
            ), {"email": email, "username": "admin", "password": hashed})
            db.commit()
            print(f"✅ Seeded admin user: {email}")
    except Exception as e:
        print(f"⚠️  Admin seed skipped: {e}")
    finally:
        db.close()
