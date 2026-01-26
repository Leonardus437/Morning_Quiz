from fastapi import FastAPI, Depends, HTTPException, status, Request, File, UploadFile, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
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
    print("[OK] AI Grader loaded successfully")
except Exception as e:
    AI_GRADER_AVAILABLE = False
    print(f"[WARNING] AI Grader not available: {e}")
    
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

def parse_advanced_question(text):
    """Parse question text and detect advanced question types"""
    import re
    
    text = text.strip()
    if len(text) < 10:
        return None
    
    # Initialize result
    result = {
        'text': '',
        'type': 'multiple_choice',
        'options': [],
        'answer': ''
    }
    
    # Detect question type patterns
    if re.search(r'\b(true|false)\b', text, re.IGNORECASE) and re.search(r'\?', text):
        result['type'] = 'true_false'
        result['text'] = re.split(r'\s*answer\s*:', text, flags=re.IGNORECASE)[0].strip()
        answer_match = re.search(r'answer\s*:\s*(true|false)', text, re.IGNORECASE)
        result['answer'] = answer_match.group(1).lower() if answer_match else 'true'
        result['options'] = ['True', 'False']
        
    elif re.search(r'select all|choose all|multiple correct', text, re.IGNORECASE):
        result['type'] = 'multiple_select'
        parts = re.split(r'\s*answer\s*:', text, flags=re.IGNORECASE)
        result['text'] = parts[0].strip()
        if len(parts) > 1:
            result['answer'] = parts[1].strip()
        # Extract options
        options = re.findall(r'[A-Z]\)\s*([^A-Z\)]+)', result['text'])
        result['options'] = [opt.strip() for opt in options]
        
    elif re.search(r'fill.{0,10}blank|complete.{0,10}sentence', text, re.IGNORECASE):
        result['type'] = 'fill_blanks'
        parts = re.split(r'\s*answer\s*:', text, flags=re.IGNORECASE)
        result['text'] = parts[0].strip()
        if len(parts) > 1:
            result['answer'] = parts[1].strip()
            
    elif re.search(r'match|pair|connect', text, re.IGNORECASE):
        result['type'] = 'drag_drop_match'
        parts = re.split(r'\s*answer\s*:', text, flags=re.IGNORECASE)
        result['text'] = parts[0].strip()
        if len(parts) > 1:
            result['answer'] = parts[1].strip()
            
    elif re.search(r'order|arrange|sequence|sort', text, re.IGNORECASE):
        result['type'] = 'drag_drop_order'
        parts = re.split(r'\s*answer\s*:', text, flags=re.IGNORECASE)
        result['text'] = parts[0].strip()
        if len(parts) > 1:
            result['answer'] = parts[1].strip()
            
    elif re.search(r'rate|scale|1.{0,5}10|rating', text, re.IGNORECASE):
        result['type'] = 'linear_scale'
        parts = re.split(r'\s*answer\s*:', text, flags=re.IGNORECASE)
        result['text'] = parts[0].strip()
        result['answer'] = '5'  # Default middle rating
        
    elif re.search(r'code|program|function|algorithm|python|java|javascript', text, re.IGNORECASE):
        result['type'] = 'code_writing'
        parts = re.split(r'\s*answer\s*:', text, flags=re.IGNORECASE)
        result['text'] = parts[0].strip()
        if len(parts) > 1:
            result['answer'] = parts[1].strip()
            
    elif re.search(r'sql|query|database|select|insert|update|delete', text, re.IGNORECASE):
        result['type'] = 'sql_query'
        parts = re.split(r'\s*answer\s*:', text, flags=re.IGNORECASE)
        result['text'] = parts[0].strip()
        if len(parts) > 1:
            result['answer'] = parts[1].strip()
            
    elif re.search(r'dropdown|select from', text, re.IGNORECASE):
        result['type'] = 'dropdown_select'
        parts = re.split(r'\s*answer\s*:', text, flags=re.IGNORECASE)
        result['text'] = parts[0].strip()
        if len(parts) > 1:
            result['answer'] = parts[1].strip()
        # Extract options
        options = re.findall(r'[A-Z]\)\s*([^A-Z\)]+)', result['text'])
        result['options'] = [opt.strip() for opt in options]
        
    elif re.search(r'short answer|brief|explain briefly', text, re.IGNORECASE):
        result['type'] = 'short_answer'
        parts = re.split(r'\s*answer\s*:', text, flags=re.IGNORECASE)
        result['text'] = parts[0].strip()
        if len(parts) > 1:
            result['answer'] = parts[1].strip()
            
    elif re.search(r'essay|discuss|elaborate|explain in detail', text, re.IGNORECASE):
        result['type'] = 'essay'
        parts = re.split(r'\s*answer\s*:', text, flags=re.IGNORECASE)
        result['text'] = parts[0].strip()
        if len(parts) > 1:
            result['answer'] = parts[1].strip()
            
    else:
        # Default to multiple choice
        result['type'] = 'multiple_choice'
        parts = re.split(r'\s*answer\s*:', text, flags=re.IGNORECASE)
        result['text'] = parts[0].strip()
        
        # Extract options (A) B) C) D) format
        options = re.findall(r'[A-Z]\)\s*([^A-Z\)]+)', result['text'])
        if options:
            result['options'] = [opt.strip() for opt in options]
            # Extract answer
            if len(parts) > 1:
                answer_text = parts[1].strip()
                # Look for single letter answer
                answer_match = re.search(r'\b([A-Z])\b', answer_text)
                result['answer'] = answer_match.group(1) if answer_match else 'A'
            else:
                result['answer'] = 'A'
        else:
            # No options found, might be short answer
            result['type'] = 'short_answer'
            if len(parts) > 1:
                result['answer'] = parts[1].strip()
    
    # Clean up text - remove options from question text for MCQ
    if result['type'] in ['multiple_choice', 'dropdown_select', 'multiple_select']:
        # Remove options from question text
        clean_text = re.sub(r'\s*[A-Z]\)\s*[^A-Z\)]+', '', result['text'])
        result['text'] = clean_text.strip()
    
    return result if result['text'] else None



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

