# 📚 Blockchain Questions Upload Guide

## Overview
This guide will help you upload the 50 Blockchain Fundamentals questions into your TVET Quiz System.

## What's Been Created

### 1. **Text Question Parser** (`backend/text_question_parser.py`)
- Parses questions from `.txt` files
- Supports the format used in `Blockchain_Fundamentals_50_Questions.txt`
- Automatically extracts:
  - Question text
  - Multiple choice options (A, B, C, D)
  - Correct answers
  - Metadata (department, level)

### 2. **Upload Endpoint** (`backend/text_question_endpoint.py`)
- FastAPI endpoint for uploading text files
- Validates teacher permissions
- Saves questions to database
- Returns success/error messages

### 3. **Web Interface** (`upload_blockchain_questions.html`)
- User-friendly HTML interface
- Department and level selection
- Lesson/course selection
- File upload with drag-and-drop
- Real-time feedback

## Quick Start (3 Steps)

### Step 1: Add the Endpoint to Backend

Open `backend/main.py` and add this import at the top:

```python
from text_question_parser import parse_text_file
```

Then add this endpoint anywhere in the file (after the `get_current_user` function):

```python
@app.post("/questions/upload-text")
async def upload_text_questions(
    file: UploadFile = File(...),
    department: str = Form(...),
    level: str = Form(...),
    lesson_id: int = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload questions from .txt file"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Teacher access required")
    
    if not file.filename.endswith('.txt'):
        raise HTTPException(status_code=400, detail="❌ Only .txt files are supported")
    
    # Validate lesson assignment
    if current_user.role == "teacher":
        assignment = db.query(TeacherLesson).filter(
            TeacherLesson.teacher_id == current_user.id,
            TeacherLesson.lesson_id == lesson_id
        ).first()
        if not assignment:
            raise HTTPException(status_code=403, detail="You can only upload questions for lessons assigned to you")
    
    # Validate lesson exists
    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id,
        Lesson.department == department,
        Lesson.level == level,
        Lesson.is_active == True
    ).first()
    if not lesson:
        raise HTTPException(status_code=400, detail=f"Invalid lesson for {department} - {level}")
    
    try:
        content = await file.read()
        result = parse_text_file(content, department, level)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['message'])
        
        created_count = 0
        errors = []
        
        for q_data in result['questions']:
            try:
                db_question = Question(
                    question_text=q_data['question_text'],
                    question_type=q_data['question_type'],
                    options=q_data['options'],
                    correct_answer=q_data['correct_answer'],
                    points=q_data['points'],
                    department=department,
                    level=level,
                    lesson_id=lesson_id,
                    created_by=current_user.id
                )
                db.add(db_question)
                created_count += 1
            except Exception as e:
                errors.append(f"Error: {str(e)}")
        
        db.commit()
        
        return {
            'success': True,
            'message': f'✅ Successfully imported {created_count} questions from {file.filename}',
            'total': created_count,
            'errors': errors if errors else []
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"❌ Failed to process file: {str(e)}")
```

### Step 2: Restart the Backend

```bash
docker-compose restart backend
```

Or if running without Docker:
```bash
cd backend
python main.py
```

### Step 3: Upload the Questions

1. **Open the upload interface:**
   - Open `upload_blockchain_questions.html` in your web browser
   - Or navigate to `http://localhost:3000/upload_blockchain_questions.html`

2. **Login as Teacher:**
   - You'll need your teacher access token
   - Get it by logging in at `http://localhost:3000/teacher`

