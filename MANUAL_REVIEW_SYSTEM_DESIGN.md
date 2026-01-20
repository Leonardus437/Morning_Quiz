# MANUAL REVIEW SYSTEM FOR OPEN-ENDED QUESTIONS

## Overview
This system allows teachers to manually review and grade open-ended questions before releasing final results to students.

## Database Changes Needed

Add these columns to existing tables:

### Quiz Table
```sql
ALTER TABLE quizzes ADD COLUMN grading_mode VARCHAR(20) DEFAULT 'auto';
-- Values: 'auto', 'manual', 'hybrid'

ALTER TABLE quizzes ADD COLUMN results_released BOOLEAN DEFAULT FALSE;
```

### QuizAttempt Table
```sql
ALTER TABLE quiz_attempts ADD COLUMN needs_review BOOLEAN DEFAULT FALSE;
ALTER TABLE quiz_attempts ADD COLUMN reviewed_by INTEGER;
ALTER TABLE quiz_attempts ADD COLUMN reviewed_at DATETIME;
ALTER TABLE quiz_attempts ADD COLUMN final_score FLOAT;
```

### StudentAnswer Table
```sql
ALTER TABLE student_answers ADD COLUMN teacher_score FLOAT;
ALTER TABLE student_answers ADD COLUMN teacher_feedback TEXT;
ALTER TABLE student_answers ADD COLUMN review_status VARCHAR(20) DEFAULT 'pending';
-- Values: 'pending', 'approved', 'adjusted'
```

## Implementation Steps

### Step 1: Update Database Models (backend/main.py)

Add to Quiz model:
```python
grading_mode = Column(String(20), default="auto")  # auto, manual, hybrid
results_released = Column(Boolean, default=False)
```

Add to QuizAttempt model:
```python
needs_review = Column(Boolean, default=False)
reviewed_by = Column(Integer, ForeignKey("users.id"))
reviewed_at = Column(DateTime)
final_score = Column(Float)
```

Add to StudentAnswer model:
```python
teacher_score = Column(Float)
teacher_feedback = Column(Text)
review_status = Column(String(20), default="pending")  # pending, approved, adjusted
```

### Step 2: Update Quiz Creation

Modify QuizCreate Pydantic model:
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
    grading_mode: str = "auto"  # NEW: auto, manual, hybrid
```

### Step 3: Update Quiz Submission Logic

Modify submit_quiz endpoint to check grading mode:

```python
@app.post("/quizzes/submit")
def submit_quiz(submission: QuizSubmission, current_user: User, db: Session):
    # ... existing code ...
    
    # Check quiz grading mode
    quiz = db.query(Quiz).filter(Quiz.id == submission.quiz_id).first()
    
    # Determine if needs manual review
    needs_review = False
    if quiz.grading_mode in ["manual", "hybrid"]:
        # Check if quiz has open-ended questions
        has_open_ended = any(
            q.question_type in ["short_answer", "fill_blanks", "essay"]
            for q in questions
        )
        needs_review = has_open_ended
    
    # Create attempt
    attempt = QuizAttempt(
        quiz_id=submission.quiz_id,
        user_id=current_user.id,
        score=score if quiz.grading_mode == "auto" else 0,
        final_score=score if quiz.grading_mode == "auto" else None,
        total_questions=total_marks,
        needs_review=needs_review,
        completed_at=now()
    )
    
    # ... rest of code ...
```

### Step 4: Add Teacher Review Endpoints

```python
@app.get("/teacher/pending-reviews")
def get_pending_reviews(current_user: User, db: Session):
    """Get all quiz attempts that need teacher review"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403)
    
    # Get quizzes created by this teacher
    teacher_quizzes = db.query(Quiz).filter(
        Quiz.created_by == current_user.id,
        Quiz.grading_mode.in_(["manual", "hybrid"])
    ).all()
    
    quiz_ids = [q.id for q in teacher_quizzes]
    
    # Get attempts needing review
    pending_attempts = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id.in_(quiz_ids),
        QuizAttempt.needs_review == True,
        QuizAttempt.reviewed_at.is_(None)
    ).all()
    
    result = []
    for attempt in pending_attempts:
        student = db.query(User).filter(User.id == attempt.user_id).first()
        quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
        
        result.append({
            "attempt_id": attempt.id,
            "quiz_id": quiz.id,
            "quiz_title": quiz.title,
            "student_name": student.full_name,
            "student_username": student.username,
            "submitted_at": attempt.completed_at.isoformat(),
            "ai_score": attempt.score,
            "total_questions": attempt.total_questions
        })
    
    return result


@app.get("/teacher/review/{attempt_id}")
def get_attempt_for_review(attempt_id: int, current_user: User, db: Session):
    """Get detailed attempt data for teacher review"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403)
    
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404)
    
    quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
    if quiz.created_by != current_user.id:
        raise HTTPException(status_code=403)
    
    student = db.query(User).filter(User.id == attempt.user_id).first()
    student_answers = db.query(StudentAnswer).filter(
        StudentAnswer.attempt_id == attempt_id
    ).all()
    
    answers_detail = []
    for sa in student_answers:
        question = db.query(Question).filter(Question.id == sa.question_id).first()
        answers_detail.append({
            "answer_id": sa.id,
            "question_id": question.id,
            "question_text": question.question_text,
            "question_type": question.question_type,
            "max_points": question.points,
            "correct_answer": question.correct_answer,
            "student_answer": sa.student_answer,
            "ai_score": sa.points_earned,
            "ai_feedback": sa.ai_feedback,
            "teacher_score": sa.teacher_score,
            "teacher_feedback": sa.teacher_feedback,
            "review_status": sa.review_status
        })
    
    return {
        "attempt_id": attempt.id,
        "quiz_title": quiz.title,
        "student_name": student.full_name,
        "student_username": student.username,
        "submitted_at": attempt.completed_at.isoformat(),
        "answers": answers_detail
    }


