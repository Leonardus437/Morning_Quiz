"""
Proctoring Database Models
Tracks all violations during offline exams
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ProctoringSession(Base):
    """Track each exam session with proctoring"""
    __tablename__ = "proctoring_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_attempt_id = Column(Integer, ForeignKey("quiz_attempts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    
    # Session info
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    duration_seconds = Column(Integer)
    
    # Violation summary
    total_violations = Column(Integer, default=0)
    face_absent_count = Column(Integer, default=0)
    multiple_faces_count = Column(Integer, default=0)
    looking_away_count = Column(Integer, default=0)
    forbidden_object_count = Column(Integer, default=0)
    audio_anomaly_count = Column(Integer, default=0)
    tab_switch_count = Column(Integer, default=0)
    
    # Risk score (0-100)
    risk_score = Column(Float, default=0.0)
    is_flagged = Column(Boolean, default=False)
    
    # Device info
    device_info = Column(JSON)  # Browser, OS, screen resolution
    
class ProctoringViolation(Base):
    """Individual violation events"""
    __tablename__ = "proctoring_violations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("proctoring_sessions.id"))
    
    # Violation details
    violation_type = Column(String(50))  # ABSENT, MULTIPLE_FACES, LOOKING_AWAY, etc.
    confidence = Column(Float)  # 0.0 to 1.0
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(Text)
    
    # Evidence (optional)
    frame_snapshot = Column(Text)  # Base64 encoded image
    
class KeystrokePattern(Base):
    """Behavioral biometrics - typing patterns"""
    __tablename__ = "keystroke_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("proctoring_sessions.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Keystroke timing data
    key_down_time = Column(Float)  # milliseconds
    key_up_time = Column(Float)
    key_code = Column(String(10))
    
    # Behavioral analysis
    is_anomalous = Column(Boolean, default=False)
    anomaly_score = Column(Float)
    
    timestamp = Column(DateTime, default=datetime.utcnow)

class ScreenActivity(Base):
    """Track screen/tab switching"""
    __tablename__ = "screen_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("proctoring_sessions.id"))
    
    activity_type = Column(String(50))  # TAB_SWITCH, WINDOW_BLUR, FULLSCREEN_EXIT
    timestamp = Column(DateTime, default=datetime.utcnow)
    duration_seconds = Column(Integer)
