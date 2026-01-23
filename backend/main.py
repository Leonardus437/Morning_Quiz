from fastapi import FastAPI, Depends, HTTPException, status, Request, File, UploadFile, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import hashlib
import secrets
from jose import JWTError, jwt
import os
import json
import io
import re
import PyPDF2

from ai_grader import grade_open_ended_question
from performance_reports import get_student_performance

# Import AI grader with fallback
try:
    from ai_grader import grade_open_ended_question
    AI_GRADER_AVAILABLE = True
    print("✅ AI Grader loaded successfully")
except Exception as e:
    AI_GRADER_AVAILABLE = False
    print(f"⚠️ AI Grader not available: {e}")
    
    # Fallback simple grader
    def grade_open_ended_question(student_answer: str, correct_answer: str, max_points: int = 1, **kwargs):
        """Fallback simple grading if AI grader fails"""
        if not student_answer or not str(student_answer).strip():
            return 0, "No answer provided"
        
        student = str(student_answer).strip().lower()
        correct = str(correct_answer).strip().lower()
        
        if student == correct:
            return max_points, "Correct"
        elif correct in student or student in correct:
            return max_points * 0.8, "Mostly correct"
        else:
            return 0, "Incorrect"

# Rwanda timezone (CAT/EAT - UTC+2)
RWANDA_TZ = timezone(timedelta(hours=2))

def now():
    """Get current time in Rwanda timezone (CAT/EAT - UTC+2)"""
    return datetime.utcnow() + timedelta(hours=2)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///quiz.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

security = HTTPBearer()

app = FastAPI(title="TVET/TSS Quiz API - Offline First")

# CRITICAL: Add CORS middleware BEFORE any routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://tsskwizi.pages.dev",
        "https://d4e95bdd.tsskwizi.pages.dev",
        "http://localhost:3000",
        "http://localhost:5173",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password_hash = Column(String(255))
    role = Column(String(20), default="student")
    full_name = Column(String(100))
    department = Column(String(100))
    level = Column(String(50))
    departments = Column(JSON)
    is_class_teacher = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text)
    question_type = Column(String)
    options = Column(JSON)
    correct_answer = Column(String)
    points = Column(Integer, default=1)
    department = Column(String)
    level = Column(String)
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class Quiz(Base):
    __tablename__ = "quizzes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    scheduled_time = Column(DateTime)
    duration_minutes = Column(Integer, default=30)
    question_time_seconds = Column(Integer, default=60)
    countdown_started_at = Column(DateTime)
    is_active = Column(Boolean, default=False)
    shuffle_questions = Column(Boolean, default=True)
    department = Column(String)
    level = Column(String)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    results_released = Column(Boolean, default=False)

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    question_order = Column(Integer)

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    score = Column(Float, default=0.0)

    total_questions = Column(Integer)
    answers = Column(JSON)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    needs_review = Column(Boolean, default=False)
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    final_score = Column(Float)

class StudentAnswer(Base):
    __tablename__ = "student_answers"
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("quiz_attempts.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    student_answer = Column(String)
    is_correct = Column(Boolean)
    points_earned = Column(Float, default=0.0)
    ai_feedback = Column(String)

    teacher_score = Column(Float)
    teacher_feedback = Column(Text)

class Lesson(Base):
    __tablename__ = "lessons"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    code = Column(String, unique=True)
    description = Column(Text)
    department = Column(String)
    level = Column(String)
    classification = Column(String)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    message = Column(Text)
    type = Column(String, default="info")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class TeacherLesson(Base):
    __tablename__ = "teacher_lessons"
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    assigned_at = Column(DateTime, default=datetime.utcnow)

# Pydantic models
class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    role: str = "student"
    department: Optional[str] = None
    level: Optional[str] = None
    departments: Optional[List[str]] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user: Optional[Dict] = None

class QuestionCreate(BaseModel):
    question_text: str
    question_type: str
    options: Optional[List[str]] = None
    correct_answer: str
    points: int = 1
    department: str
    level: str
    lesson_id: Optional[int] = None

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

class QuizAnswer(BaseModel):
    question_id: int
    answer: str

class QuizSubmission(BaseModel):
    quiz_id: int
    answers: List[QuizAnswer]

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Use bcrypt for secure password hashing
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False

def hash_password_simple(password: str) -> str:
    if BCRYPT_AVAILABLE:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    else:
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"

def verify_password_simple(password: str, hashed: str) -> bool:
    try:
        if hashed.startswith('$2b$') and BCRYPT_AVAILABLE:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        elif ':' in hashed:
            salt, password_hash = hashed.split(':', 1)
            computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return computed_hash == password_hash
        else:
            return False
    except Exception as e:
        print(f"Password verification error: {e}")
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = now() + expires_delta
    else:
        expire = now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        if not credentials or not credentials.credentials:
            raise HTTPException(status_code=401, detail="Authentication token required")
        
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token format")
    except JWTError as e:
        error_msg = str(e).lower()
        if "expired" in error_msg:
            raise HTTPException(status_code=401, detail="Token has expired. Please login again.")
        else:
            raise HTTPException(status_code=401, detail="Invalid token. Please login again.")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed. Please login again.")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found. Please login again.")
    return user

