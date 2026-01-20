-- Additional sample questions for testing
-- Run this in the database to add more questions

INSERT INTO questions (question_text, question_type, options, correct_answer, points, created_by) VALUES 
-- Math Questions
('What is 15 + 27?', 'mcq', '["40", "41", "42", "43"]', '42', 1, 1),
('What is 8 × 7?', 'mcq', '["54", "55", "56", "57"]', '56', 1, 1),
('Is 17 a prime number?', 'true_false', '["True", "False"]', 'True', 1, 1),

-- Science Questions
('What is the chemical symbol for water?', 'short_answer', '[]', 'H2O', 2, 1),
('How many planets are in our solar system?', 'mcq', '["7", "8", "9", "10"]', '8', 1, 1),
('The sun is a star.', 'true_false', '["True", "False"]', 'True', 1, 1),

-- Geography Questions
('What is the capital of Japan?', 'mcq', '["Tokyo", "Osaka", "Kyoto", "Hiroshima"]', 'Tokyo', 1, 1),
('Which is the largest ocean?', 'mcq', '["Atlantic", "Indian", "Arctic", "Pacific"]', 'Pacific', 1, 1),
('What is the longest river in the world?', 'short_answer', '[]', 'Nile', 2, 1),

-- History Questions
('In which year did World War II end?', 'mcq', '["1944", "1945", "1946", "1947"]', '1945', 1, 1),
('The Great Wall of China was built to keep out invaders.', 'true_false', '["True", "False"]', 'True', 1, 1),

-- English Questions
('What is the plural of "child"?', 'mcq', '["childs", "children", "childes", "child"]', 'children', 1, 1),
('A group of lions is called a pride.', 'true_false', '["True", "False"]', 'True', 1, 1),
('What does the word "bibliography" mean?', 'short_answer', '[]', 'list of books', 2, 1),

-- General Knowledge
('How many days are there in a leap year?', 'mcq', '["365", "366", "367", "364"]', '366', 1, 1),
('The human body has 206 bones.', 'true_false', '["True", "False"]', 'True', 1, 1);

-- Create a sample quiz with these questions
INSERT INTO quizzes (title, description, scheduled_time, duration_minutes, is_active, created_by) VALUES 
('Morning Quiz - Sample Set', 'A comprehensive quiz covering multiple subjects', CURRENT_TIMESTAMP + INTERVAL '30 minutes', 20, false, 1);

-- Link questions to the new quiz (assuming quiz_id = 2)
INSERT INTO quiz_questions (quiz_id, question_id, question_order) 
SELECT 2, id, ROW_NUMBER() OVER (ORDER BY id) 
FROM questions 
WHERE id > 5 
LIMIT 10;