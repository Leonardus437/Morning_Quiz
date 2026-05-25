"""
Rollback Script for Moodle Features
Use this if anything breaks - 100% safe rollback
"""

from sqlalchemy import text
from main import SessionLocal

def rollback_migration():
    """Remove Moodle-level features - restore to original state"""
    db = SessionLocal()
    
    try:
        print("🔄 Rolling back Moodle features...")
        
        # Drop new columns from questions
        print("📝 Removing feedback columns from questions...")
        db.execute(text("""
            ALTER TABLE questions 
            DROP COLUMN IF EXISTS general_feedback,
            DROP COLUMN IF EXISTS correct_feedback,
            DROP COLUMN IF EXISTS incorrect_feedback,
            DROP COLUMN IF EXISTS category,
            DROP COLUMN IF EXISTS tags,
            DROP COLUMN IF EXISTS difficulty,
            DROP COLUMN IF EXISTS image_url,
            DROP COLUMN IF EXISTS partial_credit_enabled,
            DROP COLUMN IF EXISTS partial_credit_rules
        """))
        
        # Drop question categories table
        print("📂 Removing question categories table...")
        db.execute(text("DROP TABLE IF EXISTS question_categories CASCADE"))
        
        # Drop new columns from student_answers
        print("💬 Removing immediate feedback columns...")
        db.execute(text("""
            ALTER TABLE student_answers
            DROP COLUMN IF EXISTS immediate_feedback,
            DROP COLUMN IF EXISTS hint_used
        """))
        
        # Drop new columns from quizzes
        print("⚙️ Removing quiz feedback settings...")
        db.execute(text("""
            ALTER TABLE quizzes
            DROP COLUMN IF EXISTS show_immediate_feedback,
            DROP COLUMN IF EXISTS show_correct_answers,
            DROP COLUMN IF EXISTS allow_multiple_attempts,
            DROP COLUMN IF EXISTS max_attempts
        """))
        
        db.commit()
        print("✅ Rollback completed - system restored to original state")
        print("✅ All existing data preserved")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Rollback failed: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    confirm = input("⚠️  Are you sure you want to rollback Moodle features? (yes/no): ")
    if confirm.lower() == "yes":
        rollback_migration()
    else:
        print("Rollback cancelled")