# Routes
@app.post("/auth/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    username = user_data.username.strip() if user_data.username else ""
    password = user_data.password.strip() if user_data.password else ""
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    if not verify_password_simple(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    
    user_dict = {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "full_name": user.full_name or "",
        "department": user.department,
        "level": user.level,
        "departments": user.departments or [],
        "is_class_teacher": bool(getattr(user, 'is_class_teacher', False))
    }
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_dict
    }

@app.options("/quizzes")
async def quizzes_options():
    """Handle CORS preflight for quizzes"""
    return {"message": "OK"}

@app.get("/quizzes")
def get_quizzes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == "teacher":
        quizzes = db.query(Quiz).filter(Quiz.created_by == current_user.id).all()
        return quizzes
    
    if not current_user.department or not current_user.level:
        raise HTTPException(status_code=400, detail="Student must have department and level assigned")
    
    quizzes = db.query(Quiz).filter(
        Quiz.is_active == True,
        Quiz.department == current_user.department,
        Quiz.level == current_user.level
    ).all()
    
    result = []
    for quiz in quizzes:
        attempt = db.query(QuizAttempt).filter(
            QuizAttempt.quiz_id == quiz.id,
            QuizAttempt.user_id == current_user.id
        ).first()
        
        quiz_dict = {
            "id": quiz.id,
            "title": quiz.title,
            "description": quiz.description,
            "department": quiz.department,
            "level": quiz.level,
            "duration_minutes": quiz.duration_minutes,
            "question_time_seconds": quiz.question_time_seconds,
            "shuffle_questions": quiz.shuffle_questions,
            "is_active": quiz.is_active,
            "created_at": quiz.created_at,
            "scheduled_time": quiz.scheduled_time.isoformat() if quiz.scheduled_time else None,
            "countdown_started_at": quiz.countdown_started_at.isoformat() if quiz.countdown_started_at else None,
            "already_attempted": attempt is not None
        }
        
        if quiz.countdown_started_at:
            current_time = now()
            countdown_time = quiz.countdown_started_at
            
            elapsed = (current_time - countdown_time).total_seconds()
            total = quiz.duration_minutes * 60
            
            # Debug logging
            print(f"DEBUG Quiz {quiz.id}: current={current_time.strftime('%H:%M:%S')}, started={countdown_time.strftime('%H:%M:%S')}, elapsed={elapsed}s, total={total}s")
            
            quiz_dict["time_remaining"] = max(0, total - elapsed)
            quiz_dict["is_expired"] = elapsed > total
            quiz_dict["debug_info"] = {
                "current_rwanda": current_time.isoformat(),
                "started_at": countdown_time.isoformat(),
                "elapsed_seconds": int(elapsed),
                "total_seconds": int(total),
                "is_expired": elapsed > total
            }
        else:
            quiz_dict["time_remaining"] = quiz.duration_minutes * 60
            quiz_dict["is_expired"] = False
        
        result.append(quiz_dict)
    
    return result

@app.get("/quizzes/{quiz_id}/questions")
def get_quiz_questions(quiz_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    if current_user.role == "student":
        if quiz.department != current_user.department or quiz.level != current_user.level:
            raise HTTPException(status_code=403, detail=f"Access denied. This quiz is for {quiz.department} - {quiz.level} students only.")
        
        if not quiz.is_active:
            raise HTTPException(status_code=403, detail="Quiz is not active")
    
    attempt = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.user_id == current_user.id
    ).first()
    
    if attempt and current_user.role == "student":
        return {
            "quiz_already_attempted": True,
            "message": "Quiz Already Completed",
            "detail": f"You have already completed this quiz. Your score: {attempt.score}/{attempt.total_questions}",
            "quiz_title": quiz.title,
            "score": attempt.score,
            "total_questions": attempt.total_questions,
            "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None
        }
    
    if quiz.countdown_started_at:
        total_quiz_time = quiz.duration_minutes * 60
        current_time = now()
        countdown_time = quiz.countdown_started_at
        
        elapsed_time = (current_time - countdown_time).total_seconds()
        
        if elapsed_time > total_quiz_time:
            minutes_ago = int((elapsed_time - total_quiz_time) / 60)
            return {
                "quiz_ended": True,
                "message": "Quiz Time Expired",
                "detail": f"This quiz ended {minutes_ago} minute{'s' if minutes_ago != 1 else ''} ago. Please wait for your teacher to rebroadcast the quiz or start a new session.",
                "quiz_title": quiz.title,
                "ended_minutes_ago": minutes_ago,
                "debug_current_rwanda": current_time.strftime("%H:%M:%S"),
                "debug_started_rwanda": countdown_time.strftime("%H:%M:%S"),
                "debug_elapsed_seconds": int(elapsed_time)
            }
    
    questions = db.query(Question).join(QuizQuestion).filter(
        QuizQuestion.quiz_id == quiz_id
    ).order_by(QuizQuestion.question_order).all()
    
    if quiz.shuffle_questions and current_user.role == "student":
        import random
        random.seed(f"{current_user.id}_{quiz_id}")
        random.shuffle(questions)
    
    if current_user.role != "teacher":
        for question in questions:
            question.correct_answer = None
    
    return questions

@app.options("/quizzes/submit")
async def submit_quiz_options():
    """Handle CORS preflight for quiz submission"""
    return {"message": "OK"}

@app.post("/quizzes/submit")
def submit_quiz(submission: QuizSubmission, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == submission.quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    existing = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == submission.quiz_id,
        QuizAttempt.user_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Quiz already submitted")
    
    score = 0.0
    needs_review = False
    attempt = QuizAttempt(
        quiz_id=submission.quiz_id,
        user_id=current_user.id,
        total_questions=len(submission.answers),
        answers={},
        completed_at=now()
    )
    db.add(attempt)
    db.flush()
    
    for answer in submission.answers:
        question = db.query(Question).filter(Question.id == answer.question_id).first()
        if not question:
            continue
        
        is_correct = False
        points = 0.0
        feedback = ""
        
        if question.question_type in ['short_answer', 'essay']:
            points, feedback = grade_open_ended_question(
                answer.answer, question.correct_answer, question.points
            )
            needs_review = True
        else:
            is_correct = str(answer.answer).strip().lower() == str(question.correct_answer).strip().lower()
            points = question.points if is_correct else 0.0
            feedback = "Correct" if is_correct else "Incorrect"
        
        score += points
        student_answer = StudentAnswer(
            attempt_id=attempt.id,
            question_id=question.id,
            student_answer=answer.answer,
            is_correct=is_correct,
            points_earned=points,
            ai_feedback=feedback
        )
        db.add(student_answer)
    
    attempt.score = score
    attempt.needs_review = needs_review
    db.commit()
    
    # Notify teacher about submission (no auto-submit reason here - manual submission)
    teacher = db.query(User).filter(User.id == quiz.created_by).first()
    if teacher:
        notification = Notification(
            user_id=teacher.id,
            title=f"📝 New Quiz Submission: {quiz.title}",
            message=f"{current_user.full_name} has submitted the quiz. Score: {score}/{len(submission.answers)}. Click to review.",
            type="quiz_submission"
        )
        db.add(notification)
        db.commit()
    
    return {"score": score, "total": len(submission.answers), "needs_review": needs_review}

@app.get("/quizzes/{quiz_id}/status")
def get_quiz_status(quiz_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    is_expired = False
    time_remaining = 0
    elapsed_minutes = 0
    
    if quiz.countdown_started_at:
        total_quiz_time = quiz.duration_minutes * 60
        current_time = now()
        countdown_time = quiz.countdown_started_at
        
        elapsed_time = (current_time - countdown_time).total_seconds()
        time_remaining = max(0, total_quiz_time - elapsed_time)
        elapsed_minutes = int(elapsed_time / 60)
        is_expired = elapsed_time > total_quiz_time
    
    return {
        "quiz_id": quiz.id,
        "title": quiz.title,
        "is_active": quiz.is_active,
        "is_expired": is_expired,
        "duration_minutes": quiz.duration_minutes,
        "time_remaining_seconds": int(time_remaining),
        "elapsed_minutes": elapsed_minutes,
        "countdown_started_at": quiz.countdown_started_at,
        "can_rebroadcast": is_expired,
        "department": quiz.department,
        "level": quiz.level
    }

@app.get("/health")
def health_check():
    rwanda_time = now()
    return {
        "status": "healthy",
        "timestamp": rwanda_time.isoformat(),
        "rwanda_time": rwanda_time.strftime("%H:%M:%S"),
        "timezone": "CAT/EAT (UTC+2)",
        "service": "Morning Quiz API",

        "version": "2.0-ANTI-CHEAT-PROD",
        "cors": "enabled",
        "ai_grader": "enabled" if AI_GRADER_AVAILABLE else "fallback",
        "fix_deployed": "2026-01-13"

    }

@app.get("/auth/test")
def test_auth(current_user: User = Depends(get_current_user)):
    return {
        "message": "Authentication successful",
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "role": current_user.role,
            "full_name": current_user.full_name
        }
    }

@app.get("/notifications")
def get_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notifications = db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).all()
    return [{"id": n.id, "title": n.title, "message": n.message, "type": n.type, "is_read": n.is_read, "created_at": n.created_at.isoformat()} for n in notifications]

@app.get("/lessons")
def get_lessons(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    lessons = db.query(Lesson).filter(Lesson.is_active == True).all()
    return lessons

@app.post("/lessons")
def create_lesson(lesson: Dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Only teachers and admins can create lessons")
    
    new_lesson = Lesson(
        title=lesson['title'],
        code=lesson.get('code', lesson['title'][:10]),
        description=lesson.get('description', ''),
        department=lesson['department'],
        level=lesson['level'],
        classification=lesson.get('classification', 'General'),
        created_by=current_user.id
    )
    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)
    return {"id": new_lesson.id, "title": new_lesson.title, "code": new_lesson.code, "department": new_lesson.department, "level": new_lesson.level}

@app.get("/questions")
def get_questions(department: Optional[str] = None, level: Optional[str] = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can view questions")
    
    query = db.query(Question).filter(Question.created_by == current_user.id)
    
    if department:
        query = query.filter(Question.department == department)
    if level:
        query = query.filter(Question.level == level)
    
    questions = query.all()
    return questions

@app.post("/questions")
def create_question(question: QuestionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can create questions")
    
    new_question = Question(
        question_text=question.question_text,
        question_type=question.question_type,
        options=question.options,
        correct_answer=question.correct_answer,
        points=question.points,
        department=question.department,
        level=question.level,
        lesson_id=question.lesson_id,
        created_by=current_user.id
    )
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    return new_question

@app.post("/upload-questions")
async def upload_questions(
    file: UploadFile = File(...),
    department: Optional[str] = Form(None),
    level: Optional[str] = Form(None),
    lesson_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can upload questions")
    
    try:
        content = await file.read()
        filename = file.filename.lower()
        text = ""
        
        # Handle different file formats
        if filename.endswith('.pdf'):
            import PyPDF2
            import io
            pdf = PyPDF2.PdfReader(io.BytesIO(content))
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        elif filename.endswith('.doc') or filename.endswith('.docx'):
            try:
                import docx
                import io
                doc = docx.Document(io.BytesIO(content))
                for para in doc.paragraphs:
                    text += para.text + "\n"
            except:
                try:
                    text = content.decode('utf-8', errors='ignore')
                except:
                    text = content.decode('latin-1', errors='ignore')
        else:
            # Text files - try multiple encodings
            try:
                text = content.decode('utf-8')
            except:
                try:
                    text = content.decode('latin-1')
                except:
                    text = content.decode('cp1252', errors='ignore')
        
        # AI-Powered Intelligent Parser - handles ANY format
        questions = []
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        # Combine lines into paragraphs for better context
        paragraphs = []
        current_para = []
        for line in lines:
            if line:
                current_para.append(line)
            elif current_para:
                paragraphs.append(' '.join(current_para))
                current_para = []
        if current_para:
            paragraphs.append(' '.join(current_para))
        
        # AI Detection: Identify questions using multiple heuristics
        for para in paragraphs:
            # Method 1: Simple Q&A (Question? Answer)
            if '?' in para:
                parts = para.split('?')
                for i in range(len(parts) - 1):
                    question_text = parts[i].strip()
                    # Get last sentence as question
                    if '. ' in question_text:
                        question_text = question_text.split('. ')[-1]
                    question_text += '?'
                    
                    answer_text = parts[i + 1].strip()
                    # Take first sentence as answer
                    if '. ' in answer_text:
                        answer_text = answer_text.split('.')[0]
                    
                    if len(question_text) > 10 and answer_text:
                        questions.append({
                            'text': question_text,
                            'options': [answer_text, 'False', 'Not applicable', 'None of the above'],
                            'answer': answer_text
                        })
            
            # Method 2: Detect structured questions with options
            elif any(marker in para for marker in ['A)', 'B)', 'a)', 'b)', 'A.', 'B.']):
                # Extract question (everything before first option)
                question_text = para
                for marker in ['A)', 'a)', 'A.', 'a.', '(A)', '(a)']:
                    if marker in para:
                        question_text = para.split(marker)[0].strip()
                        break
                
                # Extract options
                options = []
                answer = ''
                
                # Try different option patterns
                for pattern in [r'[A-E]\)', r'[a-e]\)', r'[A-E]\.', r'\([A-E]\)']:
                    import re
                    matches = re.finditer(pattern, para)
                    temp_options = []
                    for match in matches:
                        start = match.end()
                        # Find next option or end
                        next_match = re.search(pattern, para[start:])
                        if next_match:
                            end = start + next_match.start()
                        else:
                            end = len(para)
                        option_text = para[start:end].strip()
                        # Remove answer markers
                        option_text = re.sub(r'(Answer:|Ans:|Correct:).*', '', option_text).strip()
                        if option_text:
                            temp_options.append(option_text)
                    
                    if len(temp_options) >= 2:
                        options = temp_options
                        break
                
                # Extract answer
                for prefix in ['Answer:', 'ANSWER:', 'Ans:', 'ANS:', 'Correct:', 'CORRECT:']:
                    if prefix in para:
                        answer = para.split(prefix)[1].strip().split()[0]
                        break
                
                if question_text and options:
                    questions.append({
                        'text': question_text,
                        'options': options,
                        'answer': answer if answer else options[0]
                    })
            
            # Method 3: Detect question keywords without ?
            else:
                question_keywords = ['what', 'who', 'where', 'when', 'why', 'how', 'which', 
                                   'define', 'explain', 'describe', 'list', 'name', 'identify']
                para_lower = para.lower()
                
                if any(para_lower.startswith(kw) for kw in question_keywords) and len(para) > 20:
                    # Split by common delimiters
                    if ':' in para:
                        parts = para.split(':', 1)
                        question_text = parts[0].strip()
                        answer_text = parts[1].strip()
                    elif '  ' in para:  # Double space
                        parts = para.split('  ', 1)
                        question_text = parts[0].strip()
                        answer_text = parts[1].strip()
                    else:
                        # Assume first 60% is question, rest is answer
                        split_point = int(len(para) * 0.6)
                        question_text = para[:split_point].strip()
                        answer_text = para[split_point:].strip()
                    
                    if len(question_text) > 10 and answer_text:
                        questions.append({
                            'text': question_text,
                            'options': [answer_text, 'False', 'Not applicable', 'None of the above'],
                            'answer': answer_text
                        })
        
        if not questions:
            return {
                "success": False, 
                "questions": [], 
                "count": 0,
                "debug_text": text[:500],
                "message": "No questions found. Please format as: '1. Question text? A) Option B) Option Answer: A'"
            }
        
        # Use teacher's first department if not provided
        if not department and current_user.departments:
            department = current_user.departments[0]
        if not level:
            level = "General"
        
        # Save questions to database
        created_count = 0
        for q in questions:
            if q.get('text') and q.get('options'):
                new_question = Question(
                    question_text=q['text'],
                    question_type='multiple_choice' if len(q['options']) > 1 else 'true_false',
                    options=q['options'],
                    correct_answer=q.get('answer', q['options'][0] if q['options'] else ''),
                    points=1,
                    department=department,
                    level=level,
                    lesson_id=lesson_id,
                    created_by=current_user.id
                )
                db.add(new_question)
                created_count += 1
        
        db.commit()
        
        return {"success": True, "questions": questions, "count": created_count, "created": created_count}
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Upload failed: {str(e)}")

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

@app.delete("/questions/{question_id}")
def delete_question(question_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can delete questions")
    
    question = db.query(Question).filter(Question.id == question_id, Question.created_by == current_user.id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    

    # Delete student answers first
    db.query(StudentAnswer).filter(StudentAnswer.question_id == question_id).delete(synchronize_session=False)
    # Remove question from quizzes
    db.query(QuizQuestion).filter(QuizQuestion.question_id == question_id).delete(synchronize_session=False)
    

    # Delete the question
    db.delete(question)
    db.commit()
    return {"message": "Question deleted successfully"}

@app.delete("/teacher/questions/clear")
def clear_all_teacher_questions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can clear questions")
    
    # Get all teacher's questions
    questions = db.query(Question).filter(Question.created_by == current_user.id).all()
    question_ids = [q.id for q in questions]
    

    # Delete student answers first
    db.query(StudentAnswer).filter(StudentAnswer.question_id.in_(question_ids)).delete(synchronize_session=False)
    # Remove questions from quizzes
    db.query(QuizQuestion).filter(QuizQuestion.question_id.in_(question_ids)).delete(synchronize_session=False)
    

    # Delete all questions
    deleted = db.query(Question).filter(Question.created_by == current_user.id).delete(synchronize_session=False)
    db.commit()
    return {"message": f"Successfully deleted {deleted} questions", "count": deleted}

@app.delete("/quizzes/{quiz_id}")
def delete_quiz(quiz_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can delete quizzes")
    
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.created_by == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Delete related records first
    db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz_id).delete(synchronize_session=False)
    db.query(StudentAnswer).filter(StudentAnswer.attempt_id.in_(
        db.query(QuizAttempt.id).filter(QuizAttempt.quiz_id == quiz_id)
    )).delete(synchronize_session=False)
    db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).delete(synchronize_session=False)
    
    # Delete quiz
    db.delete(quiz)
    db.commit()
    return {"message": "Quiz deleted successfully"}

@app.get("/quizzes/{quiz_id}/leaderboard")
def get_quiz_leaderboard(quiz_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    if current_user.role == "teacher" and quiz.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    attempts = db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).all()
    
    leaderboard = []
    for attempt in attempts:
        student = db.query(User).filter(User.id == attempt.user_id).first()
        if student:
            leaderboard.append({
                "student_name": student.full_name,
                "username": student.username,
                "score": attempt.score,
                "total": attempt.total_questions,
                "percentage": round((attempt.score / attempt.total_questions * 100) if attempt.total_questions > 0 else 0, 1),
                "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None
            })
    
    return sorted(leaderboard, key=lambda x: x["score"], reverse=True)

@app.get("/quizzes/{quiz_id}/export")
def export_quiz_results(quiz_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can export results")
    
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.created_by == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    attempts = db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).all()
    
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    import io
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#1a5490'), alignment=TA_CENTER, spaceAfter=12)
    subtitle_style = ParagraphStyle('CustomSubtitle', parent=styles['Normal'], fontSize=12, textColor=colors.HexColor('#666666'), alignment=TA_CENTER, spaceAfter=20)
    
    elements.append(Paragraph(f"Quiz Results: {quiz.title}", title_style))
    elements.append(Paragraph(f"{quiz.department} - {quiz.level}", subtitle_style))
    elements.append(Spacer(1, 0.2*inch))
    
    data = [['#', 'Student Name', 'Username', 'Score', 'Percentage']]

    for idx, attempt in enumerate(sorted(attempts, key=lambda x: (x.final_score if x.final_score is not None else x.score), reverse=True), 1):
        student = db.query(User).filter(User.id == attempt.user_id).first()
        if student:
            display_score = attempt.final_score if attempt.final_score is not None else attempt.score
            percentage = round((display_score / attempt.total_questions * 100) if attempt.total_questions > 0 else 0, 1)
            data.append([str(idx), student.full_name, student.username, f"{display_score}/{attempt.total_questions}", f"{percentage}%"])

    
    table = Table(data, colWidths=[0.5*inch, 2*inch, 1.5*inch, 1*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
    ]))
    
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=Quiz_Results_{quiz.title.replace(' ', '_')}.pdf"})

@app.get("/quizzes/{quiz_id}/export/excel")
def export_quiz_results_excel(quiz_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can export results")
    
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.created_by == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    attempts = db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).all()
    
    try:
        import pandas as pd
        import io
        
        # Prepare data for Excel
        data = []
        for idx, attempt in enumerate(sorted(attempts, key=lambda x: x.score, reverse=True), 1):
            student = db.query(User).filter(User.id == attempt.user_id).first()
            if student:
                percentage = round((attempt.score / attempt.total_questions * 100) if attempt.total_questions > 0 else 0, 1)
                data.append({
                    'Rank': idx,
                    'Student Name': student.full_name,
                    'Username': student.username,
                    'Score': f"{attempt.score}/{attempt.total_questions}",
                    'Percentage': f"{percentage}%",
                    'Completed At': attempt.completed_at.strftime('%Y-%m-%d %H:%M:%S') if attempt.completed_at else 'N/A'
                })
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Create Excel file in memory
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Quiz Results', index=False)
            
            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Quiz Results']
            
            # Add title rows
            worksheet.insert_rows(1, 2)
            worksheet['A1'] = f"Quiz Results: {quiz.title}"
            worksheet['A2'] = f"{quiz.department} - {quiz.level}"
            
            # Style the title
            from openpyxl.styles import Font, Alignment
            worksheet['A1'].font = Font(size=14, bold=True)
            worksheet['A1'].alignment = Alignment(horizontal='center')
            worksheet['A2'].font = Font(size=12)
            worksheet['A2'].alignment = Alignment(horizontal='center')
            
            # Merge cells for title
            worksheet.merge_cells('A1:F1')
            worksheet.merge_cells('A2:F2')
        
        buffer.seek(0)
        
        return StreamingResponse(
            buffer, 
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=Quiz_Results_{quiz.title.replace(' ', '_')}.xlsx"}
        )
    except ImportError:
        # Fallback to CSV if pandas/openpyxl not available
        import csv
        import io
        
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        
        # Write header
        writer.writerow([f"Quiz Results: {quiz.title}"])
        writer.writerow([f"{quiz.department} - {quiz.level}"])
        writer.writerow([])
        writer.writerow(['Rank', 'Student Name', 'Username', 'Score', 'Percentage', 'Completed At'])
        
        # Write data
        for idx, attempt in enumerate(sorted(attempts, key=lambda x: x.score, reverse=True), 1):
            student = db.query(User).filter(User.id == attempt.user_id).first()
            if student:
                percentage = round((attempt.score / attempt.total_questions * 100) if attempt.total_questions > 0 else 0, 1)
                writer.writerow([
                    idx,
                    student.full_name,
                    student.username,
                    f"{attempt.score}/{attempt.total_questions}",
                    f"{percentage}%",
                    attempt.completed_at.strftime('%Y-%m-%d %H:%M:%S') if attempt.completed_at else 'N/A'
                ])
        
        buffer.seek(0)
        return StreamingResponse(
            io.BytesIO(buffer.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=Quiz_Results_{quiz.title.replace(' ', '_')}.csv"}
        )

@app.get("/results/{quiz_id}")
def get_quiz_results(quiz_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can view results")
    
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.created_by == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    attempts = db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).all()
    
    results = []
    for attempt in attempts:
        student = db.query(User).filter(User.id == attempt.user_id).first()
        if student:

            # Use final_score (teacher-reviewed) if available, otherwise use initial score
            display_score = attempt.final_score if attempt.final_score is not None else attempt.score
            results.append({
                "student_name": student.full_name,
                "username": student.username,
                "score": display_score,
                "total": attempt.total_questions,
                "percentage": round((display_score / attempt.total_questions * 100) if attempt.total_questions > 0 else 0, 1),
                "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None
            })
    
    return {
        "quiz_title": quiz.title,
        "total_attempts": len(results),
        "results": sorted(results, key=lambda x: x["score"], reverse=True)
    }

@app.get("/schedules")
def get_schedules(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return []

@app.get("/announcements")
def get_announcements(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return []

@app.get("/teacher-lessons/{teacher_id}")
def get_teacher_lessons(teacher_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    assignments = db.query(TeacherLesson).filter(TeacherLesson.teacher_id == teacher_id).all()
    result = []
    for assignment in assignments:
        lesson = db.query(Lesson).filter(Lesson.id == assignment.lesson_id).first()
        if lesson:
            result.append({
                "id": assignment.id,
                "lesson": {
                    "id": lesson.id,
                    "title": lesson.title,
                    "code": lesson.code,
                    "department": lesson.department,
                    "level": lesson.level
                },
                "assigned_at": assignment.assigned_at.isoformat()
            })
    return result

@app.post("/teacher-lessons")
def assign_lesson_to_teacher(assignment: Dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can assign lessons")
    
    teacher_id = assignment['teacher_id']
    lesson_id = assignment['lesson_id']
    
    existing = db.query(TeacherLesson).filter(TeacherLesson.teacher_id == teacher_id, TeacherLesson.lesson_id == lesson_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Lesson already assigned to this teacher")
    
    teacher = db.query(User).filter(User.id == teacher_id).first()
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    
    if not teacher or not lesson:
        raise HTTPException(status_code=404, detail="Teacher or lesson not found")
    
    new_assignment = TeacherLesson(teacher_id=teacher_id, lesson_id=lesson_id)
    db.add(new_assignment)
    
    notification = Notification(
        user_id=teacher_id,
        title="New Module Assigned",
        message=f"You have been assigned to teach: {lesson.title} ({lesson.code})",
        type="assignment"
    )
    db.add(notification)
    
    db.commit()
    return {"message": "Lesson assigned successfully", "teacher_id": teacher_id, "lesson_id": lesson_id}

@app.get("/my-courses")
def get_my_courses(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can access courses")
    
    assignments = db.query(TeacherLesson).filter(TeacherLesson.teacher_id == current_user.id).all()
    result = []
    for assignment in assignments:
        lesson = db.query(Lesson).filter(Lesson.id == assignment.lesson_id).first()
        if lesson:
            result.append({
                "id": assignment.id,
                "lesson": {
                    "id": lesson.id,
                    "title": lesson.title,
                    "code": lesson.code,
                    "description": lesson.description,
                    "department": lesson.department,
                    "level": lesson.level,
                    "classification": lesson.classification
                },
                "assigned_at": assignment.assigned_at.isoformat()
            })
    return result

@app.post("/quizzes")
def create_quiz(quiz: QuizCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can create quizzes")
    
    new_quiz = Quiz(
        title=quiz.title,
        description=quiz.description,
        scheduled_time=quiz.scheduled_time,
        duration_minutes=quiz.duration_minutes,
        question_time_seconds=quiz.question_time_seconds,
        shuffle_questions=quiz.shuffle_questions,
        department=quiz.department,
        level=quiz.level,
        created_by=current_user.id
    )
    db.add(new_quiz)
    db.flush()
    
    # Add questions to quiz
    for i, question_id in enumerate(quiz.question_ids):
        quiz_question = QuizQuestion(
            quiz_id=new_quiz.id,
            question_id=question_id,
            question_order=i + 1
        )
        db.add(quiz_question)
    
    db.commit()
    return new_quiz

@app.put("/quizzes/{quiz_id}/broadcast")
def broadcast_quiz(quiz_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can broadcast quizzes")
    
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    if quiz.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You can only broadcast your own quizzes")
    
    # Get current Rwanda time for countdown
    rwanda_now = now()
    
    # Set quiz as active and start countdown
    quiz.is_active = True
    quiz.countdown_started_at = rwanda_now
    
    # Notify all students
    students = db.query(User).filter(
        User.role == "student",
        User.department == quiz.department,
        User.level == quiz.level
    ).all()
    
    students_notified = 0
    for student in students:
        notification = Notification(
            user_id=student.id,
            title=f"New Quiz Available: {quiz.title}",
            message=f"A new quiz '{quiz.title}' is now available. Duration: {quiz.duration_minutes} minutes. Start now!",
            type="quiz_available"
        )
        db.add(notification)
        students_notified += 1
    
    db.commit()
    db.refresh(quiz)
    
    return {
        "message": "Quiz broadcasted successfully",
        "quiz_id": quiz_id,
        "countdown_started_at": quiz.countdown_started_at.isoformat(),
        "server_rwanda_time": rwanda_now.strftime("%H:%M:%S"),
        "students_notified": students_notified
    }

@app.get("/admin/students")
def get_students(department: Optional[str] = None, level: Optional[str] = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(User).filter(User.role == "student")
    
    if department:
        query = query.filter(User.department == department)
    if level:
        query = query.filter(User.level == level)
    
    students = query.all()
    return {"students": [{"id": s.id, "username": s.username, "full_name": s.full_name, "department": s.department, "level": s.level} for s in students]}

@app.get("/teachers")
def get_teachers(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    teachers = db.query(User).filter(User.role == "teacher").all()
    return [{"id": t.id, "username": t.username, "full_name": t.full_name, "departments": t.departments} for t in teachers]

@app.options("/admin/clear-all-students")
async def clear_students_options():
    return {"message": "OK"}

@app.delete("/admin/clear-all-students")
def clear_all_students(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can clear students")
    
    try:
        # Get all student IDs
        student_ids = [s.id for s in db.query(User).filter(User.role == "student").all()]
        
        # Delete related records first
        db.query(Notification).filter(Notification.user_id.in_(student_ids)).delete(synchronize_session=False)
        db.query(StudentAnswer).filter(StudentAnswer.attempt_id.in_(
            db.query(QuizAttempt.id).filter(QuizAttempt.user_id.in_(student_ids))
        )).delete(synchronize_session=False)
        db.query(QuizAttempt).filter(QuizAttempt.user_id.in_(student_ids)).delete(synchronize_session=False)
        
        # Delete students
        deleted = db.query(User).filter(User.role == "student").delete(synchronize_session=False)
        db.commit()
        return {"message": f"Successfully deleted {deleted} students", "count": deleted}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to clear students: {str(e)}")

@app.post("/admin/upload-students-excel")
async def upload_students_excel(file: UploadFile = File(...), department: str = Form(...), level: str = Form(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can upload students")
    
    try:
        content = await file.read()
        filename = file.filename.lower()
        import pandas as pd
        import io
        import re
        
        if filename.endswith('.pdf'):
            import PyPDF2
            pdf = PyPDF2.PdfReader(io.BytesIO(content))
            created = 0
            seen = set()
            
            for page in pdf.pages:
                text = page.extract_text()
                for line in text.split('\n'):
                    line = line.strip()
                    if not line or len(line) < 3:
                        continue
                    if line.lower() in ['name', 'names', 'student', 's/n', 'district', 'sector', 'tss', 'kamonyi', 'runda']:
                        continue
                    if not re.search(r'[a-zA-Z]{3,}', line):
                        continue
                    if line.isdigit():
                        continue
                    
                    line = re.sub(r'^\d+\.?\s*', '', line)
                    if not line or len(line) < 3:
                        continue
                    
                    key = line.lower()
                    if key in seen:
                        continue
                    seen.add(key)
                    
                    # Generate username from name
                    name_parts = line.split()
                    if len(name_parts) >= 2:
                        username = (name_parts[0][:3] + name_parts[-1][:3]).lower() + str(secrets.randbelow(1000)).zfill(3)
                    else:
                        username = line[:6].lower() + str(secrets.randbelow(1000)).zfill(3)
                    
                    password = 'student123'
                    
                    student = User(
                        username=username,
                        password_hash=hash_password_simple(password),
                        role="student",
                        full_name=line,
                        department=department,
                        level=level
                    )
                    db.add(student)
                    created += 1
            
            db.commit()
            return {"success": True, "message": f"Successfully uploaded {created} students", "count": created, "created": created, "total": created, "updated": 0}
        
        # Excel files
        df = pd.read_excel(io.BytesIO(content), header=None, engine='xlrd' if filename.endswith('.xls') else 'openpyxl')
        
        name_col_idx = None
        start_row = None
        for idx, row in df.iterrows():
            for col_idx, cell in enumerate(row):
                if pd.notna(cell) and str(cell).strip().lower() == 'names':
                    name_col_idx = col_idx
                    start_row = idx + 1
                    break
            if start_row:
                break
        
        if not start_row:
            raise HTTPException(status_code=400, detail="Could not find 'Names' column in file")
        
        created = 0
        seen = set()
        for idx in range(start_row, len(df)):
            name = str(df.iloc[idx, name_col_idx]).strip()
            
            if name == 'nan' or not name or len(name) < 3:
                continue
            if not re.search(r'[a-zA-Z]{3,}', name):
                continue
            if name.isdigit():
                continue
            
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            
            # Generate username from name: first 3 letters of first name + first 3 of last name + random 3 digits
            name_parts = name.split()
            if len(name_parts) >= 2:
                username = (name_parts[0][:3] + name_parts[-1][:3]).lower() + str(secrets.randbelow(1000)).zfill(3)
            else:
                username = name[:6].lower() + str(secrets.randbelow(1000)).zfill(3)
            
            password = 'student123'
            
            student = User(
                username=username,
                password_hash=hash_password_simple(password),
                role="student",
                full_name=name,
                department=department,
                level=level
            )
            db.add(student)
            created += 1
        
        db.commit()
        return {"success": True, "message": f"Successfully uploaded {created} students", "count": created, "created": created, "total": created, "updated": 0}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Upload failed: {str(e)}")

@app.post("/admin/register-teacher")
def register_teacher(teacher_data: UserCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can register teachers")
    
    existing = db.query(User).filter(User.username == teacher_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    teacher = User(
        username=teacher_data.username,
        password_hash=hash_password_simple(teacher_data.password),
        role="teacher",
        full_name=teacher_data.full_name,
        departments=teacher_data.departments
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    
    return {"teacher": {"id": teacher.id, "username": teacher.username, "full_name": teacher.full_name, "departments": teacher.departments}}

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
    
    # Check if results are released
    if not quiz.results_released:
        raise HTTPException(status_code=403, detail="Results not yet released by teacher. Please wait for teacher to review and release results.")
    
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

@app.post("/admin/generate-student-credentials/{department}/{level}")
async def generate_student_credentials(department: str, level: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can generate credentials")
    
    students = db.query(User).filter(User.role == "student", User.department == department, User.level == level).all()
    
    if not students:
        raise HTTPException(status_code=404, detail=f"No students found for {department} - {level}")
    
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    import io
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#1a5490'), alignment=TA_CENTER, spaceAfter=12)
    subtitle_style = ParagraphStyle('CustomSubtitle', parent=styles['Normal'], fontSize=12, textColor=colors.HexColor('#666666'), alignment=TA_CENTER, spaceAfter=20)
    
    elements.append(Paragraph(f"Student Login Credentials", title_style))
    elements.append(Paragraph(f"{department} - {level}", subtitle_style))
    elements.append(Spacer(1, 0.2*inch))
    
    data = [['#', 'Full Name', 'Username', 'Password']]
    for idx, student in enumerate(students, 1):
        data.append([str(idx), student.full_name, student.username, 'student123'])
    
    table = Table(data, colWidths=[0.5*inch, 2.5*inch, 2*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
    ]))
    
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=Student_Credentials_{department.replace(' ', '_')}_{level.replace(' ', '_')}.pdf"})

# Create tables
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
except Exception as e:
    print(f"Database error: {e}")
    raise

# Initialize database

@app.post("/report-cheating")
def report_cheating(data: Dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Report student cheating attempt to teacher"""
    try:
        quiz_id = data.get('quiz_id')
        warnings = data.get('warnings', 0)
        reason = data.get('reason', 'Unknown')
        auto_submitted = data.get('auto_submitted', False)
        
        print(f"🚨 CHEATING REPORT: quiz_id={quiz_id}, warnings={warnings}, auto_submitted={auto_submitted}, student={current_user.full_name}")
        
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not quiz:
            print(f"❌ Quiz {quiz_id} not found")
            return {"message": "Quiz not found"}
        
        teacher = db.query(User).filter(User.id == quiz.created_by).first()
        if not teacher:
            print(f"❌ Teacher not found for quiz {quiz_id}")
            return {"message": "Teacher not found"}
        
        print(f"📧 Sending notifications to teacher {teacher.full_name} (ID: {teacher.id})")
        
        # Send cheating alert
        notification = Notification(
            user_id=teacher.id,
            title=f"⚠️ Cheating Alert: {quiz.title}",
            message=f"{current_user.full_name} was caught attempting to cheat ({warnings} violations). Reason: {reason}. Quiz was auto-submitted.",
            type="cheating_alert"
        )
        db.add(notification)
        print(f"✅ Cheating alert notification created")
        
        # If auto-submitted, send separate submission notification
        if auto_submitted:
            # Get the attempt to show score
            attempt = db.query(QuizAttempt).filter(
                QuizAttempt.quiz_id == quiz_id,
                QuizAttempt.user_id == current_user.id
            ).first()
            
            score_text = f"Score: {attempt.score}/{attempt.total_questions}" if attempt else "Score pending"
            
            submission_notification = Notification(
                user_id=teacher.id,
                title=f"📝 Auto-Submitted Quiz: {quiz.title}",
                message=f"{current_user.full_name}'s quiz was automatically submitted due to cheating violations ({warnings} strikes). Reason: {reason}. {score_text}. Click to review.",
                type="quiz_submission"
            )
            db.add(submission_notification)
            print(f"✅ Auto-submission notification created")
        
        db.commit()
        print(f"✅ Notifications committed to database")
        
        return {"message": "Cheating reported to teacher", "success": True}
    except Exception as e:
        print(f"❌ Error reporting cheating: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return {"message": f"Failed to report: {str(e)}", "success": False}

@app.get("/teacher/quiz-submissions/{quiz_id}")
def get_quiz_submissions(quiz_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all submissions for a quiz for teacher review"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can view submissions")
    
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.created_by == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    attempts = db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).all()
    
    submissions = []
    for attempt in attempts:
        student = db.query(User).filter(User.id == attempt.user_id).first()
        if student:
            display_score = attempt.final_score if attempt.final_score is not None else attempt.score
            submissions.append({
                "attempt_id": attempt.id,
                "student_id": student.id,
                "student_name": student.full_name,
                "student_username": student.username,
                "final_score": display_score,
                "total_possible": attempt.total_questions,
                "percentage": round((display_score / attempt.total_questions * 100) if attempt.total_questions > 0 else 0, 1),
                "needs_review": attempt.needs_review,
                "teacher_reviewed": attempt.final_score is not None,
                "submitted_at": attempt.completed_at.isoformat() if attempt.completed_at else None
            })
    
    return {
        "quiz_id": quiz.id,
        "quiz_title": quiz.title,
        "results_released": quiz.results_released,
        "submissions": sorted(submissions, key=lambda x: x["submitted_at"] or "", reverse=True)
    }

@app.get("/teacher/review-submission/{attempt_id}")
def get_submission_details(attempt_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get detailed submission for teacher review"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can review submissions")
    
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id, Quiz.created_by == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=403, detail="Access denied")
    
    student = db.query(User).filter(User.id == attempt.user_id).first()
    student_answers = db.query(StudentAnswer).filter(StudentAnswer.attempt_id == attempt_id).all()
    
    answers_detail = []
    for sa in student_answers:
        question = db.query(Question).filter(Question.id == sa.question_id).first()
        if question:
            answers_detail.append({
                "answer_id": sa.id,
                "question_id": question.id,
                "question_text": question.question_text,
                "question_type": question.question_type,
                "correct_answer": question.correct_answer,
                "max_points": question.points,
                "student_answer": sa.student_answer,
                "is_correct": sa.is_correct,
                "points_earned": sa.points_earned,
                "ai_feedback": sa.ai_feedback,
                "teacher_score": sa.teacher_score,
                "teacher_feedback": sa.teacher_feedback
            })
    
    return {
        "attempt_id": attempt.id,
        "quiz_title": quiz.title,
        "student_name": student.full_name if student else "Unknown",
        "student_username": student.username if student else "Unknown",
        "initial_score": attempt.score,
        "final_score": attempt.final_score,
        "total_questions": attempt.total_questions,
        "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None,
        "answers": answers_detail
    }

@app.post("/teacher/grade-answer/{answer_id}")
def grade_answer(answer_id: int, data: Dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Teacher grades individual answer"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can grade answers")
    
    student_answer = db.query(StudentAnswer).filter(StudentAnswer.id == answer_id).first()
    if not student_answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == student_answer.attempt_id).first()
    quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id, Quiz.created_by == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=403, detail="Access denied")
    
    student_answer.teacher_score = data.get('score')
    student_answer.teacher_feedback = data.get('feedback', '')
    
    # Recalculate final score
    all_answers = db.query(StudentAnswer).filter(StudentAnswer.attempt_id == attempt.id).all()
    final_score = sum(a.teacher_score if a.teacher_score is not None else a.points_earned for a in all_answers)
    attempt.final_score = final_score
    attempt.reviewed_by = current_user.id
    
    db.commit()
    
    return {"message": "Answer graded successfully", "final_score": final_score}

@app.post("/teacher/release-results/{quiz_id}")
def release_results(quiz_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Teacher releases quiz results to students"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can release results")
    
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.created_by == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    quiz.results_released = True
    db.commit()
    
    # Notify all students
    attempts = db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).all()
    for attempt in attempts:
        student = db.query(User).filter(User.id == attempt.user_id).first()
        if student:
            display_score = attempt.final_score if attempt.final_score is not None else attempt.score
            notification = Notification(
                user_id=student.id,
                title=f"✅ Results Released: {quiz.title}",
                message=f"Your quiz results are now available. Score: {display_score}/{attempt.total_questions}. Download your report now!",
                type="results_released"
            )
            db.add(notification)
    
    db.commit()
    
    return {"message": "Results released successfully", "students_notified": len(attempts)}

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    
    # Add missing columns via raw SQL
    db = SessionLocal()
    try:
        from sqlalchemy import text
        db.execute(text("ALTER TABLE quizzes ADD COLUMN IF NOT EXISTS results_released BOOLEAN DEFAULT FALSE"))
        db.execute(text("ALTER TABLE quiz_attempts ADD COLUMN IF NOT EXISTS needs_review BOOLEAN DEFAULT FALSE"))
        db.execute(text("ALTER TABLE quiz_attempts ADD COLUMN IF NOT EXISTS reviewed_by INTEGER"))
        db.execute(text("ALTER TABLE quiz_attempts ADD COLUMN IF NOT EXISTS final_score FLOAT"))
        db.execute(text("ALTER TABLE student_answers ADD COLUMN IF NOT EXISTS teacher_score FLOAT"))
        db.execute(text("ALTER TABLE student_answers ADD COLUMN IF NOT EXISTS teacher_feedback TEXT"))
        db.commit()
        print("✅ Database migration complete")
    except Exception as e:
        print(f"Migration error (may be normal if columns exist): {e}")
        db.rollback()
    
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                password_hash=hash_password_simple("admin123"),
                role="admin",
                full_name="DOS Administrator",
                departments=["Software Development", "Computer System and Architecture"]
            )
            db.add(admin)
            db.commit()
            print("Admin user created")
        
        teacher = db.query(User).filter(User.username == "teacher001").first()
        if not teacher:
            teacher = User(
                username="teacher001",
                password_hash=hash_password_simple("teacher123"),
                role="teacher",
                full_name="Teacher One",
                departments=["Software Development"]
            )
            db.add(teacher)
            db.commit()
            print("Default teacher user created")
        
        student = db.query(User).filter(User.username == "student001").first()
        if not student:
            student = User(
                username="student001",
                password_hash=hash_password_simple("pass123"),
                role="student",
                full_name="Student One",
                department="Software Development",
                level="Level 5"
            )
            db.add(student)
            db.commit()
            print("Default student user created")
    except Exception as e:
        print(f"Startup error: {e}")
        db.rollback()
    finally:

        db.close()


