"""
Migration script to add missing columns to assignments table
Run this once to fix the Railway database schema
"""
from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:etFcYsqQeDTEJBvBGdZOVNlVdLLPDvLG@shinkansen.proxy.rlwy.net:42954/railway")

engine = create_engine(DATABASE_URL)

def migrate():
    with engine.connect() as conn:
        # Add missing columns if they don't exist
        try:
            conn.execute(text("ALTER TABLE assignments ADD COLUMN IF NOT EXISTS assignment_type VARCHAR(50) DEFAULT 'document'"))
            conn.execute(text("ALTER TABLE assignments ADD COLUMN IF NOT EXISTS allow_late_submission BOOLEAN DEFAULT false"))
            conn.execute(text("ALTER TABLE assignments ADD COLUMN IF NOT EXISTS is_published BOOLEAN DEFAULT false"))
            conn.commit()
            print("✅ Migration completed successfully")
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            conn.rollback()

if __name__ == "__main__":
    migrate()
