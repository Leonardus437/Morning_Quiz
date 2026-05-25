-- Initialize database with sample data and CORRECT password hashes

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student',
    full_name VARCHAR(100),
    department VARCHAR(100),
    level VARCHAR(20),
    departments JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default admin user with CORRECT hash for 'pass123'
INSERT INTO users (username, password_hash, role, full_name, departments) VALUES 
('admin', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'admin', 'System Administrator', '["Software Development", "Computer System and Architecture", "Land Surveying", "Building Construction"]');

-- Insert sample teachers with CORRECT hash for 'pass123'
INSERT INTO users (username, password_hash, role, full_name, departments) VALUES 
('teacher001', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'teacher', 'Prof. Sarah Connor', '["Software Development", "Computer System and Architecture"]'),
('teacher002', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'teacher', 'Dr. John Mitchell', '["Land Surveying", "Building Construction"]'),
('teacher003', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'teacher', 'Ms. Lisa Anderson', '["Computer System and Architecture"]');

-- Insert sample students with CORRECT hash for 'pass123'
INSERT INTO users (username, password_hash, role, full_name, department, level) VALUES 
('student001', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'student', 'Alice Johnson', 'Software Development', 'Level 3'),
('student002', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'student', 'Bob Smith', 'Computer System and Architecture', 'Level 4'),
('student003', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'student', 'Carol Davis', 'Computer System and Architecture', 'Level 5'),
('student004', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'student', 'David Wilson', 'Land Surveying', 'Level 3'),
('student005', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'student', 'Emma Brown', 'Building Construction', 'Level 4'),
('student006', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'student', 'Frank Miller', 'Software Development', 'Level 5'),
('student007', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'student', 'Grace Lee', 'Land Surveying', 'Level 5'),
('student008', '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'student', 'Henry Taylor', 'Building Construction', 'Level 5');