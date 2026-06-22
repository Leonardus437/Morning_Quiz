from fastapi import FastAPI, Depends, HTTPException, status, Request, File, UploadFile, Form, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey, Float, text
from sqlalchemy.orm import Session

# Import core modules
from core.database import Base, SessionLocal, engine, database_type, get_db
from core.config import Config
from core.seed import initialize_offline_database
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import hashlib
import secrets
from jose import JWTError, jwt
import os
import json

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

def parse_advanced_question(text):
    """Lightweight parser for documents"""
    import re
    text = text.strip()
    if len(text) < 10:
        return None
    
    result = {'text': text, 'type': 'multiple_choice', 'options': [], 'answer': ''}
    
    # Extract answer (simplified)
    for pattern in [r'answer\s*:\s*(.+?)(?=\n|$)', r'ans\s*:\s*(.+?)(?=\n|$)']:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result['answer'] = match.group(1).strip()
            text = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()
            break
    
    # Detect type (simplified)
    if re.search(r'\b(true|false)\b', text, re.IGNORECASE):
        result['type'] = 'true_false'
        result['options'] = ['True', 'False']
    
    # Extract options (simplified)
    for pattern in [r'([A-Z])\)\s*([^A-Z\)\n]+)', r'([A-Z])\.\s*([^A-Z\.\n]+)']:
        options_found = re.findall(pattern, text)
        if len(options_found) >= 2:
            result['options'] = [opt[1].strip() for opt in options_found]
            break
    
    result['text'] = text.strip()
    return result if result['text'] and result['answer'] else None

# Security (using Config from core module)
SECRET_KEY = Config.SECRET_KEY
ALGORITHM = Config.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = Config.ACCESS_TOKEN_EXPIRE_MINUTES

security = HTTPBearer()

app = FastAPI(title="TVET/TSS Quiz API - Offline First")

# CRITICAL: Add CORS middleware BEFORE any routes
# Allow all origins for now to fix immediate issue
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Must be False when allow_origins is *
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
    
    # School hierarchy fields
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=True)
    trade_id = Column(Integer, ForeignKey("trades.id"), nullable=True)
    
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
    flagged_for_cheating = Column(Boolean, default=False)
    cheating_reason = Column(Text)

class StudentAnswer(Base):
    __tablename__ = "student_answers"
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("quiz_attempts.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    student_answer = Column(Text)
    is_correct = Column(Boolean)
    points_earned = Column(Float, default=0.0)
    ai_feedback = Column(Text)
    time_spent = Column(Integer, default=0)
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

# School Management Models
class Province(Base):
    __tablename__ = "provinces"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True)
    code = Column(String(10), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class District(Base):
    __tablename__ = "districts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    code = Column(String(10))
    province_id = Column(Integer, ForeignKey("provinces.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class SchoolType(Base):
    __tablename__ = "school_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True)
    abbreviation = Column(String(10), unique=True)
    description = Column(Text)

class School(Base):
    __tablename__ = "schools"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200))
    code = Column(String(50), unique=True)
    school_type_id = Column(Integer, ForeignKey("school_types.id"))
    district_id = Column(Integer, ForeignKey("districts.id"))
    province_id = Column(Integer, ForeignKey("provinces.id"))
    sector = Column(String(100))
    school_type = Column(String(20))  # TSS, VTC, IPRC
    address = Column(Text)
    phone = Column(String(20))
    email = Column(String(100))
    is_reaccredited = Column(Boolean, default=False)
    accreditation_year = Column(String(20))
    status = Column(String(20), default="active")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200))
    code = Column(String(50), unique=True)
    description = Column(Text)
    category = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class SchoolTrade(Base):
    __tablename__ = "school_trades"
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id"))
    trade_id = Column(Integer, ForeignKey("trades.id"))
    levels_offered = Column(JSON)  # ["L3", "L4", "L5"]
    capacity = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

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

class LessonCreate(BaseModel):
    title: str
    code: str
    description: str
    department: str
    level: str
    classification: str

class TeacherLessonAssign(BaseModel):
    teacher_id: int
    lesson_id: int

# Note: get_db() is now imported from core.database module

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
        print(f"[VERIFY] Password length: {len(password)}, Hash length: {len(hashed)}, Hash starts with $2b$: {hashed.startswith('$2b$')}, BCRYPT_AVAILABLE: {BCRYPT_AVAILABLE}")
        if hashed.startswith('$2b$') and BCRYPT_AVAILABLE:
            result = bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
            print(f"[VERIFY] Bcrypt check result: {result}")
            return result
        elif ':' in hashed:
            salt, password_hash = hashed.split(':', 1)
            computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return computed_hash == password_hash
        elif len(hashed) == 64 and all(c in '0123456789abcdef' for c in hashed.lower()):
            # Plain SHA-256 hash (for DOS users)
            computed_hash = hashlib.sha256(password.encode()).hexdigest()
            print(f"[VERIFY] Plain SHA-256 check: {computed_hash == hashed}")
            return computed_hash == hashed
        else:
            print(f"[VERIFY] Hash format not recognized")
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

