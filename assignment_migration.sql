-- Assignment Management System Migration
-- Intelligent LMS with file uploads, submissions, grading, and analytics

-- 1. Assignments table
CREATE TABLE IF NOT EXISTS assignments (
    id SERIAL PRIMARY KEY,
    teacher_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    instructions TEXT,
    due_date TIMESTAMP,
    max_score FLOAT DEFAULT 100,
    allow_late_submission BOOLEAN DEFAULT FALSE,
    submission_type VARCHAR(50) DEFAULT 'file', -- file, text, link, both
    file_types_allowed TEXT[], -- ['pdf', 'docx', 'txt', 'zip']
    max_file_size INTEGER DEFAULT 10485760, -- 10MB in bytes
    school_id INTEGER REFERENCES schools(id),
    trade_id INTEGER REFERENCES trades(id),
    level VARCHAR(10),
    status VARCHAR(20) DEFAULT 'draft', -- draft, published, closed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_assignments_teacher ON assignments(teacher_id);
CREATE INDEX idx_assignments_school ON assignments(school_id);
CREATE INDEX idx_assignments_status ON assignments(status);
CREATE INDEX idx_assignments_due_date ON assignments(due_date);

-- 2. Assignment attachments (teacher uploads)
CREATE TABLE IF NOT EXISTS assignment_attachments (
    id SERIAL PRIMARY KEY,
    assignment_id INTEGER NOT NULL REFERENCES assignments(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    file_type VARCHAR(50),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_attachments_assignment ON assignment_attachments(assignment_id);

-- 3. Student submissions
CREATE TABLE IF NOT EXISTS assignment_submissions (
    id SERIAL PRIMARY KEY,
    assignment_id INTEGER NOT NULL REFERENCES assignments(id) ON DELETE CASCADE,
    student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    submission_text TEXT,
    submission_link TEXT,
    status VARCHAR(20) DEFAULT 'pending', -- pending, submitted, graded, returned
    submitted_at TIMESTAMP,
    graded_at TIMESTAMP,
    score FLOAT,
    feedback TEXT,
    ai_feedback TEXT,
    late_submission BOOLEAN DEFAULT FALSE,
    attempt_number INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(assignment_id, student_id, attempt_number)
);

CREATE INDEX idx_submissions_assignment ON assignment_submissions(assignment_id);
CREATE INDEX idx_submissions_student ON assignment_submissions(student_id);
CREATE INDEX idx_submissions_status ON assignment_submissions(status);

-- 4. Submission files (student uploads)
CREATE TABLE IF NOT EXISTS submission_files (
    id SERIAL PRIMARY KEY,
    submission_id INTEGER NOT NULL REFERENCES assignment_submissions(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    file_type VARCHAR(50),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_submission_files_submission ON submission_files(submission_id);

-- 5. Assignment analytics
CREATE TABLE IF NOT EXISTS assignment_analytics (
    id SERIAL PRIMARY KEY,
    assignment_id INTEGER NOT NULL REFERENCES assignments(id) ON DELETE CASCADE,
    total_students INTEGER DEFAULT 0,
    submitted_count INTEGER DEFAULT 0,
    pending_count INTEGER DEFAULT 0,
    graded_count INTEGER DEFAULT 0,
    average_score FLOAT,
    on_time_submissions INTEGER DEFAULT 0,
    late_submissions INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(assignment_id)
);

CREATE INDEX idx_analytics_assignment ON assignment_analytics(assignment_id);

-- 6. Student assignment views (track engagement)
CREATE TABLE IF NOT EXISTS assignment_views (
    id SERIAL PRIMARY KEY,
    assignment_id INTEGER NOT NULL REFERENCES assignments(id) ON DELETE CASCADE,
    student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    view_count INTEGER DEFAULT 1,
    first_viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(assignment_id, student_id)
);

CREATE INDEX idx_views_assignment ON assignment_views(assignment_id);
CREATE INDEX idx_views_student ON assignment_views(student_id);

-- Trigger to update assignment analytics
CREATE OR REPLACE FUNCTION update_assignment_analytics()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO assignment_analytics (
        assignment_id,
        total_students,
        submitted_count,
        pending_count,
        graded_count,
        average_score,
        on_time_submissions,
        late_submissions
    )
    SELECT 
        NEW.assignment_id,
        COUNT(DISTINCT student_id),
        COUNT(CASE WHEN status IN ('submitted', 'graded', 'returned') THEN 1 END),
        COUNT(CASE WHEN status = 'pending' THEN 1 END),
        COUNT(CASE WHEN status IN ('graded', 'returned') THEN 1 END),
        AVG(CASE WHEN score IS NOT NULL THEN score END),
        COUNT(CASE WHEN late_submission = FALSE AND status IN ('submitted', 'graded', 'returned') THEN 1 END),
        COUNT(CASE WHEN late_submission = TRUE THEN 1 END)
    FROM assignment_submissions
    WHERE assignment_id = NEW.assignment_id
    ON CONFLICT (assignment_id) 
    DO UPDATE SET
        submitted_count = EXCLUDED.submitted_count,
        pending_count = EXCLUDED.pending_count,
        graded_count = EXCLUDED.graded_count,
        average_score = EXCLUDED.average_score,
        on_time_submissions = EXCLUDED.on_time_submissions,
        late_submissions = EXCLUDED.late_submissions,
        last_updated = CURRENT_TIMESTAMP;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_assignment_analytics ON assignment_submissions;
CREATE TRIGGER trigger_update_assignment_analytics
AFTER INSERT OR UPDATE ON assignment_submissions
FOR EACH ROW
EXECUTE FUNCTION update_assignment_analytics();

-- Function to check if submission is late
CREATE OR REPLACE FUNCTION check_late_submission()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.submitted_at IS NOT NULL THEN
        SELECT 
            CASE 
                WHEN due_date IS NOT NULL AND NEW.submitted_at > due_date 
                THEN TRUE 
                ELSE FALSE 
            END INTO NEW.late_submission
        FROM assignments
        WHERE id = NEW.assignment_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_check_late_submission ON assignment_submissions;
CREATE TRIGGER trigger_check_late_submission
BEFORE INSERT OR UPDATE ON assignment_submissions
FOR EACH ROW
EXECUTE FUNCTION check_late_submission();

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'SUCCESS: Assignment system tables created successfully!';
END $$;