@app.post("/teacher/review/{attempt_id}/grade")
def grade_attempt(
    attempt_id: int,
    grades: List[Dict],  # [{"answer_id": 1, "score": 8, "feedback": "Good"}]
    current_user: User,
    db: Session
):
    """Teacher grades an attempt"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403)
    
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404)
    
    quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
    if quiz.created_by != current_user.id:
        raise HTTPException(status_code=403)
    
    # Update each answer
    final_score = 0
    for grade in grades:
        answer = db.query(StudentAnswer).filter(
            StudentAnswer.id == grade["answer_id"]
        ).first()
        
        if answer:
            answer.teacher_score = grade.get("score", answer.points_earned)
            answer.teacher_feedback = grade.get("feedback", "")
            answer.review_status = "adjusted" if grade.get("score") != answer.points_earned else "approved"
            final_score += answer.teacher_score
    
    # Update attempt
    attempt.final_score = final_score
    attempt.reviewed_by = current_user.id
    attempt.reviewed_at = now()
    attempt.needs_review = False
    
    db.commit()
    
    return {
        "message": "Grading completed",
        "final_score": final_score,
        "total_questions": attempt.total_questions
    }


@app.post("/teacher/quiz/{quiz_id}/release-results")
def release_results(quiz_id: int, current_user: User, db: Session):
    """Release quiz results to students"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403)
    
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz or quiz.created_by != current_user.id:
        raise HTTPException(status_code=403)
    
    # Check if all attempts are reviewed
    pending = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.needs_review == True
    ).count()
    
    if pending > 0:
        raise HTTPException(
            status_code=400,
            detail=f"{pending} attempts still need review"
        )
    
    quiz.results_released = True
    db.commit()
    
    # Notify students
    attempts = db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).all()
    for attempt in attempts:
        notification = Notification(
            user_id=attempt.user_id,
            title=f"Results Released: {quiz.title}",
            message=f"Your quiz results are now available. Score: {attempt.final_score or attempt.score}/{attempt.total_questions}",
            type="results_released"
        )
        db.add(notification)
    
    db.commit()
    
    return {"message": "Results released to students"}
```

### Step 5: Update Student Results View

Modify student endpoints to check if results are released:

```python
@app.get("/student/progress")
def get_student_progress_endpoint(current_user: User, db: Session):
    # ... existing code ...
    
    # Only show quizzes where results are released OR auto-graded
    for attempt in attempts:
        quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
        
        # Skip if results not released for manual/hybrid quizzes
        if quiz.grading_mode in ["manual", "hybrid"] and not quiz.results_released:
            continue
        
        # Use final_score if available, otherwise use score
        display_score = attempt.final_score if attempt.final_score is not None else attempt.score
        
        # ... rest of code ...
```

## Usage Flow

### For Auto-Grading (Current Behavior)
1. Teacher creates quiz with `grading_mode="auto"`
2. Student submits quiz
3. AI grades immediately
4. Results shown to student instantly

### For Manual Review
1. Teacher creates quiz with `grading_mode="manual"`
2. Student submits quiz
3. AI provides suggested scores (not shown to student)
4. Teacher reviews at `/teacher/pending-reviews`
5. Teacher adjusts scores and adds feedback
6. Teacher clicks "Release Results"
7. Students can now see their scores

### For Hybrid Mode
1. Teacher creates quiz with `grading_mode="hybrid"`
2. MCQ questions: Auto-graded immediately
3. Open-ended questions: Held for review
4. Teacher reviews only open-ended answers
5. Teacher releases results when ready

## Benefits

✅ **Quality Control**: Teacher can verify AI grading
✅ **Fairness**: Manual review for subjective answers
✅ **Flexibility**: Choose per-quiz grading mode
✅ **Transparency**: Students see teacher feedback
✅ **Efficiency**: AI does initial grading, teacher adjusts

## Next Steps

1. Run database migration to add new columns
2. Update backend models and endpoints
3. Create teacher review UI page
4. Add "Pending Reviews" badge in teacher dashboard
5. Test with sample quiz

Would you like me to implement this system now?
