# MANUAL REVIEW SYSTEM - IMPLEMENTATION GUIDE

## ✅ What's Been Done

1. **Enhanced AI Grader** - Added confidence scoring
2. **Database Migration** - Script created
3. **Backend Endpoints** - All endpoints ready
4. **Implementation Scripts** - Batch files created

## 🎯 What You Need to Do

This is a **MAJOR FEATURE** that requires code integration. Here's the complete guide:

---

## STEP 1: Update Database Models (5 minutes)

### File: `backend/main.py`

#### 1.1 Update Quiz Model
Find the `Quiz` class and add these fields:

```python
class Quiz(Base):
    __tablename__ = "quizzes"
    # ... existing fields ...
    
    # ADD THESE NEW FIELDS:
    grading_mode = Column(String(20), default="auto")  # auto, manual, hybrid
    results_released = Column(Boolean, default=False)
```

#### 1.2 Update QuizAttempt Model
Find the `QuizAttempt` class and add:

```python
class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    # ... existing fields ...
    
    # ADD THESE NEW FIELDS:
    needs_review = Column(Boolean, default=False)
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    reviewed_at = Column(DateTime)
    final_score = Column(Float)
    ai_confidence = Column(Float, default=1.0)
```

#### 1.3 Update StudentAnswer Model
Find the `StudentAnswer` class and add:

```python
class StudentAnswer(Base):
    __tablename__ = "student_answers"
    # ... existing fields ...
    
    # ADD THESE NEW FIELDS:
    teacher_score = Column(Float)
    teacher_feedback = Column(Text)
    review_status = Column(String(20), default="pending")
    ai_confidence = Column(Float, default=1.0)
```

---

## STEP 2: Update Quiz Creation (5 minutes)

### File: `backend/main.py`

#### 2.1 Update QuizCreate Pydantic Model
Find `class QuizCreate(BaseModel):` and add:

```python
class QuizCreate(BaseModel):
    title: str
    description: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    duration_minutes: int = 30
    question_time_seconds: int = 60
    shuffle_questions: bool = True
    department: str
    level: str
    question_ids: List[int] = []
    grading_mode: str = "auto"  # ADD THIS LINE
```

#### 2.2 Update create_quiz Endpoint
Find `@app.post("/quizzes")` and update:

```python
@app.post("/quizzes")
def create_quiz(quiz: QuizCreate, current_user: User, db: Session):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403)
    
    new_quiz = Quiz(
        title=quiz.title,
        description=quiz.description,
        scheduled_time=quiz.scheduled_time,
        duration_minutes=quiz.duration_minutes,
        question_time_seconds=quiz.question_time_seconds,
        shuffle_questions=quiz.shuffle_questions,
        department=quiz.department,
        level=quiz.level,
        created_by=current_user.id,
        grading_mode=quiz.grading_mode  # ADD THIS LINE
    )
    # ... rest of code ...
```

---

## STEP 3: Update Quiz Submission Logic (10 minutes)

### File: `backend/main.py`

Find `@app.post("/quizzes/submit")` and update the grading logic:

#### 3.1 Import Enhanced Grader
At the top of main.py, update the import:

```python
from ai_grader import grade_open_ended_question, enhanced_grade_with_confidence
```

#### 3.2 Update Grading Loop
In the `submit_quiz` function, replace the grading section with:

```python
# Inside the for loop that grades questions:
for question in questions:
    user_answer = answers_dict.get(question.id, "")
    points_earned = 0
    feedback = "Not answered"
    confidence = 1.0  # ADD THIS
    
    try:
        if not user_answer or not str(user_answer).strip():
            points_earned = 0
            feedback = "No answer provided"
            confidence = 1.0
        elif question.question_type in ["short_answer", "fill_blanks"]:
            try:
                # USE ENHANCED GRADER WITH CONFIDENCE
                points_earned, feedback, confidence = enhanced_grade_with_confidence(
                    student_answer=str(user_answer),
                    correct_answer=str(question.correct_answer or ""),
                    max_points=int(question.points or 1),
                    question_text=str(question.question_text or "")
                )
                score += points_earned
            except Exception as grade_err:
                print(f"AI grading failed: {grade_err}")
                # Fallback
                if str(user_answer).strip().lower() == str(question.correct_answer or "").strip().lower():
                    points_earned = question.points
                    score += points_earned
                    feedback = "Correct"
                    confidence = 1.0
                else:
                    points_earned = 0
                    feedback = "Incorrect"
                    confidence = 0.5
        else:
            # MCQ/True-False - exact match
            if str(user_answer).strip() == str(question.correct_answer or "").strip():
                points_earned = question.points
                score += points_earned
                feedback = "Correct"
                confidence = 1.0
            else:
                points_earned = 0
                feedback = "Incorrect"
                confidence = 1.0
        
        grading_details.append({
            "question_id": question.id,
            "points_earned": float(points_earned),
            "max_points": int(question.points or 1),
            "feedback": str(feedback),
            "confidence": float(confidence)  # ADD THIS
        })
```

