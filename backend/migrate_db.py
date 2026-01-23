"""Add missing columns to production database"""
import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set")
    exit(1)

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    try:
        # Add results_released column to quizzes table
        conn.execute(text("ALTER TABLE quizzes ADD COLUMN IF NOT EXISTS results_released BOOLEAN DEFAULT FALSE"))
        conn.commit()
        print("✅ Added results_released column to quizzes table")
    except Exception as e:
        print(f"❌ Error: {e}")
        
    try:
        # Add teacher review columns to quiz_attempts table
        conn.execute(text("ALTER TABLE quiz_attempts ADD COLUMN IF NOT EXISTS needs_review BOOLEAN DEFAULT FALSE"))
        conn.execute(text("ALTER TABLE quiz_attempts ADD COLUMN IF NOT EXISTS reviewed_by INTEGER"))
        conn.execute(text("ALTER TABLE quiz_attempts ADD COLUMN IF NOT EXISTS final_score FLOAT"))
        conn.commit()
        print("✅ Added review columns to quiz_attempts table")
    except Exception as e:
        print(f"❌ Error: {e}")
        
    try:
        # Add teacher grading columns to student_answers table
        conn.execute(text("ALTER TABLE student_answers ADD COLUMN IF NOT EXISTS teacher_score FLOAT"))
        conn.execute(text("ALTER TABLE student_answers ADD COLUMN IF NOT EXISTS teacher_feedback TEXT"))
        conn.commit()
        print("✅ Added teacher grading columns to student_answers table")
    except Exception as e:
        print(f"❌ Error: {e}")

print("✅ Database migration complete!")
