#!/usr/bin/env python3
"""
Create Advanced Question Types for TVET Quiz System
Generates all 12 question types with proper configurations
"""

import requests
import json
import sys

# API Configuration
API_BASE = "http://localhost:8000"
USERNAME = "teacher001"
PASSWORD = "teacher123"

def login():
    """Login and get token"""
    response = requests.post(f"{API_BASE}/auth/login", json={
        "username": USERNAME,
        "password": PASSWORD
    })
    if response.status_code == 200:
        data = response.json()
        return data["access_token"]
    else:
        print(f"Login failed: {response.text}")
        return None

def create_question(token, question_data):
    """Create a question"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_BASE}/questions", json=question_data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to create question: {response.text}")
        return None

def main():
    print("🚀 Creating Advanced Question Types...")
    
    # Login
    token = login()
    if not token:
        print("❌ Login failed")
        return
    
    print("✅ Login successful")
    
    # Question definitions with proper configurations
    questions = [
        # 1. Multiple Choice
        {
            "question_text": "What is the primary purpose of Python's 'self' parameter in class methods?",
            "question_type": "multiple_choice",
            "options": [
                "To reference the current instance of the class",
                "To create a new instance of the class", 
                "To access global variables",
                "To define static methods"
            ],
            "correct_answer": "To reference the current instance of the class",
            "points": 1,
            "department": "Software Development",
            "level": "Level 5"
        },
        
        # 2. True/False
        {
            "question_text": "In Python, a list is mutable while a tuple is immutable.",
            "question_type": "true_false",
            "options": ["True", "False"],
            "correct_answer": "True",
            "points": 1,
            "department": "Software Development", 
            "level": "Level 5"
        },
        
        # 3. Short Answer
        {
            "question_text": "What does HTML stand for?",
            "question_type": "short_answer",
            "correct_answer": "HyperText Markup Language",
            "points": 1,
            "department": "Software Development",
            "level": "Level 5"
        },
        
        # 4. Essay
        {
            "question_text": "Explain the importance of version control systems in software development. Discuss at least three benefits and provide examples.",
            "question_type": "essay",
            "correct_answer": "Version control systems are essential for tracking changes, collaboration, backup, branching, and maintaining code history. Examples include Git, SVN, and Mercurial.",
            "points": 5,
            "department": "Software Development",
            "level": "Level 5"
        },
        
        # 5. Multiple Select
        {
            "question_text": "Which of the following are valid Python data types? (Select all that apply)",
            "question_type": "multiple_select",
            "options": ["int", "string", "list", "dictionary", "boolean"],
            "correct_answers": ["int", "list", "dictionary"],
            "correct_answer": "int,list,dictionary",
            "partial_credit": True,
            "points": 3,
            "department": "Software Development",
            "level": "Level 5"
        },
        
        # 6. Dropdown Select
        {
            "question_text": "Which HTTP method is used to retrieve data from a server?",
            "question_type": "dropdown_select",
            "options": ["GET", "POST", "PUT", "DELETE", "PATCH"],
            "correct_answer": "GET",
            "points": 1,
            "department": "Software Development",
            "level": "Level 5"
        },
        
        # 7. Fill in the Blanks
        {
            "question_text": "Complete the sentence: Python is a _____ programming language, and it uses _____ for code blocks instead of curly braces.",
            "question_type": "fill_blanks",
            "correct_answer": "high-level|||indentation",
            "question_config": {
                "blanks": [
                    {"answer": "high-level"},
                    {"answer": "indentation"}
                ]
            },
            "points": 2,
            "department": "Software Development",
            "level": "Level 5"
        },
        
        # 8. Matching Pairs
        {
            "question_text": "Match each programming language with its primary use case:",
            "question_type": "drag_drop_match",
            "correct_answer": "Python|||JavaScript|||SQL",
            "question_config": {
                "pairs": [
                    {"left": "Python", "right": "Data Science & AI"},
                    {"left": "JavaScript", "right": "Web Development"},
                    {"left": "SQL", "right": "Database Management"}
                ]
            },
            "points": 3,
            "department": "Software Development",
            "level": "Level 5"
        },
        
        # 9. Drag & Drop Ordering
        {
            "question_text": "Arrange the software development lifecycle phases in the correct order:",
            "question_type": "drag_drop_order",
            "correct_answer": "0,1,2,3,4",
            "question_config": {
                "items": [
                    "Requirements Analysis",
                    "Design",
                    "Implementation",
                    "Testing", 
                    "Deployment"
                ],
                "correct_order": [0, 1, 2, 3, 4]
            },
            "points": 3,
            "department": "Software Development",
            "level": "Level 5"
        },
        
        # 10. Linear Scale
        {
            "question_text": "On a scale of 1-10, how important is code documentation in software development?",
            "question_type": "linear_scale",
            "correct_answer": "8",
            "question_config": {
                "min_value": 1,
                "max_value": 10,
                "min_label": "Not Important",
                "max_label": "Very Important"
            },
            "points": 1,
            "department": "Software Development",
            "level": "Level 5"
        },
        
        # 11. Code Writing
        {
            "question_text": "Write a Python function that takes a list of numbers and returns the sum of all even numbers in the list.",
            "question_type": "code_writing",
            "correct_answer": "def sum_even_numbers(numbers):\n    return sum(num for num in numbers if num % 2 == 0)",
            "question_config": {
                "language": "python",
                "starter_code": "def sum_even_numbers(numbers):\n    # Write your code here\n    pass"
            },
            "points": 5,
            "department": "Software Development",
            "level": "Level 5"
        },
        
        # 12. SQL Query
        {
            "question_text": "Write a SQL query to select all students from the 'students' table where the grade is greater than 80, ordered by grade in descending order.",
            "question_type": "sql_query",
            "correct_answer": "SELECT * FROM students WHERE grade > 80 ORDER BY grade DESC;",
            "question_config": {
                "database_schema": "CREATE TABLE students (id INT, name VARCHAR(50), grade INT);"
            },
            "points": 3,
            "department": "Software Development",
            "level": "Level 5"
        },
        
        # 13. Multi-Grid (Bonus)
        {
            "question_text": "Rate each aspect of software development on the given scale:",
            "question_type": "multi_grid",
            "correct_answer": '{"Planning": "Very Important", "Coding": "Very Important", "Testing": "Important"}',
            "question_config": {
                "rows": ["Planning", "Coding", "Testing"],
                "columns": ["Not Important", "Important", "Very Important"],
                "correct_answers": {
                    "Planning": "Very Important",
                    "Coding": "Very Important", 
                    "Testing": "Important"
                }
            },
            "points": 3,
            "department": "Software Development",
            "level": "Level 5"
        }
    ]
    
    created_count = 0
    for i, question in enumerate(questions, 1):
        print(f"Creating question {i}/13: {question['question_type']}")
        result = create_question(token, question)
        if result:
            created_count += 1
            print(f"✅ Created: {question['question_text'][:50]}...")
        else:
            print(f"❌ Failed: {question['question_text'][:50]}...")
    
    print(f"\n🎉 Successfully created {created_count}/13 advanced questions!")
    print("\n📋 Question Types Created:")
    print("1. ✅ Multiple Choice")
    print("2. ✅ True/False") 
    print("3. ✅ Short Answer")
    print("4. ✅ Essay")
    print("5. ✅ Multiple Select")
    print("6. ✅ Dropdown Select")
    print("7. ✅ Fill in the Blanks")
    print("8. ✅ Matching Pairs")
    print("9. ✅ Drag & Drop Ordering")
    print("10. ✅ Linear Scale")
    print("11. ✅ Code Writing")
    print("12. ✅ SQL Query")
    print("13. ✅ Multi-Grid")
    
    print("\n🚀 Ready for testing! Login as teacher001 to create a quiz with these questions.")

if __name__ == "__main__":
    main()