# Mount static files for uploads
import os
os.makedirs("uploads/chat", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# CRITICAL: Add CORS middleware BEFORE any routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    
    # Advanced question type fields
    question_config = Column(JSON)  # Stores type-specific config
    media_url = Column(String)  # For image/audio/video questions
    correct_answers = Column(JSON)  # For multiple correct answers
    partial_credit = Column(Boolean, default=False)

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
    percentage = Column(Float, default=0.0)
    grade = Column(String(5), default='F')
    total_possible_points = Column(Float, default=0.0)

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

class ClassTeacher(Base):
    __tablename__ = "class_teachers"
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    department = Column(String(100))
    level = Column(String(50))
    assigned_at = Column(DateTime, default=datetime.utcnow)

class ChatRoom(Base):
    __tablename__ = "chat_rooms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    room_type = Column(String(50))  # student-student, student-teacher, teacher-teacher, teacher-dos
    department = Column(String(100))
    level = Column(String(50))
    module_id = Column(Integer, ForeignKey("lessons.id"))
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text)
    message_type = Column(String(20), default="text")  # text, link, file
    file_url = Column(String)
    file_name = Column(String)
    reply_to_id = Column(Integer, ForeignKey("chat_messages.id"))
    is_deleted = Column(Boolean, default=False)
    is_flagged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class MessageReaction(Base):
    __tablename__ = "message_reactions"
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("chat_messages.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    emoji = Column(String(10))
    created_at = Column(DateTime, default=datetime.utcnow)

class ChatParticipant(Base):
    __tablename__ = "chat_participants"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    is_blocked = Column(Boolean, default=False)  # DOS can block users
    joined_at = Column(DateTime, default=datetime.utcnow)

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
    question_config: Optional[Dict] = None
    media_url: Optional[str] = None
    correct_answers: Optional[List[str]] = None
    partial_credit: Optional[bool] = False

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
    print(f"📥 SUBMIT REQUEST: quiz_id={submission.quiz_id}, user={current_user.username}, answers_count={len(submission.answers)}")
    
    quiz = db.query(Quiz).filter(Quiz.id == submission.quiz_id).first()
    if not quiz:
        print(f"❌ Quiz {submission.quiz_id} not found")
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    print(f"✅ Quiz found: {quiz.title}")
    
    existing = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == submission.quiz_id,
        QuizAttempt.user_id == current_user.id
    ).first()
    if existing:
        print(f"❌ Quiz already submitted by user {current_user.username}")
        raise HTTPException(status_code=400, detail="Quiz already submitted")
    
    print(f"✅ No existing attempt found, proceeding with submission")
    
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
    
    print(f"✅ Attempt created with ID: {attempt.id}")
    
    for answer in submission.answers:
        question = db.query(Question).filter(Question.id == answer.question_id).first()
        if not question:
            continue
        
        is_correct = False
        points = 0.0
        feedback = ""
        
        # Grade based on question type
        if question.question_type in ['short_answer', 'essay']:
            points, feedback = grade_open_ended_question(
                answer.answer, question.correct_answer, question.points
            )
            needs_review = True
        elif question.question_type == 'multiple_select':
            # Multiple correct answers
            student_answers = set(str(answer.answer).split(',')) if answer.answer else set()
            correct_answers = set(question.correct_answers or [])
            if student_answers == correct_answers:
                is_correct = True
                points = float(question.points)
            elif question.partial_credit and student_answers & correct_answers:
                # Partial credit: (correct selections / total correct) * points
                points = float(question.points) * (len(student_answers & correct_answers) / len(correct_answers))
            else:
                points = 0.0
            feedback = "Correct" if is_correct else f"Partial credit: {points:.1f}/{question.points}"
        elif question.question_type == 'fill_blanks':
            # Fill in the blanks
            config = question.question_config or {}
            blanks = config.get('blanks', [])
            student_blanks = str(answer.answer).split('|||') if answer.answer else []
            correct_count = 0
            for i, blank in enumerate(blanks):
                if i < len(student_blanks):
                    if str(student_blanks[i]).strip().lower() == str(blank.get('answer', '')).strip().lower():
                        correct_count += 1
            points = float(question.points) * (correct_count / len(blanks)) if blanks else 0.0
            is_correct = correct_count == len(blanks)
            feedback = f"Correct: {correct_count}/{len(blanks)} blanks"
        elif question.question_type == 'drag_drop_match':
            # Matching pairs
            config = question.question_config or {}
            pairs = config.get('pairs', [])
            student_pairs = str(answer.answer).split('|||') if answer.answer else []
            correct_count = sum(1 for i, pair in enumerate(pairs) if i < len(student_pairs) and student_pairs[i] == pair.get('right'))
            points = float(question.points) * (correct_count / len(pairs)) if pairs else 0.0
            is_correct = correct_count == len(pairs)
            feedback = f"Correct: {correct_count}/{len(pairs)} matches"
        elif question.question_type == 'drag_drop_order':
            # Ordering
            config = question.question_config or {}
            correct_order = config.get('correct_order', [])
            try:
                student_order = [int(x) for x in str(answer.answer).split(',')] if answer.answer else []
            except (ValueError, AttributeError):
                student_order = []
            is_correct = student_order == correct_order
            points = float(question.points) if is_correct else 0.0
            feedback = "Correct order" if is_correct else "Incorrect order"
        elif question.question_type == 'code_writing':
            # Code questions need manual review
            needs_review = True
            points = 0
            feedback = "Pending teacher review"
        elif question.question_type == 'sql_query':
            # SQL questions need manual review
            needs_review = True
            points = 0
            feedback = "Pending teacher review"
        elif question.question_type == 'multi_grid':
            # Multi-Grid questions - matrix of radio buttons
            config = question.question_config or {}
            rows = config.get('rows', [])
            columns = config.get('columns', [])
            correct_answers = config.get('correct_answers', {})
            
            try:
                student_answers = json.loads(answer.answer) if answer.answer else {}
            except (json.JSONDecodeError, TypeError):
                student_answers = {}
            
            correct_count = 0
            total_rows = len(rows)
            
            for row_id in rows:
                if str(row_id) in student_answers and str(row_id) in correct_answers:
                    if student_answers[str(row_id)] == correct_answers[str(row_id)]:
                        correct_count += 1
            
            points = float(question.points) * (correct_count / total_rows) if total_rows > 0 else 0.0
            is_correct = correct_count == total_rows
            feedback = f"Correct: {correct_count}/{total_rows} rows"
        else:
            # Standard MCQ, True/False, Dropdown - Case insensitive comparison
            student_answer_clean = str(answer.answer).strip().lower()
            correct_answer_clean = str(question.correct_answer).strip().lower()
            is_correct = student_answer_clean == correct_answer_clean
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
    
    # Calculate total possible points for this quiz
    all_questions = db.query(Question).join(QuizQuestion).filter(
        QuizQuestion.quiz_id == submission.quiz_id
    ).all()
    total_possible_points = sum(q.points for q in all_questions)
    
    # Ensure score doesn't exceed total possible points
    final_score = min(float(score), float(total_possible_points))
    
    # Calculate percentage and grade
    percentage = (final_score / total_possible_points * 100) if total_possible_points > 0 else 0
    percentage = min(percentage, 100.0)  # Cap at 100%
    
    # Grade mapping based on percentage (Rwanda grading system)
    if percentage >= 90:
        grade = 'A+'
    elif percentage >= 80:
        grade = 'A'
    elif percentage >= 70:
        grade = 'B'
    elif percentage >= 60:
        grade = 'C'
    elif percentage >= 50:
        grade = 'D'
    else:
        grade = 'F'
    
    attempt.score = final_score
    attempt.needs_review = needs_review
    attempt.percentage = round(percentage, 1)
    attempt.grade = grade
    attempt.total_possible_points = total_possible_points
    
    print(f"✅ Grading complete: score={score}/{len(submission.answers)}, needs_review={needs_review}")
    
    try:
        db.commit()
        print(f"✅ Submission committed to database")
    except Exception as e:
        print(f"❌ Database commit failed: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save submission: {str(e)}")
    
    # Notify teacher about submission (no auto-submit reason here - manual submission)
    teacher = db.query(User).filter(User.id == quiz.created_by).first()
    if teacher:
        print(f"📧 Notifying teacher {teacher.full_name} (ID: {teacher.id})")
        notification = Notification(
            user_id=teacher.id,
            title=f"📝 New Quiz Submission: {quiz.title}",
            message=f"{current_user.full_name} has submitted the quiz. Score: {score}/{len(submission.answers)}. Click to review.",
            type="quiz_submission"
        )
        db.add(notification)
        try:
            db.commit()
            print(f"✅ Teacher notification sent")
        except Exception as e:
            print(f"❌ Failed to send teacher notification: {e}")
    else:
        print(f"⚠️ Teacher not found for quiz {quiz.id}")
    
    print(f"✅ SUBMISSION COMPLETE: attempt_id={attempt.id}, score={score}")
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
        "fix_deployed": "2026-01-26",
        "cors_fix": "active"

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