3. **Fill the form:**
   - **Department:** Select "Software Development" or "Information Technology"
   - **Level:** Select "Level 5" (or appropriate level)
   - **Lesson:** Select "Blockchain Fundamentals" (create this lesson first if it doesn't exist)
   - **File:** Select `Blockchain_Fundamentals_50_Questions.txt`

4. **Click "Upload Questions"**
   - Wait for processing
   - You should see: "✅ Successfully imported 50 questions"

## Creating the Blockchain Lesson (If Needed)

If the "Blockchain Fundamentals" lesson doesn't exist:

1. Login as **DOS/Admin** at `http://localhost:3000/admin`
2. Go to **Lessons Management**
3. Click **"Create New Lesson"**
4. Fill in:
   - **Title:** Blockchain Fundamentals
   - **Code:** BCFND301 (or appropriate code)
   - **Department:** Software Development
   - **Level:** Level 5
   - **Classification:** Core/Specific
5. Click **"Create Lesson"**
6. **Assign to Teacher:**
   - Go to Teacher Management
   - Find your teacher account
   - Assign the "Blockchain Fundamentals" lesson

## Verification

After upload, verify the questions:

1. Login as teacher
2. Go to **Questions** section
3. Filter by:
   - Department: Software Development
   - Level: Level 5
   - Lesson: Blockchain Fundamentals
4. You should see all 50 questions

## Creating a Quiz with Blockchain Questions

1. Login as teacher
2. Go to **Create Quiz**
3. Fill in quiz details:
   - **Title:** Blockchain Fundamentals Quiz
   - **Department:** Software Development
   - **Level:** Level 5
   - **Duration:** 60 minutes
   - **Time per question:** 60 seconds
4. **Select Questions:**
   - Filter by lesson: Blockchain Fundamentals
   - Select all 50 questions (or subset)
5. Click **"Create Quiz"**
6. **Broadcast to Students** when ready

## Troubleshooting

### Error: "Teacher access required"
- Make sure you're logged in as a teacher
- Check your access token is valid

### Error: "Invalid lesson for [department] - [level]"
- Create the lesson first (see above)
- Make sure department and level match exactly

### Error: "You can only upload questions for lessons assigned to you"
- Ask DOS/Admin to assign the Blockchain lesson to you
- Or login as admin to upload

### Error: "No valid questions found in file"
- Check the file format matches the expected format
- Ensure questions are numbered (1., 2., 3., etc.)
- Ensure options are labeled (A), B), C), D))
- Ensure answers are marked (Answer: B)

### Questions not appearing
- Check database: `docker exec -it morning_quiz_backend sqlite3 quiz.db "SELECT COUNT(*) FROM questions WHERE lesson_id = [lesson_id];"`
- Verify lesson assignment
- Check teacher permissions

## File Format Reference

The parser expects this format:

```
1. What is a blockchain?
A) A type of database
B) A distributed ledger technology
C) A programming language
D) A web browser
Answer: B

2. Who created Bitcoin?
A) Vitalik Buterin
B) Satoshi Nakamoto
C) Bill Gates
D) Mark Zuckerberg
Answer: B
```

**Key Points:**
- Questions numbered: `1.`, `2.`, `3.`, etc.
- Options labeled: `A)`, `B)`, `C)`, `D)`
- Answer format: `Answer: B` (letter only)
- Blank line between questions (optional)

## Alternative: Manual Upload via Teacher Panel

If the automated upload doesn't work, you can manually add questions:

1. Login as teacher
2. Go to **Questions** → **Add Question**
3. For each question:
   - Type: Multiple Choice
   - Question text: Copy from file
   - Options: Copy A, B, C, D
   - Correct answer: Select the correct option
   - Points: 1
   - Department: Software Development
   - Level: Level 5
   - Lesson: Blockchain Fundamentals
4. Click **"Save Question"**
5. Repeat for all 50 questions

## Support

If you encounter issues:

1. Check backend logs: `docker-compose logs backend`
2. Check browser console for errors (F12)
3. Verify file format matches expected format
4. Ensure all prerequisites are met (lesson created, teacher assigned)

## Summary

✅ **Created:**
- Text question parser
- Upload endpoint
- Web interface
- Integration guide

✅ **Next Steps:**
1. Add endpoint to `main.py`
2. Restart backend
3. Open upload interface
4. Upload `Blockchain_Fundamentals_50_Questions.txt`
5. Create quiz with imported questions
6. Broadcast to students

🎉 **You're all set to import and use the 50 Blockchain Fundamentals questions!**
