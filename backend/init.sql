-- Initialize database with sample data

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student',
    full_name VARCHAR(100),
    department VARCHAR(100),
    level VARCHAR(20),
    departments JSONB, -- For teachers who can teach multiple departments
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Lessons/Modules table (managed by DOS)
CREATE TABLE IF NOT EXISTS lessons (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    department VARCHAR(100) NOT NULL,
    level VARCHAR(20) NOT NULL,
    classification VARCHAR(20) NOT NULL CHECK (classification IN ('Core', 'Specific', 'General')),
    is_active BOOLEAN DEFAULT true,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Teacher-Lesson assignments (managed by DOS)
CREATE TABLE IF NOT EXISTS teacher_lessons (
    id SERIAL PRIMARY KEY,
    teacher_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    lesson_id INTEGER REFERENCES lessons(id) ON DELETE CASCADE,
    assigned_by INTEGER REFERENCES users(id),
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(teacher_id, lesson_id)
);

-- Questions table
CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    question_text TEXT NOT NULL,
    question_type VARCHAR(20) NOT NULL,
    options JSONB,
    correct_answer TEXT NOT NULL,
    points INTEGER DEFAULT 1,
    department VARCHAR(100),
    level VARCHAR(20),
    lesson_id INTEGER REFERENCES lessons(id),
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Quizzes table
CREATE TABLE IF NOT EXISTS quizzes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    scheduled_time TIMESTAMP,
    duration_minutes INTEGER DEFAULT 30,
    is_active BOOLEAN DEFAULT false,
    department VARCHAR(100),
    level VARCHAR(20),
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Quiz questions junction table
CREATE TABLE IF NOT EXISTS quiz_questions (
    id SERIAL PRIMARY KEY,
    quiz_id INTEGER REFERENCES quizzes(id) ON DELETE CASCADE,
    question_id INTEGER REFERENCES questions(id) ON DELETE CASCADE,
    question_order INTEGER
);

-- Quiz attempts table
CREATE TABLE IF NOT EXISTS quiz_attempts (
    id SERIAL PRIMARY KEY,
    quiz_id INTEGER REFERENCES quizzes(id),
    user_id INTEGER REFERENCES users(id),
    score INTEGER DEFAULT 0,
    total_questions INTEGER,
    answers JSONB,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    UNIQUE(quiz_id, user_id)
);

-- Schedules table (for DOS)
CREATE TABLE IF NOT EXISTS schedules (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    scheduled_date TIMESTAMP,
    departments JSONB,
    levels JSONB,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Announcements table (for DOS)
CREATE TABLE IF NOT EXISTS announcements (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    priority VARCHAR(20) DEFAULT 'normal',
    departments JSONB,
    levels JSONB,
    is_active BOOLEAN DEFAULT true,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default admin user
INSERT INTO users (username, password_hash, role, full_name, departments) VALUES 
('admin', '$2b$12$KjyaJYqUIwyP0CJTWKqO2u0zA3zKvIwfSs7m7Pb0iG8TpM7nFaQXy', 'admin', 'System Administrator', '["Software Development", "Computer System and Architecture", "Land Surveying", "Building Construction"]');

-- Insert sample students
INSERT INTO users (username, password_hash, role, full_name, department, level) VALUES 
('student001', '$2b$12$KjyaJYqUIwyP0CJTWKqO2u0zA3zKvIwfSs7m7Pb0iG8TpM7nFaQXy', 'student', 'Alice Johnson', 'Software Development', 'Level 3'),
('student002', '$2b$12$KjyaJYqUIwyP0CJTWKqO2u0zA3zKvIwfSs7m7Pb0iG8TpM7nFaQXy', 'student', 'Bob Smith', 'Computer System and Architecture', 'Level 4'),
('student003', '$2b$12$KjyaJYqUIwyP0CJTWKqO2u0zA3zKvIwfSs7m7Pb0iG8TpM7nFaQXy', 'student', 'Carol Davis', 'Computer System and Architecture', 'Level 5'),
('student004', '$2b$12$KjyaJYqUIwyP0CJTWKqO2u0zA3zKvIwfSs7m7Pb0iG8TpM7nFaQXy', 'student', 'David Wilson', 'Land Surveying', 'Level 3'),
('student005', '$2b$12$KjyaJYqUIwyP0CJTWKqO2u0zA3zKvIwfSs7m7Pb0iG8TpM7nFaQXy', 'student', 'Emma Brown', 'Building Construction', 'Level 4'),
('student006', '$2b$12$KjyaJYqUIwyP0CJTWKqO2u0zA3zKvIwfSs7m7Pb0iG8TpM7nFaQXy', 'student', 'Frank Miller', 'Software Development', 'Level 5'),
('student007', '$2b$12$KjyaJYqUIwyP0CJTWKqO2u0zA3zKvIwfSs7m7Pb0iG8TpM7nFaQXy', 'student', 'Grace Lee', 'Land Surveying', 'Level 5'),
('student008', '$2b$12$KjyaJYqUIwyP0CJTWKqO2u0zA3zKvIwfSs7m7Pb0iG8TpM7nFaQXy', 'student', 'Henry Taylor', 'Building Construction', 'Level 5');

-- Insert sample teachers
INSERT INTO users (username, password_hash, role, full_name, departments) VALUES 
('teacher001', '$2b$12$KjyaJYqUIwyP0CJTWKqO2u0zA3zKvIwfSs7m7Pb0iG8TpM7nFaQXy', 'teacher', 'Prof. Sarah Connor', '["Software Development", "Computer System and Architecture"]'),
('teacher002', '$2b$12$KjyaJYqUIwyP0CJTWKqO2u0zA3zKvIwfSs7m7Pb0iG8TpM7nFaQXy', 'teacher', 'Dr. John Mitchell', '["Land Surveying", "Building Construction"]'),
('teacher003', '$2b$12$KjyaJYqUIwyP0CJTWKqO2u0zA3zKvIwfSs7m7Pb0iG8TpM7nFaQXy', 'teacher', 'Ms. Lisa Anderson', '["Computer System and Architecture"]');

-- Insert sample lessons/modules
INSERT INTO lessons (title, code, description, department, level, classification, created_by) VALUES 
-- Software Development
('Programming Fundamentals', 'SD-L3-001', 'Basic programming concepts and syntax', 'Software Development', 'Level 3', 'Core', 1),
('Web Development Basics', 'SD-L3-002', 'HTML, CSS, and JavaScript fundamentals', 'Software Development', 'Level 3', 'Specific', 1),
('Communication Skills', 'SD-L3-003', 'Professional communication and teamwork', 'Software Development', 'Level 3', 'General', 1),
('Database Management', 'SD-L4-001', 'SQL and database design principles', 'Software Development', 'Level 4', 'Core', 1),
('Software Engineering', 'SD-L4-002', 'Design patterns and software architecture', 'Software Development', 'Level 4', 'Specific', 1),
('Project Management', 'SD-L4-003', 'Agile methodologies and project planning', 'Software Development', 'Level 4', 'General', 1),
('Advanced Programming', 'SD-L5-001', 'Advanced algorithms and data structures', 'Software Development', 'Level 5', 'Core', 1),
('DevOps and Deployment', 'SD-L5-002', 'CI/CD, containerization, and cloud deployment', 'Software Development', 'Level 5', 'Specific', 1),
('Entrepreneurship', 'SD-L5-003', 'Business development and startup fundamentals', 'Software Development', 'Level 5', 'General', 1),

-- Computer System and Architecture
('Computer Fundamentals', 'CSA-L3-001', 'Basic computer components and operations', 'Computer System and Architecture', 'Level 3', 'Core', 1),
('Digital Logic', 'CSA-L3-002', 'Boolean algebra and logic circuits', 'Computer System and Architecture', 'Level 3', 'Specific', 1),
('Mathematics for Computing', 'CSA-L3-003', 'Discrete mathematics and statistics', 'Computer System and Architecture', 'Level 3', 'General', 1),
('Processor Architecture', 'CSA-L4-001', 'CPU design and instruction sets', 'Computer System and Architecture', 'Level 4', 'Core', 1),
('Memory Systems', 'CSA-L4-002', 'Cache, RAM, and storage technologies', 'Computer System and Architecture', 'Level 4', 'Specific', 1),
('Technical Writing', 'CSA-L4-003', 'Documentation and technical communication', 'Computer System and Architecture', 'Level 4', 'General', 1),
('Parallel Computing', 'CSA-L5-001', 'Multi-core and distributed systems', 'Computer System and Architecture', 'Level 5', 'Core', 1),
('Advanced Architecture', 'CSA-L5-002', 'Superscalar and VLIW processors', 'Computer System and Architecture', 'Level 5', 'Specific', 1),
('Research Methodology', 'CSA-L5-003', 'Scientific research and analysis methods', 'Computer System and Architecture', 'Level 5', 'General', 1),

-- Land Surveying
('Surveying Fundamentals', 'LS-L3-001', 'Basic surveying principles and instruments', 'Land Surveying', 'Level 3', 'Core', 1),
('Field Measurements', 'LS-L3-002', 'Distance and angle measurement techniques', 'Land Surveying', 'Level 3', 'Specific', 1),
('Safety Procedures', 'LS-L3-003', 'Workplace safety and risk management', 'Land Surveying', 'Level 3', 'General', 1),
('Advanced Surveying', 'LS-L4-001', 'Total stations and electronic instruments', 'Land Surveying', 'Level 4', 'Core', 1),
('Photogrammetry', 'LS-L4-002', 'Aerial photography and mapping', 'Land Surveying', 'Level 4', 'Specific', 1),
('Environmental Awareness', 'LS-L4-003', 'Environmental impact and sustainability', 'Land Surveying', 'Level 4', 'General', 1),
('GIS and Remote Sensing', 'LS-L5-001', 'Geographic Information Systems', 'Land Surveying', 'Level 5', 'Core', 1),
('LiDAR Technology', 'LS-L5-002', 'Laser scanning and point cloud processing', 'Land Surveying', 'Level 5', 'Specific', 1),
('Legal Aspects', 'LS-L5-003', 'Land law and property rights', 'Land Surveying', 'Level 5', 'General', 1),

-- Building Construction
('Construction Basics', 'BC-L3-001', 'Materials and basic construction methods', 'Building Construction', 'Level 3', 'Core', 1),
('Concrete Technology', 'BC-L3-002', 'Concrete mixing and placement techniques', 'Building Construction', 'Level 3', 'Specific', 1),
('Health and Safety', 'BC-L3-003', 'Construction site safety protocols', 'Building Construction', 'Level 3', 'General', 1),
('Structural Systems', 'BC-L4-001', 'Load-bearing systems and structural design', 'Building Construction', 'Level 4', 'Core', 1),
('Steel Construction', 'BC-L4-002', 'Steel framing and welding techniques', 'Building Construction', 'Level 4', 'Specific', 1),
('Quality Control', 'BC-L4-003', 'Construction quality assurance methods', 'Building Construction', 'Level 4', 'General', 1),
('Advanced Construction', 'BC-L5-001', 'Modern construction technologies', 'Building Construction', 'Level 5', 'Core', 1),
('BIM and CAD', 'BC-L5-002', 'Building Information Modeling systems', 'Building Construction', 'Level 5', 'Specific', 1),
('Sustainable Construction', 'BC-L5-003', 'Green building and environmental practices', 'Building Construction', 'Level 5', 'General', 1);

-- Insert comprehensive sample questions
INSERT INTO questions (question_text, question_type, options, correct_answer, points, department, level, lesson_id, created_by) VALUES 
-- Software Development Level 3
('What is Object-Oriented Programming?', 'mcq', '["A programming paradigm", "A database", "A network protocol", "An operating system"]', 'A programming paradigm', 1, 'Software Development', 'Level 3', 1, 2),
('HTML stands for HyperText Markup Language.', 'true_false', '["True", "False"]', 'True', 1, 'Software Development', 'Level 3', 2, 2),
('Which of these is a programming language?', 'mcq', '["Python", "HTTP", "HTML", "CSS"]', 'Python', 1, 'Software Development', 'Level 3', 1, 2),
('What does CSS stand for?', 'short_answer', '[]', 'Cascading Style Sheets', 2, 'Software Development', 'Level 3', 2, 2),

-- Software Development Level 4
('What is a database?', 'mcq', '["A collection of organized data", "A programming language", "A web browser", "An operating system"]', 'A collection of organized data', 1, 'Software Development', 'Level 4', 4, 2),
('SQL is used for database management.', 'true_false', '["True", "False"]', 'True', 1, 'Software Development', 'Level 4', 4, 2),
('Which design pattern ensures only one instance of a class?', 'mcq', '["Singleton", "Factory", "Observer", "Strategy"]', 'Singleton', 2, 'Software Development', 'Level 4', 5, 2),

-- Software Development Level 5
('What is microservices architecture?', 'mcq', '["A way to structure applications as loosely coupled services", "A database design pattern", "A programming language", "A testing framework"]', 'A way to structure applications as loosely coupled services', 2, 'Software Development', 'Level 5', 7, 2),
('DevOps combines development and operations.', 'true_false', '["True", "False"]', 'True', 1, 'Software Development', 'Level 5', 8, 2),
('What is the main benefit of containerization?', 'short_answer', '[]', 'Portability and consistency across environments', 3, 'Software Development', 'Level 5', 8, 2),

-- Computer System and Architecture Level 3
('What is the main function of CPU?', 'mcq', '["Store data", "Process instructions", "Display graphics", "Connect to internet"]', 'Process instructions', 1, 'Computer System and Architecture', 'Level 3', 10, 2),
('RAM is volatile memory.', 'true_false', '["True", "False"]', 'True', 1, 'Computer System and Architecture', 'Level 3', 10, 2),
('What does GPU stand for?', 'short_answer', '[]', 'Graphics Processing Unit', 1, 'Computer System and Architecture', 'Level 3', 11, 2),

-- Computer System and Architecture Level 4
('What is cache memory?', 'mcq', '["High-speed memory close to CPU", "Long-term storage", "Network memory", "Virtual memory"]', 'High-speed memory close to CPU', 2, 'Computer System and Architecture', 'Level 4', 14, 2),
('RISC processors have complex instruction sets.', 'true_false', '["True", "False"]', 'False', 1, 'Computer System and Architecture', 'Level 4', 13, 2),
('What is pipelining in CPU design?', 'mcq', '["Executing multiple instructions simultaneously", "Storing data in pipes", "Connecting multiple CPUs", "Managing memory allocation"]', 'Executing multiple instructions simultaneously', 2, 'Computer System and Architecture', 'Level 4', 13, 2),

-- Computer System and Architecture Level 5
('What is parallel processing?', 'mcq', '["Executing multiple processes simultaneously", "Processing data in sequence", "Storing data in parallel", "Connecting processors in series"]', 'Executing multiple processes simultaneously', 2, 'Computer System and Architecture', 'Level 5', 16, 5),
('NUMA architecture provides uniform memory access.', 'true_false', '["True", "False"]', 'False', 2, 'Computer System and Architecture', 'Level 5', 16, 5),
('What is the purpose of branch prediction?', 'mcq', '["Improve pipeline efficiency", "Increase memory capacity", "Reduce power consumption", "Enhance graphics performance"]', 'Improve pipeline efficiency', 3, 'Computer System and Architecture', 'Level 5', 17, 5),
('Explain the concept of superscalar architecture.', 'short_answer', '[]', 'Multiple execution units to execute multiple instructions per clock cycle', 3, 'Computer System and Architecture', 'Level 5', 17, 5),
('What is cache coherence?', 'mcq', '["Maintaining consistency of shared data in multiple caches", "Organizing cache memory", "Increasing cache size", "Reducing cache access time"]', 'Maintaining consistency of shared data in multiple caches', 3, 'Computer System and Architecture', 'Level 5', 16, 5),

-- Land Surveying Level 3
('What tool is used for measuring angles in surveying?', 'mcq', '["Theodolite", "Hammer", "Ruler", "Calculator"]', 'Theodolite', 1, 'Land Surveying', 'Level 3', 19, 3),
('GPS stands for Global Positioning System.', 'true_false', '["True", "False"]', 'True', 1, 'Land Surveying', 'Level 3', 19, 3),
('What is triangulation?', 'short_answer', '[]', 'Method of determining location using triangles', 2, 'Land Surveying', 'Level 3', 20, 3),

-- Land Surveying Level 4
('What is photogrammetry?', 'mcq', '["Making measurements from photographs", "Taking aerial photos", "Measuring light intensity", "Creating photo albums"]', 'Making measurements from photographs', 2, 'Land Surveying', 'Level 4', 23, 3),
('Total stations combine theodolite and EDM functions.', 'true_false', '["True", "False"]', 'True', 1, 'Land Surveying', 'Level 4', 22, 3),

-- Land Surveying Level 5
('What is LiDAR technology?', 'mcq', '["Light Detection and Ranging", "Linear Data Recording", "Land Information Database", "Location Identification Radar"]', 'Light Detection and Ranging', 2, 'Land Surveying', 'Level 5', 26, 3),
('GIS stands for Geographic Information System.', 'true_false', '["True", "False"]', 'True', 1, 'Land Surveying', 'Level 5', 25, 3),
('Explain the principle of GNSS.', 'short_answer', '[]', 'Global Navigation Satellite System using satellite signals for positioning', 3, 'Land Surveying', 'Level 5', 25, 3),

-- Building Construction Level 3
('Concrete is stronger in compression than tension.', 'true_false', '["True", "False"]', 'True', 1, 'Building Construction', 'Level 3', 29, 3),
('What is the main component of concrete?', 'mcq', '["Cement", "Sand", "Water", "Gravel"]', 'Cement', 1, 'Building Construction', 'Level 3', 28, 3),
('What does rebar provide to concrete?', 'short_answer', '[]', 'Tensile strength', 2, 'Building Construction', 'Level 3', 29, 3),

-- Building Construction Level 4
('What is prestressed concrete?', 'mcq', '["Concrete with pre-applied compression", "Concrete under pressure", "Concrete with additives", "Concrete mixed under stress"]', 'Concrete with pre-applied compression', 2, 'Building Construction', 'Level 4', 31, 3),
('Steel has high tensile strength.', 'true_false', '["True", "False"]', 'True', 1, 'Building Construction', 'Level 4', 32, 3),

-- Building Construction Level 5
('What is BIM in construction?', 'mcq', '["Building Information Modeling", "Basic Installation Method", "Building Inspection Manual", "Blueprint Integration Model"]', 'Building Information Modeling', 2, 'Building Construction', 'Level 5', 35, 3),
('Sustainable construction focuses on environmental impact.', 'true_false', '["True", "False"]', 'True', 1, 'Building Construction', 'Level 5', 36, 3),
('Explain the concept of green building certification.', 'short_answer', '[]', 'Rating system for environmentally sustainable construction practices', 3, 'Building Construction', 'Level 5', 36, 3);

-- Create sample quizzes
INSERT INTO quizzes (title, description, scheduled_time, duration_minutes, is_active, department, level, created_by) VALUES 
('Software Development Quiz - Level 3', 'Morning quiz for Software Development Level 3 students', CURRENT_TIMESTAMP + INTERVAL '1 hour', 15, true, 'Software Development', 'Level 3', 2),
('Computer Architecture Quiz - Level 5', 'Advanced Computer System and Architecture quiz', CURRENT_TIMESTAMP + INTERVAL '2 hours', 30, true, 'Computer System and Architecture', 'Level 5', 5),
('Land Surveying Quiz - Level 4', 'Intermediate surveying concepts', CURRENT_TIMESTAMP + INTERVAL '3 hours', 20, false, 'Land Surveying', 'Level 4', 3),
('Building Construction Quiz - Level 5', 'Advanced construction techniques', CURRENT_TIMESTAMP + INTERVAL '4 hours', 25, false, 'Building Construction', 'Level 5', 3),
('Software Development Advanced - Level 5', 'Advanced programming concepts', CURRENT_TIMESTAMP + INTERVAL '5 hours', 35, false, 'Software Development', 'Level 5', 2);

-- Link questions to quizzes
-- Software Development Level 3 Quiz
INSERT INTO quiz_questions (quiz_id, question_id, question_order) VALUES 
(1, 1, 1), (1, 2, 2), (1, 3, 3), (1, 4, 4);

-- Computer Architecture Level 5 Quiz
INSERT INTO quiz_questions (quiz_id, question_id, question_order) VALUES 
(2, 17, 1), (2, 18, 2), (2, 19, 3), (2, 20, 4), (2, 21, 5);

-- Land Surveying Level 4 Quiz
INSERT INTO quiz_questions (quiz_id, question_id, question_order) VALUES 
(3, 24, 1), (3, 25, 2);

-- Building Construction Level 5 Quiz
INSERT INTO quiz_questions (quiz_id, question_id, question_order) VALUES 
(4, 31, 1), (4, 32, 2), (4, 33, 3);

-- Software Development Level 5 Quiz
INSERT INTO quiz_questions (quiz_id, question_id, question_order) VALUES 
(5, 8, 1), (5, 9, 2), (5, 10, 3);

-- Add sample quiz attempts for testing
INSERT INTO quiz_attempts (quiz_id, user_id, score, total_questions, answers, completed_at) VALUES 
(1, 2, 3, 4, '[{"question_id": 1, "answer": "A programming paradigm"}, {"question_id": 2, "answer": "True"}, {"question_id": 3, "answer": "Python"}, {"question_id": 4, "answer": "Cascading Style Sheets"}]', CURRENT_TIMESTAMP - INTERVAL '1 day'),
(1, 7, 4, 4, '[{"question_id": 1, "answer": "A programming paradigm"}, {"question_id": 2, "answer": "True"}, {"question_id": 3, "answer": "Python"}, {"question_id": 4, "answer": "Cascading Style Sheets"}]', CURRENT_TIMESTAMP - INTERVAL '1 day'),
(2, 4, 4, 5, '[{"question_id": 17, "answer": "Executing multiple processes simultaneously"}, {"question_id": 18, "answer": "False"}, {"question_id": 19, "answer": "Improve pipeline efficiency"}, {"question_id": 20, "answer": "Multiple execution units to execute multiple instructions per clock cycle"}, {"question_id": 21, "answer": "Maintaining consistency of shared data in multiple caches"}]', CURRENT_TIMESTAMP - INTERVAL '2 hours');

-- Add sample schedules
INSERT INTO schedules (title, description, scheduled_date, departments, levels, created_by) VALUES 
('Morning Quiz Schedule', 'Daily morning quiz for all departments', CURRENT_TIMESTAMP + INTERVAL '1 day', '["Software Development", "Computer System and Architecture", "Land Surveying", "Building Construction"]', '["Level 3", "Level 4", "Level 5"]', 1),
('Midterm Examinations', 'Midterm exam schedule for all levels', CURRENT_TIMESTAMP + INTERVAL '1 week', '["Software Development", "Computer System and Architecture"]', '["Level 4", "Level 5"]', 1);

-- Add sample announcements
INSERT INTO announcements (title, content, priority, departments, levels, created_by) VALUES 
('System Maintenance Notice', 'The quiz system will undergo maintenance this weekend. Please complete any pending quizzes before Friday.', 'high', '["Software Development", "Computer System and Architecture", "Land Surveying", "Building Construction"]', '["Level 3", "Level 4", "Level 5"]', 1),
('New Quiz Format', 'Starting next week, quizzes will include more practical questions. Please prepare accordingly.', 'normal', '["Software Development", "Computer System and Architecture"]', '["Level 4", "Level 5"]', 1),
('Emergency Drill', 'Fire drill scheduled for tomorrow at 10 AM. All classes will be suspended temporarily.', 'urgent', '["Software Development", "Computer System and Architecture", "Land Surveying", "Building Construction"]', '["Level 3", "Level 4", "Level 5"]', 1);