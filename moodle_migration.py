"""
Moodle-Level Features Migration
Safe, additive-only database changes - NO breaking changes
"""

from sqlalchemy import text
from main import engine, SessionLocal

def run_migration():
    """Add Moodle-level feature columns without breaking existing data"""
    db = SessionLocal()
    
    try:
        print("🚀 Starting Moodle-level features migration...")
        
        # 1. Add feedback columns to questions (nullable - won't break existing)
        print("📝 Adding feedback columns to questions...")
        db.execute(text("""
            ALTER TABLE questions 
            ADD COLUMN IF NOT EXISTS general_feedback TEXT,
            ADD COLUMN IF NOT EXISTS correct_feedback TEXT,
            ADD COLUMN IF NOT EXISTS incorrect_feedback TEXT,
            ADD COLUMN IF NOT EXISTS category TEXT,
            ADD COLUMN IF NOT EXISTS tags TEXT,
            ADD COLUMN IF NOT EXISTS difficulty TEXT,
            ADD COLUMN IF NOT EXISTS image_url TEXT
        """))
        
        # 2. Add partial credit support (nullable)
        print("📊 Adding partial credit support...")
        db.execute(text("""
            ALTER TABLE questions
            ADD COLUMN IF NOT EXISTS partial_credit_enabled BOOLEAN DEFAULT false,
            ADD COLUMN IF NOT EXISTS partial_credit_rules TEXT
        """))
        
        # 3. Add question categories table (new table - safe)
        print("📂 Creating question categories table...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS question_categories (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                parent_id INTEGER REFERENCES question_categories(id),
                created_by INTEGER REFERENCES users(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # 4. Add immediate feedback to student answers (nullable)
        print("💬 Adding immediate feedback columns...")
        db.execute(text("""
            ALTER TABLE student_answers
            ADD COLUMN IF NOT EXISTS immediate_feedback TEXT,
            ADD COLUMN IF NOT EXISTS hint_used BOOLEAN DEFAULT false
        """))
        
        # 5. Add quiz settings for immediate feedback (nullable)
        print("⚙️ Adding quiz feedback settings...")
        db.execute(text("""
            ALTER TABLE quizzes
            ADD COLUMN IF NOT EXISTS show_immediate_feedback BOOLEAN DEFAULT false,
            ADD COLUMN IF NOT EXISTS show_correct_answers BOOLEAN DEFAULT false,
            ADD COLUMN IF NOT EXISTS allow_multiple_attempts BOOLEAN DEFAULT false,
            ADD COLUMN IF NOT EXISTS max_attempts INTEGER DEFAULT 1
        """))
        
        db.commit()
        print("✅ Migration completed successfully!")
        print("✅ All existing data preserved - NO breaking changes")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    run_migration()
