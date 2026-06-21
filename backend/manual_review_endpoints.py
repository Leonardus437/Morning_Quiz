"""
Manual Review System Endpoints
Add these to main.py
"""

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from pydantic import BaseModel

# Pydantic models for manual review
class GradeAdjustment(BaseModel):
    answer_id: int
    score: float
    feedback: str

class ManualGradeRequest(BaseModel):
    grades: List[GradeAdjustment]

# ENDPOINTS TO ADD TO main.py

@app.get("/teacher/pending-reviews")
def get_pending_reviews(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all quiz attempts that need teacher review"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can access reviews")
    
    # Get quizzes created by this teacher that need manual review
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
    ).order_by(QuizAttempt.completed_at.desc()).all()
    
    result = []
    for attempt in pending_attempts:
        student = db.query(User).filter(User.id == attempt.user_id).first()
        quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
        
        # Count low confidence answers
        low_confidence_count = db.query(StudentAnswer).filter(
            StudentAnswer.attempt_id == attempt.id,
            StudentAnswer.ai_confidence < 0.7
        ).count()
        
        result.append({
            "attempt_id": attempt.id,
            "quiz_id": quiz.id,
            "quiz_title": quiz.title,
            "student_name": student.full_name,
            "student_username": student.username,
            "submitted_at": attempt.completed_at.isoformat() if attempt.completed_at else None,
            "ai_score": attempt.score,
            "total_questions": attempt.total_questions,
            "ai_confidence": attempt.ai_confidence,
            "low_confidence_answers": low_confidence_count,
            "grading_mode": quiz.grading_mode
        })
    
    return {"pending_reviews": result, "total_count": len(result)}


@app.get("/teacher/review/{attempt_id}")
def get_attempt_for_review(attempt_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get detailed attempt data for teacher review"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can review")
    
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    
    quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
    if quiz.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not your quiz")
    
    student = db.query(User).filter(User.id == attempt.user_id).first()
    student_answers = db.query(StudentAnswer).filter(
        StudentAnswer.attempt_id == attempt_id
    ).all()
    
    answers_detail = []
    for sa in student_answers:
        question = db.query(Question).filter(Question.id == sa.question_id).first()
        
        # Only include open-ended questions for manual/hybrid mode
        if quiz.grading_mode == "hybrid" and question.question_type not in ["short_answer", "fill_blanks", "essay"]:
            continue
        
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
            "ai_confidence": sa.ai_confidence,
            "teacher_score": sa.teacher_score,
            "teacher_feedback": sa.teacher_feedback,
            "review_status": sa.review_status,
            "needs_attention": sa.ai_confidence < 0.7
        })
    
    return {
        "attempt_id": attempt.id,
        "quiz_id": quiz.id,
        "quiz_title": quiz.title,
        "grading_mode": quiz.grading_mode,
        "student_name": student.full_name,
        "student_username": student.username,
        "department": student.department,
        "level": student.level,
        "submitted_at": attempt.completed_at.isoformat() if attempt.completed_at else None,
        "ai_total_score": attempt.score,
        "total_possible": attempt.total_questions,
        "ai_confidence": attempt.ai_confidence,
        "answers": answers_detail
    }


@app.post("/teacher/review/{attempt_id}/grade")
def grade_attempt(
    attempt_id: int,
    request: ManualGradeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Teacher grades an attempt"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can grade")
    
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    
    quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
    if quiz.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not your quiz")
    
    # Update each answer
    final_score = 0
    for grade in request.grades:
        answer = db.query(StudentAnswer).filter(
            StudentAnswer.id == grade.answer_id
        ).first()
        
        if answer and answer.attempt_id == attempt_id:
            answer.teacher_score = grade.score
            answer.teacher_feedback = grade.feedback
            answer.review_status = "adjusted" if grade.score != answer.points_earned else "approved"
            final_score += grade.score
    
    # For hybrid mode, add auto-graded MCQ scores
    if quiz.grading_mode == "hybrid":
        auto_graded = db.query(StudentAnswer).filter(
            StudentAnswer.attempt_id == attempt_id,
            StudentAnswer.review_status == "pending"
        ).all()
        for ans in auto_graded:
            question = db.query(Question).filter(Question.id == ans.question_id).first()
            if question.question_type not in ["short_answer", "fill_blanks", "essay"]:
                final_score += ans.points_earned
                ans.review_status = "auto"
    
    # Update attempt
    attempt.final_score = final_score
    attempt.reviewed_by = current_user.id
    attempt.reviewed_at = now()
    attempt.needs_review = False
    
    db.commit()
    
    # Notify student
    notification = Notification(
        user_id=attempt.user_id,
        title=f"Quiz Reviewed: {quiz.title}",
        message=f"Your teacher has reviewed your quiz. Final score: {final_score}/{attempt.total_questions}",
        type="quiz_reviewed"
    )
    db.add(notification)
    db.commit()
    
    return {
        "message": "Grading completed successfully",
        "final_score": final_score,
        "total_questions": attempt.total_questions,
        "percentage": round((final_score / attempt.total_questions * 100) if attempt.total_questions > 0 else 0, 1)
    }


@app.post("/teacher/quiz/{quiz_id}/release-results")
def release_results(quiz_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Release quiz results to students"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can release results")
    
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz or quiz.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not your quiz")
    
    # Check if all attempts are reviewed
    pending = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.needs_review == True
    ).count()
    
    if pending > 0:
        raise HTTPException(
            status_code=400,
            detail=f"{pending} attempts still need review before releasing results"
        )
    
    quiz.results_released = True
    db.commit()
    
    # Notify all students
    attempts = db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).all()
    for attempt in attempts:
        score = attempt.final_score if attempt.final_score is not None else attempt.score
        notification = Notification(
            user_id=attempt.user_id,
            title=f"Results Released: {quiz.title}",
            message=f"Your quiz results are now available. Score: {score}/{attempt.total_questions}",
            type="results_released"
        )
        db.add(notification)
    
    db.commit()
    
    return {
        "message": "Results released successfully",
        "students_notified": len(attempts)
    }


@app.get("/teacher/quiz/{quiz_id}/review-status")
def get_quiz_review_status(quiz_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get review status for a quiz"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403)
    
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz or quiz.created_by != current_user.id:
        raise HTTPException(status_code=403)
    
    total_attempts = db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).count()
    pending_reviews = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.needs_review == True
    ).count()
    reviewed = total_attempts - pending_reviews
    
    return {
        "quiz_id": quiz_id,
        "quiz_title": quiz.title,
        "grading_mode": quiz.grading_mode,
        "results_released": quiz.results_released,
        "total_attempts": total_attempts,
        "reviewed": reviewed,
        "pending_review": pending_reviews,
        "can_release": pending_reviews == 0
    }