@app.put("/lessons/{lesson_id}")
def update_lesson(lesson_id: int, lesson: Dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can edit lessons")
    
    existing_lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not existing_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    existing_lesson.title = lesson.get('title', existing_lesson.title)
    existing_lesson.code = lesson.get('code', existing_lesson.code)
    existing_lesson.description = lesson.get('description', existing_lesson.description)
    existing_lesson.department = lesson.get('department', existing_lesson.department)
    existing_lesson.level = lesson.get('level', existing_lesson.level)
    existing_lesson.classification = lesson.get('classification', existing_lesson.classification)
    
    db.commit()
    db.refresh(existing_lesson)
    return {"id": existing_lesson.id, "title": existing_lesson.title, "code": existing_lesson.code, "department": existing_lesson.department, "level": existing_lesson.level}

@app.delete("/lessons/{lesson_id}")
def delete_lesson(lesson_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete lessons")
    
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Delete related records
    db.query(TeacherLesson).filter(TeacherLesson.lesson_id == lesson_id).delete(synchronize_session=False)
    db.query(Question).filter(Question.lesson_id == lesson_id).update({Question.lesson_id: None}, synchronize_session=False)
    
    db.delete(lesson)
    db.commit()
    return {"message": "Lesson deleted successfully"}

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
        created_by=current_user.id,
        question_config=question.question_config,
        media_url=question.media_url,
        correct_answers=question.correct_answers,
        partial_credit=question.partial_credit
    )
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    return new_question

@app.options("/upload-questions")
async def upload_questions_options():
    """Handle CORS preflight for upload-questions"""
    print("✅ OPTIONS /upload-questions called")
    return {"message": "OK"}

@app.get("/upload-test")
def upload_test(current_user: User = Depends(get_current_user)):
    """Test endpoint to verify authentication works"""
    print(f"✅ UPLOAD TEST: User {current_user.username} authenticated successfully")
    return {
        "message": "Upload endpoint is reachable",
        "user": current_user.username,
        "role": current_user.role
    }

@app.post("/upload-questions-simple")
async def upload_questions_simple(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Simplified upload endpoint for debugging"""
    import sys
    print("🚀 SIMPLE UPLOAD CALLED", file=sys.stderr)
    sys.stderr.flush()
    
    try:
        form = await request.form()
        print(f"📦 Form data: {dict(form)}", file=sys.stderr)
        sys.stderr.flush()
        
        file = form.get('file')
        if not file:
            return {"error": "No file provided"}
        
        content = await file.read()
        print(f"📄 File: {file.filename}, Size: {len(content)}", file=sys.stderr)
        sys.stderr.flush()
        
        return {
            "success": True,
            "filename": file.filename,
            "size": len(content),
            "message": "File received successfully"
        }
    except Exception as e:
        import traceback
        print(f"❌ ERROR: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        sys.stderr.flush()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-questions")
async def upload_questions(
    file: UploadFile = File(...),
    department: Optional[str] = Form(None),
    level: Optional[str] = Form(None),
    lesson_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    import traceback
    import sys
    
    print("="*80, file=sys.stderr)
    print("🚀 UPLOAD ENDPOINT CALLED!", file=sys.stderr)
    print(f"User: {current_user.username}, Role: {current_user.role}", file=sys.stderr)
    print(f"File: {file.filename if file else 'NO FILE'}", file=sys.stderr)
    print(f"Department: {department}, Level: {level}", file=sys.stderr)
    print("="*80, file=sys.stderr)
    sys.stderr.flush()
    
    try:
        if current_user.role != "teacher":
            print(f"❌ REJECTED: User is {current_user.role}, not teacher", file=sys.stderr)
            sys.stderr.flush()
            raise HTTPException(status_code=403, detail="Only teachers can upload questions")
        
        print(f"📁 Upload request: file={file.filename}, dept={department}, level={level}", file=sys.stderr)
        sys.stderr.flush()
        
        content = await file.read()
        filename = file.filename.lower() if file.filename else "unknown.txt"
        text = ""
        
        print(f"📄 Processing file: {filename}, size: {len(content)} bytes")
        
        # Handle different file formats
        if filename.endswith('.pdf'):
            try:
                import PyPDF2
                import io
                pdf = PyPDF2.PdfReader(io.BytesIO(content))
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
                print(f"✅ PDF processed, extracted {len(text)} characters")
            except Exception as e:
                print(f"❌ PDF processing failed: {e}")
                raise HTTPException(status_code=400, detail=f"PDF processing failed: {str(e)}")
                
        elif filename.endswith('.doc') or filename.endswith('.docx'):
            try:
                import docx
                import io
                doc = docx.Document(io.BytesIO(content))
                for para in doc.paragraphs:
                    text += para.text + "\n"
                print(f"✅ Word document processed, extracted {len(text)} characters")
            except Exception as e:
                print(f"⚠️ Word processing failed, trying text fallback: {e}")
                try:
                    text = content.decode('utf-8', errors='ignore')
                except:
                    text = content.decode('latin-1', errors='ignore')
        else:
            # Text files - try multiple encodings
            try:
                text = content.decode('utf-8')
                print(f"✅ Text file processed with UTF-8")
            except:
                try:
                    text = content.decode('latin-1')
                    print(f"✅ Text file processed with Latin-1")
                except:
                    text = content.decode('cp1252', errors='ignore')
                    print(f"✅ Text file processed with CP1252")
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text content found in file")
        
        print(f"📝 Text extracted: {len(text)} characters")
        
        # Enhanced AI Parser - handles ALL 12 advanced question types
        questions = []
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        # Join all lines for better parsing
        full_text = ' '.join(lines)
        
        # Split by question numbers (1., 2., etc.)
        import re
        question_blocks = re.split(r'\b(\d+)\s*[.):]\s*', full_text)
        
        print(f"🔍 Found {len(question_blocks)} text blocks")
        
        # Process each question block
        for i in range(1, len(question_blocks), 2):
            if i + 1 < len(question_blocks):
                question_num = question_blocks[i]
                question_content = question_blocks[i + 1].strip()
                
                if len(question_content) < 10:  # Skip very short content
                    continue
                
                print(f"📋 Processing question {question_num}: {question_content[:50]}...")
                
                # Parse different question types
                try:
                    parsed_question = parse_advanced_question(question_content)
                    if parsed_question:
                        questions.append(parsed_question)
                        print(f"✅ Parsed as {parsed_question['type']}")
                    else:
                        print(f"⚠️ Could not parse question {question_num}")
                except Exception as e:
                    print(f"❌ Error parsing question {question_num}: {e}")
        
        # Fallback: If no numbered questions found, try paragraph-based parsing
        if not questions:
            print("🔄 No numbered questions found, trying paragraph parsing")
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
            
            for para in paragraphs:
                try:
                    parsed_question = parse_advanced_question(para)
                    if parsed_question:
                        questions.append(parsed_question)
                        print(f"✅ Parsed paragraph as {parsed_question['type']}")
                except Exception as e:
                    print(f"❌ Error parsing paragraph: {e}")
        
        if not questions:
            return {
                "success": False, 
                "questions": [], 
                "count": 0,
                "debug_text": text[:500],
                "message": "No questions found. Please format as: '1. Question text? A) Option B) Option Answer: A'"
            }
        
        print(f"📊 Successfully parsed {len(questions)} questions")
        
        # Use teacher's first department if not provided
        if not department and current_user.departments:
            department = current_user.departments[0]
        if not level:
            level = "General"
        
        print(f"💾 Saving to database: dept={department}, level={level}")
        
        # Save questions to database with proper advanced types
        created_count = 0
        for q in questions:
            if q.get('text'):
                try:
                    question_type = q.get('type', 'multiple_choice')
                    
                    # Map question types to database format
                    type_mapping = {
                        'multiple_choice': 'multiple_choice',
                        'true_false': 'true_false', 
                        'multiple_select': 'multiple_select',
                        'fill_blanks': 'fill_blanks',
                        'drag_drop_match': 'drag_drop_match',
                        'drag_drop_order': 'drag_drop_order',
                        'linear_scale': 'linear_scale',
                        'code_writing': 'code_writing',
                        'sql_query': 'sql_query',
                        'multi_grid': 'multi_grid',
                        'dropdown_select': 'dropdown_select',
                        'short_answer': 'short_answer',
                        'essay': 'essay'
                    }
                    
                    db_question_type = type_mapping.get(question_type, 'multiple_choice')
                    
                    # Set up question config for advanced types
                    question_config = None
                    correct_answers = None
                    partial_credit = False
                    
                    if question_type == 'multiple_select':
                        correct_answers = q.get('answer', 'A,B').split(',')
                        partial_credit = True
                    elif question_type == 'fill_blanks':
                        blanks = q.get('answer', 'answer1|||answer2').split('|||')
                        question_config = {
                            'blanks': [{'answer': blank} for blank in blanks]
                        }
                    elif question_type == 'drag_drop_match':
                        pairs = q.get('answer', 'Item1|||Item2|||Item3').split('|||')
                        question_config = {
                            'pairs': [{'left': f'Left {i+1}', 'right': pair} for i, pair in enumerate(pairs)]
                        }
                    elif question_type == 'drag_drop_order':
                        try:
                            order = [int(x) for x in q.get('answer', '1,2,3,4').split(',')]
                        except ValueError:
                            order = [1, 2, 3, 4]
                        question_config = {
                            'correct_order': order,
                            'items': [f'Item {i}' for i in order]
                        }
                    elif question_type == 'linear_scale':
                        question_config = {
                            'min_value': 1,
                            'max_value': 10,
                            'min_label': 'Poor',
                            'max_label': 'Excellent'
                        }
                    elif question_type == 'code_writing':
                        question_config = {
                            'language': 'python',
                            'starter_code': '# Write your code here\n'
                        }
                    elif question_type == 'sql_query':
                        question_config = {
                            'database_schema': 'CREATE TABLE users (id INT, name VARCHAR(50));'
                        }
                    elif question_type == 'multi_grid':
                        try:
                            import json
                            answers = json.loads(q.get('answer', '{}'))
                        except:
                            answers = {'Row1': 'Column1', 'Row2': 'Column2'}
                        
                        question_config = {
                            'rows': list(answers.keys()),
                            'columns': ['Column1', 'Column2', 'Column3'],
                            'correct_answers': answers
                        }
                    
                    new_question = Question(
                        question_text=q['text'],
                        question_type=db_question_type,
                        options=q.get('options', []),
                        correct_answer=q.get('answer', ''),
                        points=1,
                        department=department,
                        level=level,
                        lesson_id=lesson_id,
                        created_by=current_user.id,
                        question_config=question_config,
                        media_url=None,
                        correct_answers=correct_answers,
                        partial_credit=partial_credit
                    )
                    db.add(new_question)
                    created_count += 1
                    print(f"✅ Created question {created_count}: {db_question_type}")
                except Exception as e:
                    print(f"❌ Error creating question: {e}")
                    continue
        
        db.commit()
        print(f"🎉 Successfully saved {created_count} questions to database")
        
        return {
            "success": True, 
            "questions": [{
                'text': q.get('text', ''),
                'type': q.get('type', 'multiple_choice'),
                'options': q.get('options', []),
                'answer': q.get('answer', '')
            } for q in questions], 
            "count": created_count, 
            "created": created_count,
            "types_detected": list(set(q.get('type', 'multiple_choice') for q in questions))
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        import sys
        error_trace = traceback.format_exc()
        print(f"❌ UPLOAD ERROR: {e}", file=sys.stderr)
        print(f"📋 Full traceback:", file=sys.stderr)
        print(error_trace, file=sys.stderr)
        sys.stderr.flush()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

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
                "total": attempt.total_possible_points or attempt.total_questions,
                "percentage": attempt.percentage or round((attempt.score / (attempt.total_possible_points or attempt.total_questions) * 100) if (attempt.total_possible_points or attempt.total_questions) > 0 else 0, 1),
                "grade": attempt.grade or ('A+' if (attempt.percentage or 0) >= 90 else 'A' if (attempt.percentage or 0) >= 80 else 'B' if (attempt.percentage or 0) >= 70 else 'C' if (attempt.percentage or 0) >= 60 else 'D' if (attempt.percentage or 0) >= 50 else 'F'),
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
            total_possible = attempt.total_possible_points or attempt.total_questions
            percentage = attempt.percentage or round((display_score / total_possible * 100) if total_possible > 0 else 0, 1)
            grade = attempt.grade or ('A+' if percentage >= 90 else 'A' if percentage >= 80 else 'B' if percentage >= 70 else 'C' if percentage >= 60 else 'D' if percentage >= 50 else 'F')
            
            results.append({
                "student_name": student.full_name,
                "username": student.username,
                "score": display_score,
                "total": total_possible,
                "percentage": percentage,
                "grade": grade,
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
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view students")
    
    query = db.query(User).filter(User.role == "student")
    
    if department:
        query = query.filter(User.department == department)
    if level:
        query = query.filter(User.level == level)
    
    students = query.all()
    return {"students": [{"id": s.id, "username": s.username, "full_name": s.full_name, "department": s.department, "level": s.level} for s in students]}

@app.get("/teachers")
def get_teachers(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view teachers")
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
        print("🗑️ Starting clear all students operation...")
        
        # Get all student IDs
        student_ids = [s.id for s in db.query(User).filter(User.role == "student").all()]
        print(f"📊 Found {len(student_ids)} students to delete")
        
        if not student_ids:
            return {"message": "No students to delete", "count": 0}
        
        # Get all message IDs from students
        student_message_ids = [m.id for m in db.query(ChatMessage.id).filter(ChatMessage.sender_id.in_(student_ids)).all()]
        print(f"💬 Found {len(student_message_ids)} messages from students")
        
        # Delete message reactions (both reactions TO student messages and BY students)
        if student_message_ids:
            reactions_deleted = db.query(MessageReaction).filter(MessageReaction.message_id.in_(student_message_ids)).delete(synchronize_session=False)
            print(f"✅ Deleted {reactions_deleted} reactions to student messages")
        reactions_by_students = db.query(MessageReaction).filter(MessageReaction.user_id.in_(student_ids)).delete(synchronize_session=False)
        print(f"✅ Deleted {reactions_by_students} reactions by students")
        
        # Nullify reply_to_id for messages that reply to student messages
        if student_message_ids:
            replies_updated = db.query(ChatMessage).filter(ChatMessage.reply_to_id.in_(student_message_ids)).update({ChatMessage.reply_to_id: None}, synchronize_session=False)
            print(f"✅ Nullified {replies_updated} message replies")
        
        # Delete chat messages
        messages_deleted = db.query(ChatMessage).filter(ChatMessage.sender_id.in_(student_ids)).delete(synchronize_session=False)
        print(f"✅ Deleted {messages_deleted} chat messages")
        
        # Delete chat participants
        participants_deleted = db.query(ChatParticipant).filter(ChatParticipant.user_id.in_(student_ids)).delete(synchronize_session=False)
        print(f"✅ Deleted {participants_deleted} chat participants")
        
        # Nullify chat room creators (if any student created a room)
        rooms_updated = db.query(ChatRoom).filter(ChatRoom.created_by.in_(student_ids)).update({ChatRoom.created_by: None}, synchronize_session=False)
        print(f"✅ Nullified {rooms_updated} chat room creators")
        
        # Delete notifications
        notifications_deleted = db.query(Notification).filter(Notification.user_id.in_(student_ids)).delete(synchronize_session=False)
        print(f"✅ Deleted {notifications_deleted} notifications")
        
        # Nullify quiz_attempts.reviewed_by (if any student somehow reviewed)
        attempts_updated = db.query(QuizAttempt).filter(QuizAttempt.reviewed_by.in_(student_ids)).update({QuizAttempt.reviewed_by: None}, synchronize_session=False)
        print(f"✅ Nullified {attempts_updated} quiz attempt reviewers")
        
        # Delete student answers and quiz attempts
        answers_deleted = db.query(StudentAnswer).filter(StudentAnswer.attempt_id.in_(
            db.query(QuizAttempt.id).filter(QuizAttempt.user_id.in_(student_ids))
        )).delete(synchronize_session=False)
        print(f"✅ Deleted {answers_deleted} student answers")
        
        attempts_deleted = db.query(QuizAttempt).filter(QuizAttempt.user_id.in_(student_ids)).delete(synchronize_session=False)
        print(f"✅ Deleted {attempts_deleted} quiz attempts")
        
        # Finally, delete students
        deleted = db.query(User).filter(User.role == "student").delete(synchronize_session=False)
        print(f"✅ Deleted {deleted} students")
        
        db.commit()
        print(f"🎉 Successfully cleared all students!")
        return {"message": f"Successfully deleted {deleted} students", "count": deleted}
    except Exception as e:
        print(f"❌ ERROR clearing students: {str(e)}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
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

@app.post("/admin/assign-class-teacher")
def assign_class_teacher(data: Dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can assign class teachers")
    teacher_id = data.get("teacher_id")
    department = data.get("department")
    level = data.get("level")
    existing = db.query(ClassTeacher).filter(ClassTeacher.department == department, ClassTeacher.level == level).first()
    if existing:
        existing.teacher_id = teacher_id
    else:
        class_teacher = ClassTeacher(teacher_id=teacher_id, department=department, level=level)
        db.add(class_teacher)
    
    # Send notification to teacher
    notification = Notification(
        user_id=teacher_id,
        title="🎓 Class Teacher Assignment",
        message=f"You have been assigned as class teacher for {department} - {level}. You can now manage this class.",
        type="class_assignment"
    )
    db.add(notification)
    db.commit()
    return {"message": "Class teacher assigned successfully"}

@app.get("/admin/class-teachers")
def get_class_teachers(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view class teachers")
    assignments = db.query(ClassTeacher).all()
    result = []
    for assignment in assignments:
        teacher = db.query(User).filter(User.id == assignment.teacher_id).first()
        if teacher:
            result.append({"id": assignment.id, "teacher_id": teacher.id, "teacher_name": teacher.full_name, "department": assignment.department, "level": assignment.level, "assigned_at": assignment.assigned_at.isoformat()})
    return result

@app.delete("/admin/class-teacher/{assignment_id}")
def remove_class_teacher(assignment_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can remove class teachers")
    assignment = db.query(ClassTeacher).filter(ClassTeacher.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    db.delete(assignment)
    db.commit()
    return {"message": "Class teacher removed successfully"}

@app.get("/teacher/my-assigned-class")
def get_my_assigned_class(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can access this")
    assignment = db.query(ClassTeacher).filter(ClassTeacher.teacher_id == current_user.id).first()
    if not assignment:
        return {"assigned": False, "message": "You are not assigned as a class teacher"}
    return {
        "assigned": True,
        "department": assignment.department,
        "level": assignment.level,
        "assigned_at": assignment.assigned_at.isoformat()
    }

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    
    # Add missing columns via raw SQL with better error handling
    db = SessionLocal()
    try:
        from sqlalchemy import text
        
        # Phase 1: Advanced question types columns
        migration_queries = [
            "ALTER TABLE questions ADD COLUMN question_config JSON",
            "ALTER TABLE questions ADD COLUMN media_url VARCHAR",
            "ALTER TABLE questions ADD COLUMN correct_answers JSON", 
            "ALTER TABLE questions ADD COLUMN partial_credit BOOLEAN DEFAULT FALSE",
            # Other existing migrations
            "ALTER TABLE quizzes ADD COLUMN results_released BOOLEAN DEFAULT FALSE",
            "ALTER TABLE quiz_attempts ADD COLUMN needs_review BOOLEAN DEFAULT FALSE",
            "ALTER TABLE quiz_attempts ADD COLUMN reviewed_by INTEGER",
            "ALTER TABLE quiz_attempts ADD COLUMN final_score FLOAT",
            "ALTER TABLE quiz_attempts ADD COLUMN percentage FLOAT DEFAULT 0.0",
            "ALTER TABLE quiz_attempts ADD COLUMN grade VARCHAR(5) DEFAULT 'F'",
            "ALTER TABLE quiz_attempts ADD COLUMN total_possible_points FLOAT DEFAULT 0.0",
            "ALTER TABLE student_answers ADD COLUMN points_earned FLOAT DEFAULT 0.0",
            "ALTER TABLE student_answers ADD COLUMN ai_feedback VARCHAR",
            "ALTER TABLE student_answers ADD COLUMN teacher_score FLOAT",
            "ALTER TABLE student_answers ADD COLUMN teacher_feedback TEXT",
            "ALTER TABLE chat_rooms ADD COLUMN module_id INTEGER",
            "ALTER TABLE chat_messages ADD COLUMN file_url VARCHAR",
            "ALTER TABLE chat_messages ADD COLUMN file_name VARCHAR",
            "ALTER TABLE chat_messages ADD COLUMN reply_to_id INTEGER"
        ]
        
        for query in migration_queries:
            try:
                db.execute(text(query))
                print(f"✅ Migration: {query[:50]}...")
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                    print(f"⚠️ Column already exists: {query[:50]}...")
                else:
                    print(f"❌ Migration failed: {query[:50]}... - {e}")
        
        db.commit()
        print("✅ Database migration complete")
    except Exception as e:
        print(f"Migration error: {e}")
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






# ==================== CHAT SYSTEM API ====================

@app.get("/chat/rooms")
def get_chat_rooms(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all chat rooms accessible to current user"""
    rooms = []
    
    if current_user.role == "admin":
        # DOS sees all rooms
        all_rooms = db.query(ChatRoom).filter(ChatRoom.is_active == True).all()
        for room in all_rooms:
            rooms.append({
                "id": room.id,
                "name": room.name,
                "room_type": room.room_type,
                "department": room.department,
                "level": room.level,
                "created_by": room.created_by,
                "unread_count": 0
            })
    elif current_user.role == "teacher":
        # Teachers see teacher-teacher, teacher-dos, and student-teacher rooms
        participant_rooms = db.query(ChatRoom).join(ChatParticipant).filter(
            ChatParticipant.user_id == current_user.id,
            ChatRoom.is_active == True
        ).all()
        for room in participant_rooms:
            rooms.append({
                "id": room.id,
                "name": room.name,
                "room_type": room.room_type,
                "department": room.department,
                "level": room.level,
                "created_by": room.created_by,
                "unread_count": 0
            })
    else:  # student
        # Students see student-student and student-teacher rooms for their dept/level
        participant_rooms = db.query(ChatRoom).join(ChatParticipant).filter(
            ChatParticipant.user_id == current_user.id,
            ChatRoom.is_active == True
        ).all()
        for room in participant_rooms:
            rooms.append({
                "id": room.id,
                "name": room.name,
                "room_type": room.room_type,
                "department": room.department,
                "level": room.level,
                "created_by": room.created_by,
                "unread_count": 0
            })
    
    return rooms

@app.post("/chat/rooms")
def create_chat_room(data: Dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new chat room"""
    # Allow both admin and teacher to create rooms
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Only admins and teachers can create chat rooms")
    
    room_type = data.get("room_type")
    name = data.get("name")
    department = data.get("department")
    level = data.get("level")
    notify_participants = data.get("notify_participants", True)
    
    # Create room
    room = ChatRoom(
        name=name,
        room_type=room_type,
        department=department,
        level=level,
        created_by=current_user.id
    )
    db.add(room)
    db.flush()
    
    # Add creator as participant
    participant = ChatParticipant(room_id=room.id, user_id=current_user.id)
    db.add(participant)
    
    participants_added = 0
    
    # Auto-add participants based on room type
    if room_type == "student-student" and department and level:
        students = db.query(User).filter(
            User.role == "student",
            User.department == department,
            User.level == level
        ).all()
        for student in students:
            if student.id != current_user.id:
                p = ChatParticipant(room_id=room.id, user_id=student.id)
                db.add(p)
                participants_added += 1
                
                # Send notification
                if notify_participants:
                    notif = Notification(
                        user_id=student.id,
                        title=f"💬 New Chat Room: {name}",
                        message=f"You've been added to '{name}' chat room. Start chatting now!",
                        type="chat_room"
                    )
                    db.add(notif)
        
        # Add ALL teachers from that department
        teachers = db.query(User).filter(User.role == "teacher").all()
        for teacher in teachers:
            if teacher.departments and department in teacher.departments:
                if teacher.id != current_user.id:  # Don't add creator twice
                    p = ChatParticipant(room_id=room.id, user_id=teacher.id)
                    db.add(p)
                    participants_added += 1
                    
                    if notify_participants:
                        notif = Notification(
                            user_id=teacher.id,
                            title=f"💬 New Chat Room: {name}",
                            message=f"You've been added to '{name}' for {department} - {level}.",
                            type="chat_room"
                        )
                        db.add(notif)
        
        # Add class teacher if exists
        class_teacher = db.query(ClassTeacher).filter(
            ClassTeacher.department == department,
            ClassTeacher.level == level
        ).first()
        if class_teacher and class_teacher.teacher_id != current_user.id:
            existing = db.query(ChatParticipant).filter(
                ChatParticipant.room_id == room.id,
                ChatParticipant.user_id == class_teacher.teacher_id
            ).first()
            if not existing:
                p = ChatParticipant(room_id=room.id, user_id=class_teacher.teacher_id)
                db.add(p)
                participants_added += 1
                
                if notify_participants:
                    notif = Notification(
                        user_id=class_teacher.teacher_id,
                        title=f"💬 New Chat Room: {name}",
                        message=f"You've been added to '{name}' as class teacher for {department} - {level}.",
                        type="chat_room"
                    )
                    db.add(notif)
                    
    elif room_type == "student-teacher" and department and level:
        # Add all students from dept/level
        students = db.query(User).filter(
            User.role == "student",
            User.department == department,
            User.level == level
        ).all()
        for student in students:
            p = ChatParticipant(room_id=room.id, user_id=student.id)
            db.add(p)
            participants_added += 1
            
            if notify_participants:
                notif = Notification(
                    user_id=student.id,
                    title=f"💬 New Chat Room: {name}",
                    message=f"You've been added to '{name}' chat room with your teachers. Start chatting now!",
                    type="chat_room"
                )
                db.add(notif)
                
        # Add ALL teachers from that department
        teachers = db.query(User).filter(User.role == "teacher").all()
        for teacher in teachers:
            if teacher.departments and department in teacher.departments:
                if teacher.id != current_user.id:  # Don't add creator twice
                    p = ChatParticipant(room_id=room.id, user_id=teacher.id)
                    db.add(p)
                    participants_added += 1
                    
                    if notify_participants:
                        notif = Notification(
                            user_id=teacher.id,
                            title=f"💬 New Chat Room: {name}",
                            message=f"You've been added to '{name}' chat room for {department} - {level}.",
                            type="chat_room"
                        )
                        db.add(notif)
                    
        # Add class teacher if exists
        class_teacher = db.query(ClassTeacher).filter(
            ClassTeacher.department == department,
            ClassTeacher.level == level
        ).first()
        if class_teacher and class_teacher.teacher_id != current_user.id:
            existing = db.query(ChatParticipant).filter(
                ChatParticipant.room_id == room.id,
                ChatParticipant.user_id == class_teacher.teacher_id
            ).first()
            if not existing:
                p = ChatParticipant(room_id=room.id, user_id=class_teacher.teacher_id)
                db.add(p)
                participants_added += 1
                
                if notify_participants:
                    notif = Notification(
                        user_id=class_teacher.teacher_id,
                        title=f"💬 New Chat Room: {name}",
                        message=f"You've been added to '{name}' as class teacher for {department} - {level}.",
                        type="chat_room"
                    )
                    db.add(notif)
                    
    elif room_type == "teacher-teacher":
        teachers = db.query(User).filter(User.role == "teacher").all()
        for teacher in teachers:
            if teacher.id != current_user.id:
                p = ChatParticipant(room_id=room.id, user_id=teacher.id)
                db.add(p)
                participants_added += 1
                
                if notify_participants:
                    notif = Notification(
                        user_id=teacher.id,
                        title=f"💬 New Chat Room: {name}",
                        message=f"You've been added to '{name}' teacher lounge.",
                        type="chat_room"
                    )
                    db.add(notif)
                    
    elif room_type == "teacher-dos":
        # Add all teachers
        teachers = db.query(User).filter(User.role == "teacher").all()
        for teacher in teachers:
            if teacher.id != current_user.id:
                p = ChatParticipant(room_id=room.id, user_id=teacher.id)
                db.add(p)
                participants_added += 1
                
                if notify_participants:
                    notif = Notification(
                        user_id=teacher.id,
                        title=f"💬 New Chat Room: {name}",
                        message=f"You've been added to '{name}' with DOS.",
                        type="chat_room"
                    )
                    db.add(notif)
                
        # Add DOS
        admins = db.query(User).filter(User.role == "admin").all()
        for admin in admins:
            if admin.id != current_user.id:
                p = ChatParticipant(room_id=room.id, user_id=admin.id)
                db.add(p)
                participants_added += 1
    
    db.commit()
    db.refresh(room)
    
    return {
        "id": room.id,
        "name": room.name,
        "room_type": room.room_type,
        "participants_added": participants_added
    }

@app.get("/chat/rooms/{room_id}/messages")
def get_chat_messages(room_id: int, limit: int = 50, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get messages from a chat room"""
    # Check if user is participant
    participant = db.query(ChatParticipant).filter(
        ChatParticipant.room_id == room_id,
        ChatParticipant.user_id == current_user.id
    ).first()
    
    if not participant and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not a participant of this room")
    
    if participant and participant.is_blocked:
        raise HTTPException(status_code=403, detail="You have been blocked from this room")
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.room_id == room_id,
        ChatMessage.is_deleted == False
    ).order_by(ChatMessage.created_at.desc()).limit(limit).all()
    
    result = []
    for msg in reversed(messages):
        sender = db.query(User).filter(User.id == msg.sender_id).first()
        
        # Get reactions
        reactions = db.query(MessageReaction).filter(MessageReaction.message_id == msg.id).all()
        reaction_counts = {}
        for reaction in reactions:
            if reaction.emoji not in reaction_counts:
                reaction_counts[reaction.emoji] = {"count": 0, "users": [], "user_reacted": False}
            reaction_counts[reaction.emoji]["count"] += 1
            if reaction.user_id == current_user.id:
                reaction_counts[reaction.emoji]["user_reacted"] = True
        
        # Get reply info
        reply_to = None
        if msg.reply_to_id:
            reply_msg = db.query(ChatMessage).filter(ChatMessage.id == msg.reply_to_id).first()
            if reply_msg:
                reply_sender = db.query(User).filter(User.id == reply_msg.sender_id).first()
                reply_to = {
                    "id": reply_msg.id,
                    "sender_name": reply_sender.full_name if reply_sender else "Unknown",
                    "message": reply_msg.message[:50] + "..." if len(reply_msg.message) > 50 else reply_msg.message
                }
        
        result.append({
            "id": msg.id,
            "sender_id": msg.sender_id,
            "sender_name": sender.full_name if sender else "Unknown",
            "sender_role": sender.role if sender else "unknown",
            "message": msg.message,
            "message_type": msg.message_type,
            "file_url": msg.file_url,
            "file_name": msg.file_name,
            "reply_to": reply_to,
            "reactions": reaction_counts,
            "is_flagged": msg.is_flagged,
            "created_at": msg.created_at.isoformat()
        })
    
    return result

@app.post("/chat/rooms/{room_id}/messages")
def send_chat_message(room_id: int, data: Dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Send a message to a chat room"""
    # Check if user is participant
    participant = db.query(ChatParticipant).filter(
        ChatParticipant.room_id == room_id,
        ChatParticipant.user_id == current_user.id
    ).first()
    
    if not participant:
        raise HTTPException(status_code=403, detail="Not a participant of this room")
    
    if participant.is_blocked:
        raise HTTPException(status_code=403, detail="You have been blocked from this room")
    
    message_text = data.get("message", "").strip()
    message_type = data.get("message_type", "text")
    
    if not message_text:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Create message
    message = ChatMessage(
        room_id=room_id,
        sender_id=current_user.id,
        message=message_text,
        message_type=message_type,
        reply_to_id=data.get("reply_to_id"),
        file_url=data.get("file_url"),
        file_name=data.get("file_name")
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    
    return {
        "id": message.id,
        "sender_id": current_user.id,
        "sender_name": current_user.full_name,
        "sender_role": current_user.role,
        "message": message.message,
        "message_type": message.message_type,
        "file_url": message.file_url,
        "file_name": message.file_name,
        "reply_to_id": message.reply_to_id,
        "created_at": message.created_at.isoformat()
    }

@app.post("/chat/upload-file")
async def upload_chat_file(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    """Upload a file for chat"""
    import os
    import uuid
    
    # Create uploads directory if not exists
    upload_dir = "uploads/chat"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save file
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    return {
        "file_url": f"/uploads/chat/{unique_filename}",
        "file_name": file.filename
    }

@app.post("/chat/messages/{message_id}/react")
def react_to_message(message_id: int, data: Dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Add or remove reaction to a message"""
    emoji = data.get("emoji")
    if not emoji:
        raise HTTPException(status_code=400, detail="Emoji required")
    
    # Check if reaction already exists
    existing = db.query(MessageReaction).filter(
        MessageReaction.message_id == message_id,
        MessageReaction.user_id == current_user.id,
        MessageReaction.emoji == emoji
    ).first()
    
    if existing:
        # Remove reaction
        db.delete(existing)
        db.commit()
        return {"action": "removed", "emoji": emoji}
    else:
        # Add reaction
        reaction = MessageReaction(
            message_id=message_id,
            user_id=current_user.id,
            emoji=emoji
        )
        db.add(reaction)
        db.commit()
        return {"action": "added", "emoji": emoji}

@app.get("/chat/messages/{message_id}/reactions")
def get_message_reactions(message_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all reactions for a message"""
    reactions = db.query(MessageReaction).filter(MessageReaction.message_id == message_id).all()
    
    # Group by emoji
    reaction_counts = {}
    for reaction in reactions:
        if reaction.emoji not in reaction_counts:
            reaction_counts[reaction.emoji] = {"count": 0, "users": [], "user_reacted": False}
        reaction_counts[reaction.emoji]["count"] += 1
        user = db.query(User).filter(User.id == reaction.user_id).first()
        if user:
            reaction_counts[reaction.emoji]["users"].append(user.full_name)
        if reaction.user_id == current_user.id:
            reaction_counts[reaction.emoji]["user_reacted"] = True
    
    return reaction_counts

@app.delete("/chat/messages/{message_id}")
def delete_chat_message(message_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a chat message (sender or DOS only)"""
    message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Only sender or DOS can delete
    if message.sender_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Cannot delete this message")
    
    message.is_deleted = True
    db.commit()
    
    return {"message": "Message deleted"}

@app.post("/chat/messages/{message_id}/flag")
def flag_chat_message(message_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Flag a message for DOS review"""
    message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    message.is_flagged = True
    db.commit()
    
    # Notify DOS
    admins = db.query(User).filter(User.role == "admin").all()
    for admin in admins:
        notification = Notification(
            user_id=admin.id,
            title="🚩 Message Flagged for Review",
            message=f"A message in chat room has been flagged by {current_user.full_name}",
            type="chat_flag"
        )
        db.add(notification)
    db.commit()
    
    return {"message": "Message flagged for review"}

@app.post("/chat/rooms/{room_id}/block-user/{user_id}")
def block_user_from_room(room_id: int, user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Block a user from a chat room (DOS only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only DOS can block users")
    
    participant = db.query(ChatParticipant).filter(
        ChatParticipant.room_id == room_id,
        ChatParticipant.user_id == user_id
    ).first()
    
    if not participant:
        raise HTTPException(status_code=404, detail="User not in this room")
    
    participant.is_blocked = True
    db.commit()
    
    return {"message": "User blocked from room"}

@app.get("/chat/flagged-messages")
def get_flagged_messages(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all flagged messages (DOS only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only DOS can view flagged messages")
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.is_flagged == True,
        ChatMessage.is_deleted == False
    ).order_by(ChatMessage.created_at.desc()).all()
    
    result = []
    for msg in messages:
        sender = db.query(User).filter(User.id == msg.sender_id).first()
        room = db.query(ChatRoom).filter(ChatRoom.id == msg.room_id).first()
        result.append({
            "id": msg.id,
            "room_id": msg.room_id,
            "room_name": room.name if room else "Unknown",
            "sender_id": msg.sender_id,
            "sender_name": sender.full_name if sender else "Unknown",
            "message": msg.message,
            "created_at": msg.created_at.isoformat()
        })
    
    return result
@app.get("/chat/unread-count")
def get_unread_count(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get unread message count for current user"""
    # Get user's rooms
    user_rooms = db.query(ChatParticipant.room_id).filter(
        ChatParticipant.user_id == current_user.id,
        ChatParticipant.is_blocked == False
    ).subquery()
    
    # Count messages in user's rooms from last 24 hours that aren't from the user
    from datetime import timedelta
    yesterday = now() - timedelta(days=1)
    
    unread_count = db.query(ChatMessage).filter(
        ChatMessage.room_id.in_(user_rooms),
        ChatMessage.sender_id != current_user.id,
        ChatMessage.created_at > yesterday,
        ChatMessage.is_deleted == False
    ).count()
    
    return {"count": unread_count}

@app.put("/chat/rooms/{room_id}")
def update_chat_room(room_id: int, data: Dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update a chat room (creator only)"""
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    if room.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Only the room creator can edit this room")
    
    room.name = data.get("name", room.name)
    db.commit()
    db.refresh(room)
    
    return {
        "id": room.id,
        "name": room.name,
        "room_type": room.room_type,
        "department": room.department,
        "level": room.level,
        "created_by": room.created_by
    }

@app.delete("/chat/rooms/{room_id}")
def delete_chat_room(room_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a chat room (creator or admin only)"""
    room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    
    # Only creator or admin can delete
    if room.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only the room creator or admin can delete this room")
    
    # Delete all messages in the room
    db.query(ChatMessage).filter(ChatMessage.room_id == room_id).delete(synchronize_session=False)
    
    # Delete all participants
    db.query(ChatParticipant).filter(ChatParticipant.room_id == room_id).delete(synchronize_session=False)
    
    # Delete the room
    db.delete(room)
    db.commit()
    
    return {"message": "Chat room deleted successfully"}