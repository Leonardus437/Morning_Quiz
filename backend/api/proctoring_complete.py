"""
Proctoring API - WebSocket + REST
Real-time violation detection and session management
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
from datetime import datetime
import json
import base64

from core.database import get_db
from services.proctoring.engine_complete import get_proctor_engine, ViolationEvent
from models.proctoring import ProctoringSession, ProctoringViolation, KeystrokePattern, ScreenActivity

router = APIRouter()

# Active WebSocket connections
active_connections: Dict[int, WebSocket] = {}

@router.websocket("/ws/proctor/{session_id}")
async def proctoring_websocket(websocket: WebSocket, session_id: int, db: Session = Depends(get_db)):
    """
    Real-time proctoring WebSocket
    Client sends: video frames, audio chunks, keystroke data
    Server sends: violation alerts, risk score updates
    """
    await websocket.accept()
    active_connections[session_id] = websocket
    
    engine = get_proctor_engine()
    
    if not engine.enabled:
        await websocket.send_json({
            "status": "disabled",
            "message": "Proctoring not enabled on server"
        })
        await websocket.close()
        return
    
    print(f"🔒 Proctoring session {session_id} started")
    
    try:
        while True:
            # Receive data from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            msg_type = message.get("type")
            
            if msg_type == "video_frame":
                # Analyze video frame
                frame_base64 = message.get("frame")
                frame_bytes = base64.b64decode(frame_base64)
                
                result = engine.analyze_frame(frame_bytes)
                
                # Save violations to database
                if result.get("violations"):
                    for violation in result["violations"]:
                        db_violation = ProctoringViolation(
                            session_id=session_id,
                            violation_type=violation["type"],
                            confidence=violation["confidence"],
                            details=violation.get("details"),
                            timestamp=datetime.fromisoformat(violation["timestamp"])
                        )
                        db.add(db_violation)
                    
                    # Update session violation counts
                    session = db.query(ProctoringSession).filter(
                        ProctoringSession.id == session_id
                    ).first()
                    
                    if session:
                        session.total_violations += len(result["violations"])
                        for v in result["violations"]:
                            if v["type"] == "FACE_ABSENT":
                                session.face_absent_count += 1
                            elif v["type"] == "MULTIPLE_FACES":
                                session.multiple_faces_count += 1
                            elif v["type"] == "LOOKING_AWAY":
                                session.looking_away_count += 1
                            elif v["type"] == "FORBIDDEN_OBJECT":
                                session.forbidden_object_count += 1
                        
                        # Calculate risk score
                        session.risk_score = engine.calculate_risk_score(result["violations"])
                        if session.risk_score > 70:
                            session.is_flagged = True
                    
                    db.commit()
                
                # Send response to client
                await websocket.send_json({
                    "type": "analysis_result",
                    "violations": result.get("violations", []),
                    "metrics": result.get("metrics", {}),
                    "risk_score": result.get("risk_score", 0)
                })
            
            elif msg_type == "audio_chunk":
                # Analyze audio
                audio_base64 = message.get("audio")
                audio_bytes = base64.b64decode(audio_base64)
                
                violation = engine.analyze_audio(audio_bytes)
                if violation:
                    db_violation = ProctoringViolation(
                        session_id=session_id,
                        violation_type=violation.type,
                        confidence=violation.confidence,
                        details=violation.details
                    )
                    db.add(db_violation)
                    db.commit()
                    
                    await websocket.send_json({
                        "type": "violation_alert",
                        "violation": violation.dict()
                    })
            
            elif msg_type == "keystroke":
                # Store keystroke pattern
                keystroke = KeystrokePattern(
                    session_id=session_id,
                    user_id=message.get("user_id"),
                    key_down_time=message.get("key_down_time"),
                    key_up_time=message.get("key_up_time"),
                    key_code=message.get("key_code")
                )
                db.add(keystroke)
                db.commit()
            
            elif msg_type == "screen_activity":
                # Track tab switches, window blur, etc.
                activity = ScreenActivity(
                    session_id=session_id,
                    activity_type=message.get("activity_type"),
                    duration_seconds=message.get("duration", 0)
                )
                db.add(activity)
                
                # Update session
                session = db.query(ProctoringSession).filter(
                    ProctoringSession.id == session_id
                ).first()
                if session and message.get("activity_type") == "TAB_SWITCH":
                    session.tab_switch_count += 1
                
                db.commit()
                
                # Alert client
                await websocket.send_json({
                    "type": "warning",
                    "message": "Tab switching detected - this is a violation"
                })
            
            elif msg_type == "ping":
                # Heartbeat
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        print(f"🔓 Proctoring session {session_id} ended")
        if session_id in active_connections:
            del active_connections[session_id]
    
    except Exception as e:
        print(f"Proctoring WebSocket error: {e}")
        await websocket.close()

@router.post("/sessions/start")
def start_proctoring_session(
    quiz_attempt_id: int,
    user_id: int,
    quiz_id: int,
    device_info: Dict,
    db: Session = Depends(get_db)
):
    """Start a new proctoring session"""
    session = ProctoringSession(
        quiz_attempt_id=quiz_attempt_id,
        user_id=user_id,
        quiz_id=quiz_id,
        device_info=device_info,
        started_at=datetime.utcnow()
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return {
        "session_id": session.id,
        "message": "Proctoring session started",
        "websocket_url": f"/ws/proctor/{session.id}"
    }

@router.post("/sessions/{session_id}/end")
def end_proctoring_session(session_id: int, db: Session = Depends(get_db)):
    """End proctoring session and calculate final risk score"""
    session = db.query(ProctoringSession).filter(
        ProctoringSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.ended_at = datetime.utcnow()
    session.duration_seconds = int((session.ended_at - session.started_at).total_seconds())
    
    # Get all violations
    violations = db.query(ProctoringViolation).filter(
        ProctoringViolation.session_id == session_id
    ).all()
    
    # Calculate final risk score
    engine = get_proctor_engine()
    violation_dicts = [{"type": v.violation_type, "confidence": v.confidence} for v in violations]
    session.risk_score = engine.calculate_risk_score(violation_dicts)
    
    if session.risk_score > 70:
        session.is_flagged = True
    
    db.commit()
    
    return {
        "session_id": session.id,
        "duration_seconds": session.duration_seconds,
        "total_violations": session.total_violations,
        "risk_score": session.risk_score,
        "is_flagged": session.is_flagged
    }

@router.get("/sessions/{session_id}/report")
def get_proctoring_report(session_id: int, db: Session = Depends(get_db)):
    """Get detailed proctoring report"""
    session = db.query(ProctoringSession).filter(
        ProctoringSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    violations = db.query(ProctoringViolation).filter(
        ProctoringViolation.session_id == session_id
    ).order_by(ProctoringViolation.timestamp).all()
    
    screen_activities = db.query(ScreenActivity).filter(
        ScreenActivity.session_id == session_id
    ).all()
    
    return {
        "session_id": session.id,
        "user_id": session.user_id,
        "quiz_id": session.quiz_id,
        "started_at": session.started_at.isoformat() if session.started_at else None,
        "ended_at": session.ended_at.isoformat() if session.ended_at else None,
        "duration_seconds": session.duration_seconds,
        "risk_score": session.risk_score,
        "is_flagged": session.is_flagged,
        "violation_summary": {
            "total": session.total_violations,
            "face_absent": session.face_absent_count,
            "multiple_faces": session.multiple_faces_count,
            "looking_away": session.looking_away_count,
            "forbidden_objects": session.forbidden_object_count,
            "audio_anomalies": session.audio_anomaly_count,
            "tab_switches": session.tab_switch_count
        },
        "violations": [
            {
                "type": v.violation_type,
                "confidence": v.confidence,
                "timestamp": v.timestamp.isoformat(),
                "details": v.details
            }
            for v in violations
        ],
        "screen_activities": [
            {
                "type": a.activity_type,
                "timestamp": a.timestamp.isoformat(),
                "duration": a.duration_seconds
            }
            for a in screen_activities
        ]
    }

@router.get("/status")
def get_proctoring_status():
    """Check if proctoring is enabled and working"""
    engine = get_proctor_engine()
    return {
        "enabled": engine.enabled,
        "dependencies_loaded": engine._mediapipe is not None,
        "active_sessions": len(active_connections)
    }
