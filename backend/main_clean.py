from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
import json

# Environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://quiz_user:quiz_pass@localhost:5432/quiz_db")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
OFFLINE_MODE = os.getenv("OFFLINE_MODE", "true").lower() == "true"

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Quiz(Base):
    __tablename__ = "quizzes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text, nullable=True)
    duration = Column(Integer)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    question_text = Column(Text)
    option_a = Column(String)
    option_b = Column(String)
    option_c = Column(String)
    option_d = Column(String)
    correct_answer = Column(String)
    points = Column(Integer, default=1)

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    score = Column(Float)
    total_questions = Column(Integer)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(title="TVET Quiz API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auth functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Pydantic schemas
class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    role: str
    full_name: Optional[str] = None

class QuizCreate(BaseModel):
    title: str
    description: Optional[str] = None
    duration: int

class QuestionCreate(BaseModel):
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str
    points: int = 1

# Routes
@app.get("/")
def root():
    return {"message": "TVET Quiz API", "offline_mode": OFFLINE_MODE}

@app.post("/api/auth/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer", "role": user.role, "username": user.username}

@app.post("/api/users")
def create_user(user: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can create users")
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, password=hashed_password, role=user.role, full_name=user.full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"id": db_user.id, "username": db_user.username, "role": db_user.role}

@app.get("/api/users/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username, "role": current_user.role, "full_name": current_user.full_name}

@app.post("/api/quizzes")
def create_quiz(quiz: QuizCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can create quizzes")
    db_quiz = Quiz(title=quiz.title, description=quiz.description, duration=quiz.duration, created_by=current_user.id)
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    return {"id": db_quiz.id, "title": db_quiz.title}

@app.get("/api/quizzes")
def get_quizzes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    quizzes = db.query(Quiz).filter(Quiz.is_active == True).all()
    return [{"id": q.id, "title": q.title, "description": q.description, "duration": q.duration} for q in quizzes]

@app.post("/api/quizzes/{quiz_id}/questions")
def add_question(quiz_id: int, question: QuestionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can add questions")
    db_question = Question(quiz_id=quiz_id, **question.dict())
    db.add(db_question)
    db.commit()
    return {"message": "Question added"}

@app.get("/api/quizzes/{quiz_id}/questions")
def get_questions(quiz_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()
    result = []
    for q in questions:
        question_data = {
            "id": q.id,
            "question_text": q.question_text,
            "option_a": q.option_a,
            "option_b": q.option_b,
            "option_c": q.option_c,
            "option_d": q.option_d,
            "points": q.points
        }
        if current_user.role == "teacher":
            question_data["correct_answer"] = q.correct_answer
        result.append(question_data)
    return result

@app.post("/api/quizzes/{quiz_id}/submit")
def submit_quiz(quiz_id: int, answers: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()
    score = 0
    total = len(questions)
    for q in questions:
        if str(q.id) in answers and answers[str(q.id)] == q.correct_answer:
            score += q.points
    attempt = QuizAttempt(quiz_id=quiz_id, student_id=current_user.id, score=score, total_questions=total, completed_at=datetime.utcnow())
    db.add(attempt)
    db.commit()
    return {"score": score, "total": total, "percentage": (score/total*100) if total > 0 else 0}

@app.get("/api/leaderboard/{quiz_id}")
def get_leaderboard(quiz_id: int, db: Session = Depends(get_db)):
    attempts = db.query(QuizAttempt, User).join(User, QuizAttempt.student_id == User.id).filter(QuizAttempt.quiz_id == quiz_id).order_by(QuizAttempt.score.desc()).limit(10).all()
    return [{"username": user.username, "full_name": user.full_name, "score": attempt.score, "total": attempt.total_questions} for attempt, user in attempts]

# Initialize default admin
@app.on_event("startup")
def startup():
    db = SessionLocal()
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        hashed = get_password_hash("pass123")
        admin = User(username="admin", password=hashed, role="teacher", full_name="Administrator")
        db.add(admin)
        db.commit()
    db.close()
