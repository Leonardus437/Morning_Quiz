# Teacher Review Endpoints - Add to main.py

from pydantic import BaseModel
from typing import List

class GradeAdjustment(BaseModel):
    answer_id: int
    score: float
    feedback: str

class ReviewRequest(BaseModel):
    grades: List[GradeAdjustment]

# 1. Get pending reviews
@app.get("/teacher/pending-reviews")
def get_pending_reviews(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403)
    
    attempts = db.query(QuizAttempt).join(Quiz).filter(
        Quiz.created_by == current_user.id,
        QuizAttempt.needs_review == True,
        QuizAttempt.reviewed_by == None
    ).all()
    
    result = []
    for attempt in attempts:
        quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
        student = db.query(User).filter(User.id == attempt.user_id).first()
        result.append({
            "attempt_id": attempt.id,
            "quiz_title": quiz.title,
            "student_name": student.full_name,
            "score": attempt.score,
            "submitted_at": attempt.completed_at
        })
    
    return result

# 2. Get attempt details for review
@app.get("/teacher/review/{attempt_id}")
def get_attempt_for_review(attempt_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403)
    
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404)
    
    quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
    student = db.query(User).filter(User.id == attempt.user_id).first()
    answers = db.query(StudentAnswer).filter(StudentAnswer.attempt_id == attempt_id).all()
    
    answer_details = []
    for ans in answers:
        question = db.query(Question).filter(Question.id == ans.question_id).first()
        answer_details.append({
            "answer_id": ans.id,
            "question_text": question.question_text,
            "correct_answer": question.correct_answer,
            "student_answer": ans.student_answer,
            "ai_score": ans.points_earned,
            "ai_feedback": ans.ai_feedback,
            "max_points": question.points,
            "teacher_score": ans.teacher_score,
            "teacher_feedback": ans.teacher_feedback
        })
    
    return {
        "attempt_id": attempt.id,
        "quiz_title": quiz.title,
        "student_name": student.full_name,
        "total_score": attempt.score,
        "answers": answer_details
    }

# 3. Submit review and adjust grades
@app.post("/teacher/review/{attempt_id}/grade")
def submit_review(attempt_id: int, review: ReviewRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403)
    
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404)
    
    # Update each answer with teacher's grade
    new_total = 0.0
    for grade in review.grades:
        answer = db.query(StudentAnswer).filter(StudentAnswer.id == grade.answer_id).first()
        if answer:
            answer.teacher_score = grade.score
            answer.teacher_feedback = grade.feedback
            new_total += grade.score
    
    # Update attempt
    attempt.final_score = new_total
    attempt.reviewed_by = current_user.id
    attempt.needs_review = False
    
    db.commit()
    
    return {"message": "Review submitted", "final_score": new_total}

# 4. Release results to students
@app.post("/teacher/quiz/{quiz_id}/release-results")
def release_results(quiz_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403)
    
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz or quiz.created_by != current_user.id:
        raise HTTPException(status_code=404)
    
    quiz.results_released = True
    db.commit()
    
    return {"message": "Results released to students"}

# 5. Get review status
@app.get("/teacher/quiz/{quiz_id}/review-status")
def get_review_status(quiz_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403)
    
    total = db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).count()
    pending = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.needs_review == True,
        QuizAttempt.reviewed_by == None
    ).count()
    
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    
    return {
        "total_submissions": total,
        "pending_review": pending,
        "results_released": quiz.results_released if quiz else False
    }
