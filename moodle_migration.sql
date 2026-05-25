-- Moodle-Level Features Migration (SQL Version)
-- Safe, additive-only database changes - NO breaking changes

-- 1. Add feedback columns to questions (nullable - won't break existing)
ALTER TABLE questions 
ADD COLUMN IF NOT EXISTS general_feedback TEXT,
ADD COLUMN IF NOT EXISTS correct_feedback TEXT,
ADD COLUMN IF NOT EXISTS incorrect_feedback TEXT,
ADD COLUMN IF NOT EXISTS category TEXT,
ADD COLUMN IF NOT EXISTS tags TEXT,
ADD COLUMN IF NOT EXISTS difficulty TEXT,
ADD COLUMN IF NOT EXISTS image_url TEXT;

-- 2. Add partial credit support (nullable)
ALTER TABLE questions
ADD COLUMN IF NOT EXISTS partial_credit_enabled BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS partial_credit_rules TEXT;

-- 3. Add question categories table (new table - safe)
CREATE TABLE IF NOT EXISTS question_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    parent_id INTEGER REFERENCES question_categories(id),
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Add immediate feedback to student answers (nullable)
ALTER TABLE student_answers
ADD COLUMN IF NOT EXISTS immediate_feedback TEXT,
ADD COLUMN IF NOT EXISTS hint_used BOOLEAN DEFAULT false;

-- 5. Add quiz settings for immediate feedback (nullable)
ALTER TABLE quizzes
ADD COLUMN IF NOT EXISTS show_immediate_feedback BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS show_correct_answers BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS allow_multiple_attempts BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS max_attempts INTEGER DEFAULT 1;

-- Verify migration
SELECT 'Migration completed successfully!' as status;
