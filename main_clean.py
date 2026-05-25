from ai_grader import grade_open_ended_question
from performance_reports import get_student_performance
    results_released = Column(Boolean, default=False)
    score = Column(Float, default=0.0)
    needs_review = Column(Boolean, default=False)
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    final_score = Column(Float)
    teacher_score = Column(Float)
    teacher_feedback = Column(Text)
        score = 0.0
            # Clean answer: remove newlines and extra spaces
            if user_answer:
                user_answer = str(user_answer).replace('\n', ' ').replace('\r', ' ').strip()
                    grading_details.append({
                        "question_id": question.id,
                        "points_earned": 0.0,
                        "max_points": int(question.points or 1),
                        "feedback": feedback
                    })
                    continue  # Skip to next question
                elif question.question_type == "short_answer" or question.question_type == "fill_blanks":
                    try:
                        # Use CONCEPT-BASED grader - understands meaning globally
                        from concept_grader import concept_based_grade
                        points_earned, feedback, confidence = concept_based_grade(
                            student_answer=str(user_answer),
                            correct_answer=str(question.correct_answer or ""),
                            max_points=int(question.points or 1),
                            question_text=str(question.question_text or "")
                        )
                        score += points_earned
                    except Exception as grade_err:
                        print(f"AI grading failed for question {question.id}, using fallback: {grade_err}")
                        # Fallback: simple string comparison
                        if str(user_answer).strip().lower() == str(question.correct_answer or "").strip().lower():
                            points_earned = question.points
                            score += points_earned
                            feedback = "Correct"
                        else:
                            points_earned = 0
                            feedback = "Incorrect"
            completed_at=now(),
            needs_review=True  # All quizzes need teacher review
            "needs_review": True,
            "message": "Quiz submitted successfully! Your answers are under review by your teacher. Results will be available soon.",
            "quiz_title": quiz.title
        "version": "1.8-SUBMISSION-FIX",
        "cors": "enabled",
        "fix_deployed": "2026-01-10-12:40"
