"""
Pillar C: On-Device AI Proctoring Engine
Lazy-loaded only when PROCTORING_ENABLED=true
"""
from typing import Dict, Optional
from pydantic import BaseModel
from datetime import datetime

class ViolationEvent(BaseModel):
    """Standardized violation event"""
    type: str  # ABSENT, MULTIPLE_FACES, LOOKING_AWAY, FORBIDDEN_OBJECT, AUDIO_ANOMALY
    confidence: float
    timestamp: datetime
    details: Optional[str] = None

class ProctorEngine:
    """Lightweight proctoring engine with lazy module loading"""
    
    def __init__(self):
        self._mediapipe = None
        self._cv2 = None
        self._onnx = None
        self.enabled = False
    
    def _load_mediapipe(self):
        """Lazy load MediaPipe"""
        if self._mediapipe is None:
            try:
                import mediapipe as mp
                self._mediapipe = mp
                self.face_mesh = mp.solutions.face_mesh.FaceMesh(
                    max_num_faces=2,
                    refine_landmarks=False,
                    min_detection_confidence=0.5
                )
                print("✅ MediaPipe loaded")
            except ImportError:
                print("⚠️ MediaPipe not available")
        return self._mediapipe
    
    def _load_cv2(self):
        """Lazy load OpenCV"""
        if self._cv2 is None:
            try:
                import cv2
                self._cv2 = cv2
                print("✅ OpenCV loaded")
            except ImportError:
                print("⚠️ OpenCV not available")
        return self._cv2
    
    def analyze_frame(self, frame_bytes: bytes) -> Dict:
        """Analyze single frame for violations"""
        if not self.enabled:
            return {"violations": [], "status": "disabled"}
        
        violations = []
        
        try:
            # Lazy load dependencies
            mp = self._load_mediapipe()
            cv2 = self._load_cv2()
            
            if not mp or not cv2:
                return {"violations": [], "status": "dependencies_missing"}
            
            # Decode frame
            import numpy as np
            nparr = np.frombuffer(frame_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return {"violations": [], "status": "invalid_frame"}
            
            # Convert to RGB for MediaPipe
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Face detection
            results = self.face_mesh.process(rgb)
            
            if not results.multi_face_landmarks:
                violations.append(ViolationEvent(
                    type="ABSENT",
                    confidence=0.9,
                    timestamp=datetime.utcnow(),
                    details="No face detected"
                ))
            elif len(results.multi_face_landmarks) > 1:
                violations.append(ViolationEvent(
                    type="MULTIPLE_FACES",
                    confidence=0.95,
                    timestamp=datetime.utcnow(),
                    details=f"{len(results.multi_face_landmarks)} faces detected"
                ))
            
            return {
                "violations": [v.dict() for v in violations],
                "status": "ok",
                "faces_detected": len(results.multi_face_landmarks) if results.multi_face_landmarks else 0
            }
        
        except Exception as e:
            print(f"Proctoring error: {e}")
            return {"violations": [], "status": "error", "error": str(e)}
    
    def enable(self):
        """Enable proctoring and preload models"""
        self.enabled = True
        self._load_mediapipe()
        self._load_cv2()
        print("🔒 Proctoring enabled")
    
    def disable(self):
        """Disable proctoring"""
        self.enabled = False
        print("🔓 Proctoring disabled")

# Global instance (lazy-initialized)
_engine: Optional[ProctorEngine] = None

def get_proctor_engine() -> ProctorEngine:
    """Get or create proctoring engine"""
    global _engine
    if _engine is None:
        _engine = ProctorEngine()
        from core.config import settings
        if settings.PROCTORING_ENABLED:
            _engine.enable()
    return _engine