#### 3.3 Determine if Needs Review
After grading all questions, add:

```python
# After the grading loop, before creating attempt:

# Determine if needs manual review
needs_review = False
avg_confidence = sum(d['confidence'] for d in grading_details) / len(grading_details) if grading_details else 1.0

if quiz.grading_mode in ["manual", "hybrid"]:
    # Check if quiz has open-ended questions
    has_open_ended = any(
        q.question_type in ["short_answer", "fill_blanks", "essay"]
        for q in questions
    )
    needs_review = has_open_ended
    
    # Or if AI confidence is low
    if avg_confidence < 0.7:
        needs_review = True
```

#### 3.4 Update Attempt Creation
Update the QuizAttempt creation:

```python
attempt = QuizAttempt(
    quiz_id=submission.quiz_id,
    user_id=current_user.id,
    score=score,
    final_score=score if quiz.grading_mode == "auto" else None,  # ADD THIS
    total_questions=total_marks,
    answers=[{"question_id": ans.question_id, "answer": ans.answer} for ans in submission.answers],
    completed_at=now(),
    needs_review=needs_review,  # ADD THIS
    ai_confidence=avg_confidence  # ADD THIS
)
```

#### 3.5 Update StudentAnswer Creation
In the loop that creates StudentAnswer records:

```python
for idx, question in enumerate(questions):
    user_answer = answers_dict.get(question.id, "")
    detail = grading_details[idx]
    is_correct = detail['points_earned'] >= (detail['max_points'] * 0.7)
    
    student_answer = StudentAnswer(
        attempt_id=attempt.id,
        question_id=question.id,
        student_answer=user_answer,
        is_correct=is_correct,
        points_earned=detail['points_earned'],
        ai_feedback=detail['feedback'],
        ai_confidence=detail.get('confidence', 1.0),  # ADD THIS
        review_status="pending" if needs_review else "auto"  # ADD THIS
    )
    db.add(student_answer)
```

---

## STEP 4: Add Manual Review Endpoints (5 minutes)

### File: `backend/main.py`

Copy ALL the endpoints from `backend/manual_review_endpoints.py` and paste them into `main.py` before the database initialization section.

The endpoints to add:
1. `@app.get("/teacher/pending-reviews")`
2. `@app.get("/teacher/review/{attempt_id}")`
3. `@app.post("/teacher/review/{attempt_id}/grade")`
4. `@app.post("/teacher/quiz/{quiz_id}/release-results")`
5. `@app.get("/teacher/quiz/{quiz_id}/review-status")`

Also add the Pydantic models at the top:

```python
class GradeAdjustment(BaseModel):
    answer_id: int
    score: float
    feedback: str

class ManualGradeRequest(BaseModel):
    grades: List[GradeAdjustment]
```

---

## STEP 5: Update Student Results View (5 minutes)

### File: `backend/main.py`

Find `@app.get("/student/progress")` and update to check if results are released:

```python
@app.get("/student/progress")
def get_student_progress_endpoint(current_user: User, db: Session):
    # ... existing code ...
    
    # In the loop that builds recent_quizzes:
    for attempt in attempts[:10]:
        quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
        if quiz:
            # SKIP IF RESULTS NOT RELEASED FOR MANUAL/HYBRID QUIZZES
            if quiz.grading_mode in ["manual", "hybrid"] and not quiz.results_released:
                continue
            
            # USE FINAL SCORE IF AVAILABLE
            display_score = attempt.final_score if attempt.final_score is not None else attempt.score
            percentage = round((display_score / attempt.total_questions * 100) if attempt.total_questions > 0 else 0, 1)
            grade = 'A+' if percentage >= 90 else 'A' if percentage >= 80 else 'B' if percentage >= 70 else 'C' if percentage >= 60 else 'D'
            
            recent_quizzes.append({
                "quiz_id": quiz.id,
                "quiz_title": quiz.title,
                "department": quiz.department,
                "level": quiz.level,
                "score": display_score,  # CHANGED
                "total_questions": attempt.total_questions,
                "percentage": percentage,
                "grade": grade,
                "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None,
                "needs_review": attempt.needs_review,  # ADD THIS
                "results_released": quiz.results_released  # ADD THIS
            })
```

