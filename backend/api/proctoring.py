"""
Proctoring WebSocket API
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from services.proctoring.engine import get_proctor_engine
import json

router = APIRouter()

@router.websocket("/ws/proctor")
async def proctoring_websocket(websocket: WebSocket):
    """Real-time proctoring WebSocket"""
    await websocket.accept()
    engine = get_proctor_engine()
    
    if not engine.enabled:
        await websocket.send_json({"status": "disabled", "message": "Proctoring not enabled"})
        await websocket.close()
        return
    
    try:
        while True:
            # Receive frame from client
            data = await websocket.receive_bytes()
            
            # Analyze frame
            result = engine.analyze_frame(data)
            
            # Send back violations
            await websocket.send_json(result)
    
    except WebSocketDisconnect:
        print("Proctoring WebSocket disconnected")
    except Exception as e:
        print(f"Proctoring WebSocket error: {e}")
        await websocket.close()

@router.get("/proctor/status")
def get_proctor_status():
    """Check if proctoring is enabled"""
    engine = get_proctor_engine()
    return {
        "enabled": engine.enabled,
        "mediapipe_loaded": engine._mediapipe is not None,
        "opencv_loaded": engine._cv2 is not None
    }