@app.put("/questions/{question_id}")
def update_question(question_id: int, question_data: QuestionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can edit questions")
    question = db.query(Question).filter(Question.id == question_id, Question.created_by == current_user.id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    question.question_text = question_data.question_text
    question.question_type = question_data.question_type
    question.correct_answer = question_data.correct_answer
    question.options = question_data.options
    question.points = question_data.points
    question.department = question_data.department
    question.level = question_data.level
    db.commit()
    return question

    # Delete student answers first
    db.query(StudentAnswer).filter(StudentAnswer.question_id == question_id).delete(synchronize_session=False)
    # Remove question from quizzes
    db.query(QuizQuestion).filter(QuizQuestion.question_id == question_id).delete(synchronize_session=False)
    # Delete student answers first
    db.query(StudentAnswer).filter(StudentAnswer.question_id.in_(question_ids)).delete(synchronize_session=False)
    # Remove questions from quizzes
    db.query(QuizQuestion).filter(QuizQuestion.question_id.in_(question_ids)).delete(synchronize_session=False)
    for idx, attempt in enumerate(sorted(attempts, key=lambda x: (x.final_score if x.final_score is not None else x.score), reverse=True), 1):
        student = db.query(User).filter(User.id == attempt.user_id).first()
        if student:
            display_score = attempt.final_score if attempt.final_score is not None else attempt.score
            percentage = round((display_score / attempt.total_questions * 100) if attempt.total_questions > 0 else 0, 1)
            data.append([str(idx), student.full_name, student.username, f"{display_score}/{attempt.total_questions}", f"{percentage}%"])
            # Use final_score (teacher-reviewed) if available, otherwise use initial score
            display_score = attempt.final_score if attempt.final_score is not None else attempt.score
            results.append({
                "student_name": student.full_name,
                "username": student.username,
                "score": display_score,
                "total": attempt.total_questions,
                "percentage": round((display_score / attempt.total_questions * 100) if attempt.total_questions > 0 else 0, 1),
@app.get("/student/progress")
def get_student_progress_endpoint(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can access progress")
    
    # Get all quiz attempts for the student
    attempts = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == current_user.id,
        QuizAttempt.completed_at.isnot(None)
    ).order_by(QuizAttempt.completed_at.desc()).all()
    
    # Filter: only show attempts where results are released
    visible_attempts = []
    for attempt in attempts:
        quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
        if quiz and quiz.results_released:
            visible_attempts.append(attempt)
    
    if not visible_attempts:
        return {
            "total_quizzes": 0,
            "overall_percentage": 0,
            "recent_quizzes": [],
            "improvement_tips": ["Complete your first quiz to see your progress!"]
        }
    
    # Calculate overall stats
    total_score = sum(a.final_score if a.final_score else a.score for a in visible_attempts)
    total_possible = sum(a.total_questions for a in visible_attempts)
    overall_percentage = round((total_score / total_possible * 100) if total_possible > 0 else 0, 1)
    
    # Get recent quizzes with details
    recent_quizzes = []
    for attempt in visible_attempts[:10]:  # Last 10 quizzes
        quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
        if quiz:
            display_score = attempt.final_score if attempt.final_score else attempt.score
            percentage = round((display_score / attempt.total_questions * 100) if attempt.total_questions > 0 else 0, 1)
            grade = 'A+' if percentage >= 90 else 'A' if percentage >= 80 else 'B' if percentage >= 70 else 'C' if percentage >= 60 else 'D'
            
            recent_quizzes.append({
                "quiz_id": quiz.id,
                "quiz_title": quiz.title,
                "department": quiz.department,
                "level": quiz.level,
                "score": display_score,
                "total_questions": attempt.total_questions,
                "percentage": percentage,
                "grade": grade,
                "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None
            })
    
    # Generate improvement tips
    improvement_tips = []
    if overall_percentage < 70:
        improvement_tips.append("Review your incorrect answers to learn from mistakes")
        improvement_tips.append("Practice more quizzes to improve your understanding")
    elif overall_percentage < 85:
        improvement_tips.append("You're doing well! Focus on challenging topics to reach excellence")
    else:
        improvement_tips.append("Excellent work! Keep maintaining your high performance")
    
    return {
        "total_quizzes": len(visible_attempts),
        "overall_percentage": overall_percentage,
        "recent_quizzes": recent_quizzes,
        "improvement_tips": improvement_tips
    }

@app.get("/student-report/{quiz_id}")
def download_student_report(quiz_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can download their reports")
    
    # Get the student's attempt for this quiz
    attempt = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.user_id == current_user.id
    ).first()
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Quiz attempt not found")
    
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Get detailed answers
    student_answers = db.query(StudentAnswer).filter(
        StudentAnswer.attempt_id == attempt.id
    ).all()
    
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    import io
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#1a5490'), alignment=TA_CENTER, spaceAfter=12)
    subtitle_style = ParagraphStyle('CustomSubtitle', parent=styles['Normal'], fontSize=12, textColor=colors.HexColor('#666666'), alignment=TA_CENTER, spaceAfter=20)
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontSize=10, alignment=TA_LEFT)
    
    # Title
    elements.append(Paragraph(f"Quiz Performance Report", title_style))
    elements.append(Paragraph(f"{quiz.title}", subtitle_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Student info - use final_score if available
    display_score = attempt.final_score if attempt.final_score is not None else attempt.score
    percentage = round((display_score / attempt.total_questions * 100) if attempt.total_questions > 0 else 0, 1)
    grade = 'A+' if percentage >= 90 else 'A' if percentage >= 80 else 'B' if percentage >= 70 else 'C' if percentage >= 60 else 'D'
    
    info_data = [
        ['Student:', current_user.full_name],
        ['Username:', current_user.username],
        ['Department:', current_user.department],
        ['Level:', current_user.level],
        ['Score:', f"{display_score}/{attempt.total_questions}"],
        ['Percentage:', f"{percentage}%"],
        ['Grade:', grade],
        ['Completed:', attempt.completed_at.strftime('%Y-%m-%d %H:%M') if attempt.completed_at else 'N/A']
    ]
    
    info_table = Table(info_data, colWidths=[1.5*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Detailed answers
    elements.append(Paragraph("Detailed Results", styles['Heading2']))
    elements.append(Spacer(1, 0.1*inch))
    
    for idx, student_answer in enumerate(student_answers, 1):
        question = db.query(Question).filter(Question.id == student_answer.question_id).first()
        if question:
            # Question
            elements.append(Paragraph(f"<b>Question {idx}:</b> {question.question_text}", normal_style))
            elements.append(Spacer(1, 0.05*inch))
            
            # Student answer
            elements.append(Paragraph(f"<b>Your Answer:</b> {student_answer.student_answer or 'Not answered'}", normal_style))
            elements.append(Spacer(1, 0.05*inch))
            
            # Correct answer
            elements.append(Paragraph(f"<b>Correct Answer:</b> {question.correct_answer}", normal_style))
            elements.append(Spacer(1, 0.05*inch))
            
            # Result - use teacher score if available
            final_points = student_answer.teacher_score if student_answer.teacher_score is not None else student_answer.points_earned
            feedback = student_answer.teacher_feedback if student_answer.teacher_feedback else (student_answer.ai_feedback or ('Correct' if student_answer.is_correct else 'Incorrect'))
            result_color = 'green' if final_points >= (question.points * 0.7) else 'red'
            result_text = f"<font color='{result_color}'><b>Result:</b> {feedback} ({final_points}/{question.points} points)</font>"
            elements.append(Paragraph(result_text, normal_style))
            elements.append(Spacer(1, 0.15*inch))
    
    doc.build(elements)
    buffer.seek(0)
    
    return StreamingResponse(
        buffer, 
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Quiz_Report_{quiz.title.replace(' ', '_')}_{current_user.username}.pdf"}
    )

        db.close()# Teacher Review Endpoints - Add to main.py

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
        "quiz_id": quiz.id,
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



# Teacher Review Endpoints
class GradeAdjustment(BaseModel):
    answer_id: int
    score: float
    feedback: str

class ReviewRequest(BaseModel):
    grades: List[GradeAdjustment]

@app.get("/teacher/pending-reviews")
def get_pending_reviews(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403)
    attempts = db.query(QuizAttempt).join(Quiz).filter(Quiz.created_by == current_user.id, QuizAttempt.needs_review == True, QuizAttempt.reviewed_by == None).all()
    result = []
    for attempt in attempts:
        quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
        student = db.query(User).filter(User.id == attempt.user_id).first()
        result.append({"attempt_id": attempt.id, "quiz_title": quiz.title, "student_name": student.full_name, "score": attempt.score, "submitted_at": attempt.completed_at})
    return result

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
        answer_details.append({"answer_id": ans.id, "question_text": question.question_text, "correct_answer": question.correct_answer, "student_answer": ans.student_answer, "ai_score": ans.points_earned, "ai_feedback": ans.ai_feedback, "max_points": question.points, "teacher_score": ans.teacher_score, "teacher_feedback": ans.teacher_feedback})
    return {"attempt_id": attempt.id, "quiz_title": quiz.title, "student_name": student.full_name, "total_score": attempt.score, "answers": answer_details}

@app.post("/teacher/review/{attempt_id}/grade")
def submit_review(attempt_id: int, review: ReviewRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403)
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404)
    new_total = 0.0
    for grade in review.grades:
        answer = db.query(StudentAnswer).filter(StudentAnswer.id == grade.answer_id).first()
        if answer:
            answer.teacher_score = grade.score
            answer.teacher_feedback = grade.feedback
            new_total += grade.score
    attempt.final_score = new_total
    attempt.reviewed_by = current_user.id
    attempt.needs_review = False
    db.commit()
    return {"message": "Review submitted", "final_score": new_total}

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

@app.get("/teacher/quiz/{quiz_id}/review-status")
def get_review_status(quiz_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403)
    total = db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).count()
    pending = db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id, QuizAttempt.needs_review == True, QuizAttempt.reviewed_by == None).count()
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    return {"total_submissions": total, "pending_review": pending, "results_released": quiz.results_released if quiz else False}

@app.post("/report-cheating")
def report_cheating(data: Dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Report student cheating attempt to teacher"""
    try:
        quiz_id = data.get('quiz_id')
        warnings = data.get('warnings', 0)
        reason = data.get('reason', 'Unknown')
        
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not quiz:
            return {"message": "Quiz not found"}
        
        teacher = db.query(User).filter(User.id == quiz.created_by).first()
        if teacher:
            notification = Notification(
                user_id=teacher.id,
                title=f"⚠️ Cheating Alert: {quiz.title}",
                message=f"{current_user.full_name} was caught attempting to cheat ({warnings} violations). Reason: {reason}. Quiz was auto-submitted.",
                type="cheating_alert"
            )
            db.add(notification)
            db.commit()
        
        return {"message": "Cheating reported to teacher"}
    except Exception as e:
        print(f"Error reporting cheating: {e}")
        return {"message": "Failed to report"}