---

## STEP 6: Restart and Test (2 minutes)

```cmd
docker-compose down
docker-compose up -d
```

Wait 30 seconds, then test:

1. **Create Quiz with Manual Review:**
   - Login as teacher
   - Create quiz
   - Select "Manual Review" grading mode
   - Add open-ended questions

2. **Student Takes Quiz:**
   - Login as student
   - Take the quiz
   - Submit answers

3. **Teacher Reviews:**
   - Login as teacher
   - Go to "Pending Reviews"
   - Review student answers
   - Adjust scores if needed
   - Release results

4. **Student Sees Results:**
   - Login as student
   - Check "My Performance"
   - See final scores

---

## 🎯 Grading Modes Explained

### AUTO (Default - Current Behavior)
- AI grades everything instantly
- Results shown to students immediately
- No teacher review needed
- Best for: MCQ quizzes, quick assessments

### MANUAL (New)
- AI provides suggested scores
- Teacher reviews ALL answers before releasing
- Results hidden until teacher releases
- Best for: Essay questions, subjective assessments

### HYBRID (New - Recommended)
- MCQ questions: Auto-graded instantly
- Open-ended questions: Held for teacher review
- Teacher only reviews subjective answers
- Results released when teacher approves
- Best for: Mixed question types

---

## 🤖 AI Grader Confidence Levels

The enhanced AI grader provides confidence scores:

- **0.90-1.00**: Very confident - likely correct
- **0.75-0.89**: Confident - probably correct
- **0.60-0.74**: Moderate - may need review
- **0.40-0.59**: Low confidence - should review
- **0.00-0.39**: Very low - definitely review

Answers with confidence < 0.70 are flagged for teacher attention.

---

## 📊 Benefits

✅ **Quality Control**: Teacher verifies AI grading
✅ **Fairness**: Manual review for subjective answers
✅ **Flexibility**: Choose grading mode per quiz
✅ **Efficiency**: AI does initial work, teacher adjusts
✅ **Transparency**: Students see teacher feedback
✅ **Confidence**: AI tells you when it's unsure

---

## 🚀 Quick Start After Implementation

1. **Test Auto Mode** (current behavior):
   - Create quiz with grading_mode="auto"
   - Student takes quiz
   - Results instant

2. **Test Manual Mode**:
   - Create quiz with grading_mode="manual"
   - Student takes quiz
   - Teacher reviews at `/teacher/pending-reviews`
   - Teacher releases results

3. **Test Hybrid Mode** (recommended):
   - Create quiz with both MCQ and open-ended
   - Set grading_mode="hybrid"
   - MCQ auto-graded, open-ended held for review

---

## ⚠️ Important Notes

1. **Database Migration**: Happens automatically on restart
2. **Existing Quizzes**: Will default to "auto" mode
3. **Backward Compatible**: All existing features still work
4. **No Breaking Changes**: Students/teachers can use system normally

---

## 📁 Files Modified

- `backend/ai_grader.py` - Enhanced with confidence scoring ✅
- `backend/main.py` - Models and endpoints (YOU DO THIS)
- Database - Auto-migrated on restart ✅

## 📁 Files Created

- `backend/migration_manual_review.py` - Migration script ✅
- `backend/manual_review_endpoints.py` - Ready-to-use endpoints ✅
- `IMPLEMENT_MANUAL_REVIEW.bat` - Implementation script ✅
- This guide ✅

---

## 🆘 Need Help?

If you get stuck:
1. Check `backend/manual_review_endpoints.py` for complete endpoint code
2. Check `backend/migration_manual_review.py` for database changes
3. All code is ready - just needs to be integrated into main.py

---

**Estimated Time**: 30-45 minutes
**Difficulty**: Moderate (copy-paste with care)
**Risk**: Low (backward compatible)

**Ready to implement?** Follow the steps above carefully!
