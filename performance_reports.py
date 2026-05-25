from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

def get_student_performance(db, user_id: int) -> Dict:
    """Get student performance statistics and quiz history"""
    
    # Get all quiz results for the student
    cursor = db.cursor()
    cursor.execute("""
        SELECT qr.quiz_id, qr.score, qr.submitted_at, q.title, q.total_questions
        FROM quiz_results qr
        JOIN quizzes q ON qr.quiz_id = q.id
        WHERE qr.user_id = ?
        ORDER BY qr.submitted_at DESC
    """, (user_id,))
    
    results = cursor.fetchall()
    
    if not results:
        return {
            "totalQuizzes": 0,
            "averageScore": 0,
            "bestScore": 0,
            "improvement": 0,
            "quizHistory": []
        }
    
    # Calculate statistics
    total_quizzes = len(results)
    scores = [result[1] for result in results]
    average_score = round(sum(scores) / len(scores), 1)
    best_score = max(scores)
    
    # Calculate improvement (compare first 3 vs last 3 quizzes)
    improvement = 0
    if total_quizzes >= 6:
        first_three = scores[-3:]  # First 3 quizzes (oldest)
        last_three = scores[:3]   # Last 3 quizzes (newest)
        first_avg = sum(first_three) / 3
        last_avg = sum(last_three) / 3
        improvement = round(last_avg - first_avg, 1)
    
    # Get rankings for each quiz
    quiz_history = []
    for result in results:
        quiz_id, score, submitted_at, title, total_questions = result
        
        # Get ranking for this quiz
        cursor.execute("""
            SELECT COUNT(*) + 1 as rank
            FROM quiz_results qr2
            WHERE qr2.quiz_id = ? AND qr2.score > ?
        """, (quiz_id, score))
        
        rank = cursor.fetchone()[0]
        
        quiz_history.append({
            "date": submitted_at,
            "title": title,
            "score": score,
            "rank": rank
        })
    
    return {
        "totalQuizzes": total_quizzes,
        "averageScore": average_score,
        "bestScore": best_score,
        "improvement": improvement,
        "quizHistory": quiz_history
    }

def generate_department_report(db, department: str, level: str, report_type: str, date: str) -> Dict:
    """Generate department report for specified period"""
    
    target_date = datetime.strptime(date, "%Y-%m-%d")
    
    # Calculate date range based on report type
    if report_type == "daily":
        start_date = target_date
        end_date = target_date + timedelta(days=1)
    elif report_type == "weekly":
        # Get start of week (Monday)
        start_date = target_date - timedelta(days=target_date.weekday())
        end_date = start_date + timedelta(days=7)
    else:  # monthly
        start_date = target_date.replace(day=1)
        if target_date.month == 12:
            end_date = target_date.replace(year=target_date.year + 1, month=1, day=1)
        else:
            end_date = target_date.replace(month=target_date.month + 1, day=1)
    
    cursor = db.cursor()
    
    # Get quiz results for the department and level in the specified period
    cursor.execute("""
        SELECT 
            u.username,
            u.full_name,
            q.title as quiz_title,
            qr.score,
            qr.submitted_at,
            q.total_questions
        FROM quiz_results qr
        JOIN users u ON qr.user_id = u.id
        JOIN quizzes q ON qr.quiz_id = q.id
        WHERE u.department = ? 
        AND u.level = ?
        AND qr.submitted_at >= ?
        AND qr.submitted_at < ?
        ORDER BY qr.submitted_at DESC, qr.score DESC
    """, (department, level, start_date.isoformat(), end_date.isoformat()))
    
    results = cursor.fetchall()
    
    # Calculate statistics
    total_students = len(set(result[0] for result in results))
    total_quizzes = len(set(result[2] for result in results))
    
    if results:
        scores = [result[3] for result in results]
        average_score = round(sum(scores) / len(scores), 1)
        highest_score = max(scores)
        lowest_score = min(scores)
    else:
        average_score = 0
        highest_score = 0
        lowest_score = 0
    
    # Format results for report
    formatted_results = []
    for result in results:
        formatted_results.append({
            "username": result[0],
            "full_name": result[1],
            "quiz_title": result[2],
            "score": result[3],
            "submitted_at": result[4],
            "total_questions": result[5]
        })
    
    return {
        "department": department,
        "level": level,
        "report_type": report_type,
        "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
        "statistics": {
            "total_students": total_students,
            "total_quizzes": total_quizzes,
            "average_score": average_score,
            "highest_score": highest_score,
            "lowest_score": lowest_score
        },
        "results": formatted_results
    }
