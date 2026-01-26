#!/usr/bin/env python3
"""
Manual database migration script for Render PostgreSQL
Run this to add missing columns to production database
"""
import os
import psycopg2
from psycopg2 import sql

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL environment variable not set")
    exit(1)

print(f"🔗 Connecting to database...")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("✅ Connected successfully")
    
    # List of migrations to run
    migrations = [
        # Phase 1: Advanced question types
        "ALTER TABLE questions ADD COLUMN IF NOT EXISTS question_config JSON",
        "ALTER TABLE questions ADD COLUMN IF NOT EXISTS media_url VARCHAR",
        "ALTER TABLE questions ADD COLUMN IF NOT EXISTS correct_answers JSON",
        "ALTER TABLE questions ADD COLUMN IF NOT EXISTS partial_credit BOOLEAN DEFAULT FALSE",
        
        # Quiz attempts enhancements
        "ALTER TABLE quiz_attempts ADD COLUMN IF NOT EXISTS percentage FLOAT DEFAULT 0.0",
        "ALTER TABLE quiz_attempts ADD COLUMN IF NOT EXISTS grade VARCHAR(5) DEFAULT 'F'",
        "ALTER TABLE quiz_attempts ADD COLUMN IF NOT EXISTS total_possible_points FLOAT DEFAULT 0.0",
        "ALTER TABLE quiz_attempts ADD COLUMN IF NOT EXISTS needs_review BOOLEAN DEFAULT FALSE",
        "ALTER TABLE quiz_attempts ADD COLUMN IF NOT EXISTS reviewed_by INTEGER",
        "ALTER TABLE quiz_attempts ADD COLUMN IF NOT EXISTS final_score FLOAT",
        
        # Student answers enhancements
        "ALTER TABLE student_answers ADD COLUMN IF NOT EXISTS points_earned FLOAT DEFAULT 0.0",
        "ALTER TABLE student_answers ADD COLUMN IF NOT EXISTS ai_feedback VARCHAR",
        "ALTER TABLE student_answers ADD COLUMN IF NOT EXISTS teacher_score FLOAT",
        "ALTER TABLE student_answers ADD COLUMN IF NOT EXISTS teacher_feedback TEXT",
        
        # Quiz results release
        "ALTER TABLE quizzes ADD COLUMN IF NOT EXISTS results_released BOOLEAN DEFAULT FALSE",
        
        # Chat system enhancements
        "ALTER TABLE chat_rooms ADD COLUMN IF NOT EXISTS module_id INTEGER",
        "ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS file_url VARCHAR",
        "ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS file_name VARCHAR",
        "ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS reply_to_id INTEGER",
    ]
    
    print(f"\n📋 Running {len(migrations)} migrations...\n")
    
    for i, migration in enumerate(migrations, 1):
        try:
            print(f"[{i}/{len(migrations)}] {migration[:60]}...")
            cur.execute(migration)
            conn.commit()
            print(f"    ✅ Success")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                print(f"    ⚠️  Column already exists (skipped)")
                conn.rollback()
            else:
                print(f"    ❌ Failed: {e}")
                conn.rollback()
    
    print(f"\n🎉 Migration complete!")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Database error: {e}")
    exit(1)