@app.get("/quizzes")
def get_quizzes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == "teacher":
        quizzes = db.query(Quiz).filter(Quiz.created_by == current_user.id).all()
        return quizzes
    
    if not current_user.department or not current_user.level:
        raise HTTPException(status_code=400, detail="Student must have department and level assigned")
    
    # Handle both specific levels (L5) and ranges (L3-5)
    student_level = current_user.level
    
    if '-' in student_level:
        # Student has a range - expand it (e.g., L3-5 -> [L3, L4, L5])
        parts = student_level.replace('L', '').split('-')
        if len(parts) == 2:
            try:
                start = int(parts[0])
                end = int(parts[1])
                student_levels = [f"L{i}" for i in range(start, end + 1)]
            except:
                student_levels = [student_level]
        else:
            student_levels = [student_level]
        
        quizzes = db.query(Quiz).filter(
            Quiz.is_active == True,
            Quiz.department == current_user.department,
            Quiz.level.in_(student_levels)
        ).all()
    else:
        # Student has specific level - exact match only
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
        # Check department match
        if quiz.department != current_user.department:
            raise HTTPException(status_code=403, detail=f"Access denied. This quiz is for {quiz.department} students only.")
        
        # Check level match - handle both ranges and specific levels
        student_level = current_user.level
        level_match = False
        
        if '-' in student_level:
            # Student has range (e.g., L3-5) - check if quiz level is in range
            parts = student_level.replace('L', '').split('-')
            if len(parts) == 2:
                try:
                    start = int(parts[0])
                    end = int(parts[1])
                    quiz_level_num = int(quiz.level.replace('L', ''))
                    level_match = start <= quiz_level_num <= end
                except:
                    level_match = (quiz.level == student_level)
            else:
                level_match = (quiz.level == student_level)
        else:
            # Student has specific level - exact match
            level_match = (quiz.level == student_level)
        
        if not level_match:
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
async def submit_quiz(submission: Dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Submit quiz answers and calculate score"""
    try:
        quiz_id = submission.get('quiz_id')
        answers_list = submission.get('answers', [])
        
        # Convert answers array to dictionary
        answers = {}
        if isinstance(answers_list, list):
            for item in answers_list:
                if isinstance(item, dict):
                    answers[str(item.get('question_id'))] = item.get('answer')
        elif isinstance(answers_list, dict):
            answers = answers_list
        
        if not quiz_id:
            raise HTTPException(status_code=400, detail="Quiz ID is required")
        
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        # Check if already attempted
        existing_attempt = db.query(QuizAttempt).filter(
            QuizAttempt.quiz_id == quiz_id,
            QuizAttempt.user_id == current_user.id
        ).first()
        
        if existing_attempt:
            raise HTTPException(status_code=400, detail="Quiz already submitted")
        
        # Get all questions for this quiz
        questions = db.query(Question).join(QuizQuestion).filter(
            QuizQuestion.quiz_id == quiz_id
        ).all()
        
        score = 0
        total_questions = len(questions)
        
        # Create quiz attempt first
        attempt = QuizAttempt(
            user_id=current_user.id,
            quiz_id=quiz_id,
            score=0,  # Will update after grading
            total_questions=total_questions,
            completed_at=now()
        )
        db.add(attempt)
        db.flush()  # Get the attempt ID without committing
        
        # Grade each question
        for question in questions:
            student_answer = answers.get(str(question.id), '')
            
            # Convert answer to string for storage
            if isinstance(student_answer, dict):
                answer_text = json.dumps(student_answer)
            elif isinstance(student_answer, list):
                answer_text = ','.join(str(a) for a in student_answer)
            else:
                answer_text = str(student_answer) if student_answer else ''
            
            # Save student answer with attempt_id
            student_ans = StudentAnswer(
                attempt_id=attempt.id,
                user_id=current_user.id,
                question_id=question.id,
                student_answer=answer_text,
                time_spent=0
            )
            db.add(student_ans)
            
            # Grade the answer based on question type
            if question.question_type in ['mcq', 'multiple_choice', 'true_false', 'dropdown_select']:
                if str(student_answer).strip().lower() == str(question.correct_answer).strip().lower():
                    score += question.points
                    student_ans.is_correct = True
            
            elif question.question_type == 'multiple_select':
                # Handle array of selected options
                if isinstance(student_answer, list):
                    correct_answers = [a.strip() for a in str(question.correct_answer).split(',')]
                    student_answers = [str(a).strip() for a in student_answer]
                    if set(student_answers) == set(correct_answers):
                        score += question.points
                        student_ans.is_correct = True
            
            elif question.question_type in ['fill_blanks', 'fill_in_blanks']:
                # Handle pipe-separated answers: "answer1|answer2|answer3"
                if isinstance(student_answer, str) and '|' in student_answer:
                    student_blanks = [a.strip().lower() for a in student_answer.split('|')]
                    correct_blanks = [a.strip().lower() for a in str(question.correct_answer).split('|')]
                    if student_blanks == correct_blanks:
                        score += question.points
                        student_ans.is_correct = True
                elif isinstance(student_answer, str) and student_answer.strip():
                    if student_answer.strip().lower() == str(question.correct_answer).strip().lower():
                        score += question.points
                        student_ans.is_correct = True
            
            elif question.question_type == 'matching_pairs':
                # Handle pipe-separated pairs: "match1|match2|match3"
                if isinstance(student_answer, str) and '|' in student_answer:
                    student_pairs = set(student_answer.split('|'))
                    correct_pairs = set(str(question.correct_answer).split('|'))
                    if student_pairs == correct_pairs:
                        score += question.points
                        student_ans.is_correct = True
            
            elif question.question_type == 'drag_drop_ordering':
                # Handle pipe-separated order: "item1|item2|item3"
                if isinstance(student_answer, str) and '|' in student_answer:
                    if student_answer.strip() == str(question.correct_answer).strip():
                        score += question.points
                        student_ans.is_correct = True
            
            elif question.question_type == 'multi_grid':
                # Handle object: {row1: "col1", row2: "col2"}
                if isinstance(student_answer, dict):
                    # For now, mark as needs review
                    student_ans.is_correct = False
                    # Teacher will review manually
            
            elif question.question_type in ['short_answer', 'essay', 'code_writing', 'sql_query']:
                # Accept any non-empty answer for text-based questions
                if student_answer and str(student_answer).strip():
                    if str(student_answer).strip().lower() == str(question.correct_answer).strip().lower():
                        score += question.points
                        student_ans.is_correct = True
                        student_ans.points_earned = question.points
                    else:
                        student_ans.is_correct = False
                        student_ans.points_earned = 0
                        attempt.needs_review = True
            
            elif question.question_type == 'linear_scale':
                # Linear scale has no correct answer, just record the response
                student_ans.is_correct = True
                score += question.points
        
        # Update attempt score
        attempt.score = score
        print(f"DEBUG: About to commit attempt - quiz_id={quiz_id}, user_id={current_user.id}, score={score}/{total_questions}")
        print(f"DEBUG: Attempt object: id={attempt.id}, score={attempt.score}, total={attempt.total_questions}")
        
        # Commit the attempt and answers FIRST
        try:
            db.commit()
            print(f"DEBUG: Commit successful, attempt_id={attempt.id}")
        except Exception as commit_error:
            print(f"ERROR: Commit failed: {commit_error}")
            print(f"ERROR: Exception type: {type(commit_error).__name__}")
            import traceback
            traceback.print_exc()
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to save quiz attempt: {str(commit_error)}")
        
        db.refresh(attempt)
        print(f"DEBUG: Attempt refreshed, final score={attempt.score}")
        
        # NOW create notification AFTER successful commit
        try:
            teacher = db.query(User).filter(User.id == quiz.created_by).first()
            if teacher:
                percentage = round((score / total_questions * 100) if total_questions > 0 else 0, 2)
                notification = Notification(
                    user_id=teacher.id,
                    title=f"New Quiz Submission: {quiz.title}",
                    message=f"{current_user.full_name} completed '{quiz.title}' - Score: {score}/{total_questions} ({percentage}%)",
                    type="quiz_submission"
                )
                db.add(notification)
                db.commit()
                print(f"DEBUG: Notification created for teacher {teacher.id}")
        except Exception as e:
            print(f"WARNING: Failed to create notification: {e}")
            # Don't fail the submission if notification fails
        
        return {
            "success": True,
            "score": score,
            "total_questions": total_questions,
            "percentage": round((score / total_questions * 100) if total_questions > 0 else 0, 2),
            "attempt_id": attempt.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"ERROR in submit_quiz: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Submission failed: {str(e)}")

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
@app.head("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "TVET Quiz API",
        "version": "2.0"
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

@app.get("/lessons-list")
def get_lessons(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    lessons = db.query(Lesson).filter(Lesson.is_active == True).all()
    return lessons

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

@app.get("/questions-list")
def get_questions_list(department: Optional[str] = None, level: Optional[str] = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can view questions")
    
    query = db.query(Question).filter(Question.created_by == current_user.id)
    
    if department:
        query = query.filter(Question.department == department)
    if level:
        query = query.filter(Question.level == level)
    
    questions = query.all()
    return questions

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
async def upload_questions(file: UploadFile = File(...), department: str = Form(...), level: str = Form(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can upload questions")
    
    try:
        from advanced_question_parser import parser
        
        content = await file.read()
        filename = file.filename
        
        print(f"📄 Processing file: {filename} ({len(content)} bytes)")
        
        # Use advanced parser
        result = parser.parse_document(content, filename)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to parse document'))
        
        # Save questions to database
        saved_questions = []
        for parsed_q in result['questions']:
            new_question = Question(
                question_text=parsed_q['text'],
                question_type=parsed_q['type'],
                options=parsed_q.get('options', []),
                correct_answer=parsed_q.get('answer', ''),
                points=1,
                department=department,
                level=level,
                created_by=current_user.id
            )
            db.add(new_question)
            saved_questions.append(parsed_q)
        
        db.commit()
        
        print(f"✅ Successfully saved {len(saved_questions)} questions")
        
        # Build response
        response = {
            "success": True,
            "questions": saved_questions,
            "count": result['count'],
            "total_blocks_found": result['total_blocks'],
            "skipped_blocks": result['skipped'],
            "message": f"Successfully extracted and saved {result['count']} questions from {filename}"
        }
        
        # Add warnings if any
        if result.get('warnings'):
            response['warnings'] = result['warnings']
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ Upload failed: {str(e)}")
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

@app.options("/quizzes/{quiz_id}")
async def delete_quiz_options(quiz_id: int):
    """Handle CORS preflight for quiz deletion"""
    return {"message": "OK"}

@app.delete("/quizzes/{quiz_id}")
def delete_quiz(quiz_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can delete quizzes")
    
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.created_by == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    try:
        # Get all attempt IDs for this quiz first
        attempt_ids = [attempt.id for attempt in db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).all()]
        
        # Delete student answers using attempt_id (not quiz_id)
        if attempt_ids:
            db.query(StudentAnswer).filter(StudentAnswer.attempt_id.in_(attempt_ids)).delete(synchronize_session=False)
        
        # Delete quiz attempts
        db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).delete(synchronize_session=False)
        
        # Delete quiz questions
        db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz_id).delete(synchronize_session=False)
        
        # Delete quiz
        db.delete(quiz)
        db.commit()
        return {"message": "Quiz deleted successfully"}
    except Exception as e:
        db.rollback()
        print(f"Error deleting quiz: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete quiz: {str(e)}")

@app.get("/quizzes/{quiz_id}/leaderboard")
def get_quiz_leaderboard(quiz_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Teachers can always see leaderboard, students only if results are released
    if current_user.role == "teacher" and quiz.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if current_user.role == "student" and not quiz.results_released:
        raise HTTPException(status_code=403, detail="Results not yet released by teacher")
    
    attempts = db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).all()
    
    leaderboard = []
    for attempt in attempts:
        student = db.query(User).filter(User.id == attempt.user_id).first()
        if student:
            # Use final_score if available (teacher-reviewed), otherwise use initial score
            display_score = attempt.final_score if attempt.final_score is not None else attempt.score
            leaderboard.append({
                "student_name": student.full_name,
                "username": student.username,
                "score": display_score,
                "total": attempt.total_questions,
                "percentage": round((display_score / attempt.total_questions * 100) if attempt.total_questions > 0 else 0, 1),
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
    
    print(f"DEBUG /results/{quiz_id}: Quiz found: {quiz.title}")
    
    attempts = db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).all()
    print(f"DEBUG /results/{quiz_id}: Found {len(attempts)} attempts")
    
    results = []
    for attempt in attempts:
        print(f"DEBUG: Processing attempt {attempt.id}, user_id={attempt.user_id}, score={attempt.score}")
        student = db.query(User).filter(User.id == attempt.user_id).first()
        if student:
            # Use final_score (teacher-reviewed) if available, otherwise use initial score
            display_score = attempt.final_score if attempt.final_score is not None else attempt.score
            result_item = {
                "student_name": student.full_name,
                "username": student.username,
                "score": display_score,
                "total": attempt.total_questions,
                "percentage": round((display_score / attempt.total_questions * 100) if attempt.total_questions > 0 else 0, 1),
                "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None
            }
            print(f"DEBUG: Adding result: {result_item}")
            results.append(result_item)
        else:
            print(f"DEBUG: Student not found for user_id={attempt.user_id}")
    
    response = {
        "quiz_title": quiz.title,
        "total_attempts": len(results),
        "results": sorted(results, key=lambda x: x["score"], reverse=True)
    }
    print(f"DEBUG /results/{quiz_id}: Returning response with {len(results)} results")
    print(f"DEBUG: Full response: {response}")
    return response

@app.get("/schedules")
def get_schedules(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return []

@app.get("/announcements")
def get_announcements(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return []

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

@app.get("/lessons/by-department-level")
def get_lessons_by_department_level(
    department: str,
    level: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get lessons assigned to teacher filtered by department and optionally level"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can access lessons")
    
    # Get lessons assigned to this teacher
    query = db.query(Lesson).join(TeacherLesson).filter(
        TeacherLesson.teacher_id == current_user.id,
        Lesson.department == department,
        Lesson.is_active == True
    )
    
    # Filter by level if provided
    if level:
        query = query.filter(Lesson.level == level)
    
    lessons = query.all()
    
    return [
        {
            "id": lesson.id,
            "title": lesson.title,
            "code": lesson.code,
            "department": lesson.department,
            "level": lesson.level
        }
        for lesson in lessons
    ]

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
    
    # Clear previous attempts when rebroadcasting
    attempt_ids = [attempt.id for attempt in db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).all()]
    if attempt_ids:
        db.query(StudentAnswer).filter(StudentAnswer.attempt_id.in_(attempt_ids)).delete(synchronize_session=False)
    db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).delete(synchronize_session=False)
    
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
    try:
        teachers = db.query(User).filter(User.role == "teacher").all()
        return [{"id": t.id, "username": t.username, "full_name": t.full_name, "departments": t.departments or []} for t in teachers]
    except Exception as e:
        print(f"Error fetching teachers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/lessons")
def get_lessons(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all lessons"""
    try:
        lessons = db.query(Lesson).all()
        return [
            {
                "id": l.id,
                "title": l.title,
                "code": l.code,
                "description": l.description,
                "department": l.department,
                "level": l.level,
                "classification": l.classification,
                "is_active": l.is_active,
                "created_by": l.created_by,
                "created_at": l.created_at.isoformat() if l.created_at else None
            }
            for l in lessons
        ]
    except Exception as e:
        print(f"Error fetching lessons: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/lessons")
def create_lesson(lesson_data: LessonCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new lesson (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create lessons")
    
    try:
        # Check if lesson code already exists
        existing = db.query(Lesson).filter(Lesson.code == lesson_data.code).first()
        if existing:
            raise HTTPException(status_code=400, detail="Lesson code already exists")
        
        lesson = Lesson(
            title=lesson_data.title,
            code=lesson_data.code,
            description=lesson_data.description,
            department=lesson_data.department,
            level=lesson_data.level,
            classification=lesson_data.classification,
            created_by=current_user.id
        )
        db.add(lesson)
        db.commit()
        db.refresh(lesson)
        
        return {
            "id": lesson.id,
            "title": lesson.title,
            "code": lesson.code,
            "description": lesson.description,
            "department": lesson.department,
            "level": lesson.level,
            "classification": lesson.classification,
            "created_at": lesson.created_at.isoformat() if lesson.created_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error creating lesson: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create lesson: {str(e)}")

@app.post("/lessons/{lesson_id}/assign-teacher")
def assign_teacher_to_lesson(lesson_id: int, assignment: TeacherLessonAssign, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Assign a teacher to a lesson (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can assign teachers")
    
    try:
        # Verify lesson exists
        lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
        if not lesson:
            raise HTTPException(status_code=404, detail="Lesson not found")
        
        # Verify teacher exists
        teacher = db.query(User).filter(User.id == assignment.teacher_id, User.role == "teacher").first()
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")
        
        # Check if already assigned
        existing = db.query(TeacherLesson).filter(
            TeacherLesson.teacher_id == assignment.teacher_id,
            TeacherLesson.lesson_id == lesson_id
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Teacher already assigned to this lesson")
        
        # Create assignment
        assignment_obj = TeacherLesson(
            teacher_id=assignment.teacher_id,
            lesson_id=lesson_id
        )
        db.add(assignment_obj)
        db.commit()
        db.refresh(assignment_obj)
        
        return {
            "id": assignment_obj.id,
            "teacher_id": assignment_obj.teacher_id,
            "lesson_id": assignment_obj.lesson_id,
            "assigned_at": assignment_obj.assigned_at.isoformat() if assignment_obj.assigned_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error assigning teacher to lesson: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to assign teacher: {str(e)}")

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
        import pandas as pd
        import io
        import re
        
        content = await file.read()
        filename = file.filename.lower()
        
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

@app.put("/admin/teacher/{teacher_id}/change-password")
def change_teacher_password(teacher_id: int, data: Dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """DOS can change teacher password"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can change teacher passwords")
    
    new_password = data.get('new_password', '').strip()
    if not new_password or len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    # First try to find by ID only
    teacher = db.query(User).filter(User.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail=f"User with ID {teacher_id} not found")
    
    # Check if user is a teacher or admin (allow changing admin passwords too)
    if teacher.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=400, detail=f"Cannot change password for role: {teacher.role}")
    
    teacher.password_hash = hash_password_simple(new_password)
    db.commit()
    
    return {"message": f"Password changed successfully for {teacher.full_name}", "username": teacher.username}
    
    return {"message": f"Password changed successfully for {teacher.full_name}", "username": teacher.username}

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

@app.get("/student/results")
def get_student_results(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all quiz results for the logged-in student"""
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can access their results")
    
    print(f"[STUDENT RESULTS] User: {current_user.username} (ID: {current_user.id})")
    
    attempts = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == current_user.id,
        QuizAttempt.completed_at.isnot(None)
    ).order_by(QuizAttempt.completed_at.desc()).all()
    
    print(f"[STUDENT RESULTS] Found {len(attempts)} completed attempts")
    
    results = []
    for attempt in attempts:
        quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()
        print(f"[STUDENT RESULTS] Attempt {attempt.id}: quiz_id={attempt.quiz_id}, quiz_found={quiz is not None}, results_released={quiz.results_released if quiz else 'N/A'}")
        # Only show results if quiz results have been released by teacher
        if quiz and quiz.results_released:
            display_score = attempt.final_score if attempt.final_score is not None else attempt.score
            result_item = {
                "quiz_id": quiz.id,
                "quiz_title": quiz.title,
                "score": display_score,
                "total_questions": attempt.total_questions,
                "completed_at": attempt.completed_at.isoformat() if attempt.completed_at else None
            }
            print(f"[STUDENT RESULTS] Adding result: {result_item}")
            results.append(result_item)
    
    print(f"[STUDENT RESULTS] Returning {len(results)} results")
    return results

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
    
    # Check if results have been released
    if not quiz.results_released:
        raise HTTPException(status_code=403, detail="Results not yet released by teacher")
    
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

# Create tables (lightweight)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"DB init: {e}")

# Initialize database

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

@app.on_event("startup")
def startup_event():
    # Create tables only
    Base.metadata.create_all(bind=engine)
    
    # Minimal offline mode check
    if Config.is_offline_mode():
        print("🔒 OFFLINE MODE")
        initialize_offline_database(engine, Base, {'User': User, 'Question': Question, 'Quiz': Quiz})
    
    # Seed only essential users
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "admin").first():
            db.add(User(username="admin", password_hash=hash_password_simple("admin123"), role="admin", full_name="DOS Admin"))
        if not db.query(User).filter(User.username == "teacher001").first():
            db.add(User(username="teacher001", password_hash=hash_password_simple("teacher123"), role="teacher", full_name="Teacher One"))
        db.commit()
    except:
        db.rollback()
    finally:
        db.close()

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
    
    # Validate grades before saving (with better error handling)
    validation_errors = []
    for grade in review.grades:
        try:
            answer = db.query(StudentAnswer).filter(StudentAnswer.id == grade.answer_id).first()
            if answer:
                # Get the question to check max points
                question = db.query(Question).filter(Question.id == answer.question_id).first()
                if question:
                    max_points = question.points
                    
                    if grade.score > max_points:
                        validation_errors.append(f"Question ID {answer.question_id}: Maximum {max_points} marks, but {grade.score} given")
                    
                    if grade.score < 0:
                        validation_errors.append(f"Question ID {answer.question_id}: Cannot have negative marks")
        except Exception as e:
            print(f"Validation error for answer {grade.answer_id}: {str(e)}")
            continue
    
    if validation_errors:
        error_msg = "; ".join(validation_errors)
        print(f"Validation failed: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Update each answer with teacher's grade
    new_total = 0.0
    for grade in review.grades:
        try:
            answer = db.query(StudentAnswer).filter(StudentAnswer.id == grade.answer_id).first()
            if answer:
                answer.teacher_score = grade.score
                answer.teacher_feedback = grade.feedback
                new_total += grade.score
        except Exception as e:
            print(f"Error updating answer {grade.answer_id}: {str(e)}")
            continue
    
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
    
    # Send notifications to all students who took this quiz
    attempts = db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).all()
    for attempt in attempts:
        student = db.query(User).filter(User.id == attempt.user_id).first()
        if student:
            # Use final_score if available (teacher-reviewed), otherwise use initial score
            display_score = attempt.final_score if attempt.final_score is not None else attempt.score
            percentage = round((display_score / attempt.total_questions * 100) if attempt.total_questions > 0 else 0, 1)
            
            notification = Notification(
                user_id=student.id,
                title="Quiz Results Released!",
                message=f"Your results for '{quiz.title}' are now available! You scored {display_score}/{attempt.total_questions} ({percentage}%). Check your dashboard to view details.",
                type="results_released",
                is_read=False
            )
            db.add(notification)
    
    db.commit()
    
    return {"message": f"Results released to {len(attempts)} students"}

@app.post("/report-cheating")
def report_cheating(request: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Report cheating attempt to teacher"""
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can report from quiz")
    
    quiz_id = request.get('quiz_id')
    reason = request.get('reason', 'Unknown violation')
    warnings_count = request.get('warnings_count', 3)
    
    # Get quiz and teacher
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    teacher = db.query(User).filter(User.id == quiz.created_by).first()
    if not teacher:
        return {"message": "Teacher not found"}
    
    # Mark the attempt as flagged for cheating
    attempt = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.user_id == current_user.id
    ).first()
    
    if attempt:
        attempt.flagged_for_cheating = True
        attempt.cheating_reason = reason
    
    # Create notification for teacher
    notification = Notification(
        user_id=teacher.id,
        title="⚠️ Cheating Alert!",
        message=f"Student {current_user.full_name} ({current_user.username}) attempted to cheat in '{quiz.title}'. Reason: {reason}. Quiz was automatically terminated after {warnings_count} warnings.",
        type="cheating_alert",
        is_read=False
    )
    db.add(notification)
    db.commit()
    
    return {"message": "Cheating alert sent to teacher"}

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





# ============================================================================
# SCHOOL MANAGEMENT SYSTEM - COMPLETE API
# ============================================================================

from school_api import router as school_router
app.include_router(school_router, prefix="/api/schools", tags=["School Management"])

# ============================================================================
# REAL-TIME CHAT SYSTEM
# ============================================================================

from chat_api import router as chat_router
app.include_router(chat_router, tags=["Chat"])

# ============================================================================
# ASSIGNMENT/LMS SYSTEM
# ============================================================================

from assignment_api_simple import router as assignment_router
app.include_router(assignment_router, prefix="/api/assignments", tags=["Assignments"])

# ============================================================================
# MOODLE-LEVEL FEATURES - NEW ENDPOINTS (NON-BREAKING)
# ============================================================================

from moodle_endpoints import router as moodle_router
app.include_router(moodle_router, prefix="/api/moodle", tags=["Moodle Features"])

# ============================================================================
# EDUCATIONAL MATERIALS SYSTEM
# ============================================================================

from materials_api import router as materials_router
app.include_router(materials_router, prefix="/api/materials", tags=["Educational Materials"])

# Moodle Feature Endpoints (added directly to avoid circular imports)

class QuestionFeedbackUpdate(BaseModel):
    general_feedback: Optional[str] = None
    correct_feedback: Optional[str] = None
    incorrect_feedback: Optional[str] = None

@app.put("/api/moodle/questions/{question_id}/feedback")
def update_question_feedback(
    question_id: int,
    feedback: QuestionFeedbackUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add/update feedback for existing question (Moodle-style)"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can update feedback")
    
    db.execute(text("""
        UPDATE questions
        SET general_feedback = :gen_fb,
            correct_feedback = :corr_fb,
            incorrect_feedback = :incorr_fb
        WHERE id = :qid AND created_by = :uid
    """), {
        "gen_fb": feedback.general_feedback,
        "corr_fb": feedback.correct_feedback,
        "incorr_fb": feedback.incorrect_feedback,
        "qid": question_id,
        "uid": current_user.id
    })
    
    db.commit()
    return {"message": "Feedback updated successfully"}

@app.get("/api/moodle/questions/{question_id}/feedback")
def get_question_feedback(
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get feedback for a question"""
    result = db.execute(text("""
        SELECT general_feedback, correct_feedback, incorrect_feedback
        FROM questions
        WHERE id = :qid
    """), {"qid": question_id}).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return {
        "general_feedback": result[0],
        "correct_feedback": result[1],
        "incorrect_feedback": result[2]
    }

class QuestionCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

@app.post("/api/moodle/question-categories")
def create_question_category(
    category: QuestionCategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create question category (Moodle-style organization)"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can create categories")
    
    result = db.execute(text("""
        INSERT INTO question_categories (name, description, created_by)
        VALUES (:name, :desc, :creator)
        RETURNING id
    """), {
        "name": category.name,
        "desc": category.description,
        "creator": current_user.id
    })
    
    db.commit()
    cat_id = result.fetchone()[0]
    
    return {"id": cat_id, "name": category.name, "message": "Category created"}

@app.get("/api/moodle/question-categories")
def get_question_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all question categories for current teacher"""
    result = db.execute(text("""
        SELECT id, name, description
        FROM question_categories
        WHERE created_by = :uid
        ORDER BY name
    """), {"uid": current_user.id})
    
    categories = []
    for row in result:
        categories.append({
            "id": row[0],
            "name": row[1],
            "description": row[2]
        })
    
    return categories

class QuizFeedbackSettings(BaseModel):
    show_immediate_feedback: bool = False
    show_correct_answers: bool = False
    allow_multiple_attempts: bool = False
    max_attempts: int = 1

@app.put("/api/moodle/quizzes/{quiz_id}/feedback-settings")
def update_quiz_feedback_settings(
    quiz_id: int,
    settings: QuizFeedbackSettings,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enable immediate feedback for quiz (Moodle-style)"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can update quiz settings")
    
    db.execute(text("""
        UPDATE quizzes
        SET show_immediate_feedback = :imm_fb,
            show_correct_answers = :show_ans,
            allow_multiple_attempts = :multi_att,
            max_attempts = :max_att
        WHERE id = :qid AND created_by = :uid
    """), {
        "imm_fb": settings.show_immediate_feedback,
        "show_ans": settings.show_correct_answers,
        "multi_att": settings.allow_multiple_attempts,
        "max_att": settings.max_attempts,
        "qid": quiz_id,
        "uid": current_user.id
    })
    
    db.commit()
    return {"message": "Feedback settings updated successfully"}

@app.get("/api/moodle/quizzes/{quiz_id}/feedback-settings")
def get_quiz_feedback_settings(
    quiz_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get quiz feedback settings"""
    result = db.execute(text("""
        SELECT show_immediate_feedback, show_correct_answers, 
               allow_multiple_attempts, max_attempts
        FROM quizzes
        WHERE id = :qid
    """), {"qid": quiz_id}).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    return {
        "show_immediate_feedback": result[0] or False,
        "show_correct_answers": result[1] or False,
        "allow_multiple_attempts": result[2] or False,
        "max_attempts": result[3] or 1
    }

# ============================================================================
# PROCTORING WEBSOCKET
# ============================================================================

@app.websocket("/ws/proctoring/{quiz_id}/{user_id}")
async def proctoring_websocket(websocket: WebSocket, quiz_id: int, user_id: int, db: Session = Depends(get_db)):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            event_type = data.get('type')
            
            if event_type == 'violation':
                # Log violation to database
                quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
                if quiz:
                    teacher = db.query(User).filter(User.id == quiz.created_by).first()
                    student = db.query(User).filter(User.id == user_id).first()
                    
                    if teacher and student:
                        notification = Notification(
                            user_id=teacher.id,
                            title=f"⚠️ Proctoring Alert: {quiz.title}",
                            message=f"{student.full_name}: {data.get('reason', 'Unknown violation')}",
                            type="proctoring_alert"
                        )
                        db.add(notification)
                        db.commit()
                
                await websocket.send_json({"status": "logged"})
            
            elif event_type == 'heartbeat':
                await websocket.send_json({"status": "ok"})
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"Proctoring WS error: {e}")

# ============================================================================
# HIERARCHICAL SCHOOL SYSTEM ENDPOINTS
# ============================================================================

# Include cascading dropdown API
from cascading_api import router as cascading_router
app.include_router(cascading_router, tags=["Cascading Hierarchy"])

@app.get("/trades")
def get_trades(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get trades for the logged-in teacher's school"""
    from sqlalchemy import text
    
    # If user has school_id, get only that school's trades
    if current_user.school_id:
        result = db.execute(text("""
            SELECT DISTINCT t.name
            FROM trades t
            JOIN school_trades st ON t.id = st.trade_id
            WHERE st.school_id = :school_id
              AND st.is_active = true
              AND t.name IS NOT NULL
              AND LENGTH(TRIM(t.name)) > 3
            ORDER BY t.name
        """), {"school_id": current_user.school_id})
    else:
        # Fallback: get all trades if no school_id
        result = db.execute(text("""
            SELECT DISTINCT TRIM(name) as name 
            FROM trades 
            WHERE name IS NOT NULL 
              AND LENGTH(TRIM(name)) > 3
              AND name NOT LIKE '%1 %'
              AND name NOT LIKE '%2 %'
              AND name NOT LIKE '%/%'
            ORDER BY name
        """))
    
    trades = [row[0] for row in result]
    # Remove duplicates (case-insensitive)
    seen = set()
    unique_trades = []
    for trade in trades:
        trade_lower = trade.lower().strip()
        if trade_lower not in seen:
            seen.add(trade_lower)
            unique_trades.append(trade)
    return unique_trades

@app.get("/levels")
def get_levels(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get levels for the logged-in teacher's school from school_trades"""
    from sqlalchemy import text
    
    if current_user.school_id:
        # Get unique levels from school_trades for this school
        result = db.execute(text("""
            SELECT DISTINCT jsonb_array_elements_text(levels_offered::jsonb) as level
            FROM school_trades
            WHERE school_id = :school_id
              AND is_active = true
            ORDER BY level
        """), {"school_id": current_user.school_id})
        
        raw_levels = [row[0] for row in result]
        
        # Expand combined levels like "L3-5" into individual levels
        expanded_levels = set()
        for level in raw_levels:
            if 'L3-5' in level or 'L3-L5' in level:
                expanded_levels.update(['L3', 'L4', 'L5'])
            elif 'L4-5' in level or 'L4-L5' in level:
                expanded_levels.update(['L4', 'L5'])
            else:
                expanded_levels.add(level)
        
        # Sort levels properly (L1, L3, L4, L5)
        sorted_levels = sorted(expanded_levels, key=lambda x: int(x[1:]) if x.startswith('L') and x[1:].isdigit() else 99)
        return sorted_levels if sorted_levels else ["L3", "L4", "L5"]
    else:
        # Fallback for users without school_id
        return ["L3", "L4", "L5"]

@app.get("/hierarchy/provinces")
def get_provinces(db: Session = Depends(get_db)):
    """Get all provinces - NO AUTH REQUIRED"""
    from sqlalchemy import text
    try:
        result = db.execute(text("SELECT id, name FROM provinces ORDER BY name"))
        provinces = [{"id": row[0], "name": row[1], "code": row[1][:3].upper()} for row in result]
        print(f"[PROVINCES] Returning {len(provinces)} provinces")
        return provinces
    except Exception as e:
        print(f"[PROVINCES ERROR] {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/hierarchy/districts")
def get_districts(province_id: int, db: Session = Depends(get_db)):
    """Get districts by province with school count and enabled status"""
    from sqlalchemy import text
    result = db.execute(text("""
        SELECT d.id, d.name, COUNT(s.id) as school_count
        FROM districts d
        LEFT JOIN schools s ON d.id = s.district_id
        WHERE d.province_id = :pid
        GROUP BY d.id, d.name
        ORDER BY d.name
    """), {"pid": province_id})
    
    districts = []
    for row in result:
        school_count = row[2] or 0
        districts.append({
            "id": row[0],
            "name": row[1],
            "code": row[1][:3].upper(),
            "school_count": school_count,
            "enabled": school_count > 0,
            "disabled": school_count == 0
        })
    return districts

@app.get("/hierarchy/schools")
def get_schools(district_id: int, db: Session = Depends(get_db)):
    """Get schools by district"""
    from sqlalchemy import text
    result = db.execute(text("SELECT id, name FROM schools WHERE district_id = :did ORDER BY name"), {"did": district_id})
    return [{"id": row[0], "name": row[1]} for row in result]

@app.get("/hierarchy/school-trades")
def get_school_trades(school_id: int, db: Session = Depends(get_db)):
    """Get trades offered by a school with levels"""
    from sqlalchemy import text
    result = db.execute(text("""
        SELECT t.id, t.name, t.code, t.category, st.levels_offered
        FROM trades t
        JOIN school_trades st ON t.id = st.trade_id
        WHERE st.school_id = :sid AND st.is_active = true
        ORDER BY t.name
    """), {"sid": school_id})
    
    trades = []
    for row in result:
        import json
        levels = json.loads(row[4]) if isinstance(row[4], str) else row[4]
        trades.append({
            "id": row[0],
            "name": row[1],
            "code": row[2],
            "category": row[3],
            "levels_offered": levels
        })
    return trades

@app.post("/auth/hierarchical-login")
def hierarchical_login(data: Dict, db: Session = Depends(get_db)):
    """Login with hierarchical school/trade/level selection"""
    print(f"[HIERARCHICAL LOGIN] Raw data received: {data}")
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    school_id = data.get('school_id')
    trade_id = data.get('trade_id')
    level = data.get('level')
    
    print(f"[HIERARCHICAL LOGIN] After processing: username={username}, password={password}, len={len(password)}, school_id={school_id}, trade_id={trade_id}, level={level}")
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        print(f"[HIERARCHICAL LOGIN] User not found: {username}")
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    print(f"[HIERARCHICAL LOGIN] User found: {user.username}, checking password...")
    password_valid = verify_password_simple(password, user.password_hash)
    print(f"[HIERARCHICAL LOGIN] Password valid: {password_valid}")
    
    if not password_valid:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    if school_id:
        user.school_id = school_id
    if trade_id:
        user.trade_id = trade_id
    if level:
        user.level = level
    
    db.commit()
    db.refresh(user)
    
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    
    from sqlalchemy import text
    school_name = None
    trade_name = None
    
    if user.school_id:
        school_result = db.execute(text("SELECT name FROM schools WHERE id = :sid"), {"sid": user.school_id}).first()
        school_name = school_result[0] if school_result else None
    
    if user.trade_id:
        trade_result = db.execute(text("SELECT name FROM trades WHERE id = :tid"), {"tid": user.trade_id}).first()
        trade_name = trade_result[0] if trade_result else None
    
    user_dict = {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "full_name": user.full_name or "",
        "school_id": user.school_id,
        "school_name": school_name,
        "trade_id": user.trade_id,
        "trade_name": trade_name,
        "level": user.level,
        "department": user.department,
        "departments": user.departments or [],
        "is_class_teacher": bool(getattr(user, 'is_class_teacher', False))
    }
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_dict
    }

@app.get("/admin/schools/all")
def get_all_schools(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all schools with details (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view all schools")
    
    from sqlalchemy import text
    result = db.execute(text("""
        SELECT s.id, s.name, s.code, s.school_type, s.sector,
               p.name as province_name, d.name as district_name
        FROM schools s
        JOIN provinces p ON s.province_id = p.id
        JOIN districts d ON s.district_id = d.id
        WHERE s.status = 'active'
        ORDER BY p.name, d.name, s.name
    """))
    
    schools = []
    for row in result:
        schools.append({
            "id": row[0],
            "name": row[1],
            "code": row[2],
            "school_type": row[3],
            "sector": row[4],
            "province": row[5],
            "district": row[6]
        })
    
    return schools
