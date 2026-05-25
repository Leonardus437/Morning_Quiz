"""
Database Migration: Add Manual Review System
Run this after updating main.py models
"""

# SQL for SQLite (development)
SQLITE_MIGRATION = """
-- Add grading mode to quizzes
ALTER TABLE quizzes ADD COLUMN grading_mode VARCHAR(20) DEFAULT 'auto';
ALTER TABLE quizzes ADD COLUMN results_released BOOLEAN DEFAULT 0;

-- Add review fields to quiz_attempts
ALTER TABLE quiz_attempts ADD COLUMN needs_review BOOLEAN DEFAULT 0;
ALTER TABLE quiz_attempts ADD COLUMN reviewed_by INTEGER;
ALTER TABLE quiz_attempts ADD COLUMN reviewed_at DATETIME;
ALTER TABLE quiz_attempts ADD COLUMN final_score FLOAT;
ALTER TABLE quiz_attempts ADD COLUMN ai_confidence FLOAT DEFAULT 1.0;

-- Add teacher grading fields to student_answers
ALTER TABLE student_answers ADD COLUMN teacher_score FLOAT;
ALTER TABLE student_answers ADD COLUMN teacher_feedback TEXT;
ALTER TABLE student_answers ADD COLUMN review_status VARCHAR(20) DEFAULT 'pending';
ALTER TABLE student_answers ADD COLUMN ai_confidence FLOAT DEFAULT 1.0;
"""

# SQL for PostgreSQL (production)
POSTGRESQL_MIGRATION = """
-- Add grading mode to quizzes
ALTER TABLE quizzes ADD COLUMN IF NOT EXISTS grading_mode VARCHAR(20) DEFAULT 'auto';
ALTER TABLE quizzes ADD COLUMN IF NOT EXISTS results_released BOOLEAN DEFAULT FALSE;

-- Add review fields to quiz_attempts
ALTER TABLE quiz_attempts ADD COLUMN IF NOT EXISTS needs_review BOOLEAN DEFAULT FALSE;
ALTER TABLE quiz_attempts ADD COLUMN IF NOT EXISTS reviewed_by INTEGER REFERENCES users(id);
ALTER TABLE quiz_attempts ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMP;
ALTER TABLE quiz_attempts ADD COLUMN IF NOT EXISTS final_score FLOAT;
ALTER TABLE quiz_attempts ADD COLUMN IF NOT EXISTS ai_confidence FLOAT DEFAULT 1.0;

-- Add teacher grading fields to student_answers
ALTER TABLE student_answers ADD COLUMN IF NOT EXISTS teacher_score FLOAT;
ALTER TABLE student_answers ADD COLUMN IF NOT EXISTS teacher_feedback TEXT;
ALTER TABLE student_answers ADD COLUMN IF NOT EXISTS review_status VARCHAR(20) DEFAULT 'pending';
ALTER TABLE student_answers ADD COLUMN IF NOT EXISTS ai_confidence FLOAT DEFAULT 1.0;
"""

if __name__ == "__main__":
    print("Manual Review System Migration")
    print("=" * 50)
    print("\nFor SQLite (local development):")
    print(SQLITE_MIGRATION)
    print("\nFor PostgreSQL (production):")
    print(POSTGRESQL_MIGRATION)
    print("\nNote: These will be applied automatically when you restart the backend")
