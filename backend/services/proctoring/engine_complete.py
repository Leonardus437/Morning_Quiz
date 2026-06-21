"""
Complete Offline AI Proctoring Engine
Detects: Face presence, Multiple people, Gaze direction, Forbidden objects, Audio anomalies
"""
from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime
import numpy as np

class ViolationEvent(BaseModel):
    type: str
    confidence: float
    timestamp: datetime
    details: Optional[str] = None
    frame_snapshot: Optional[str] = None

class ProctorEngine:
    """Complete AI proctoring with lazy loading"""
    
    def __init__(self):
        self._mediapipe = None
        self._cv2 = None
        self._face_mesh = None
        self.enabled = False
        self.face_absent_threshold = 5  # seconds
        self.gaze_threshold = 30  # degrees
        self.last_face_time = None
        
    def _load_dependencies(self):
        """Lazy load all ML dependencies"""
        if self._mediapipe is None:
            try:
                import mediapipe as mp
                import cv2
                
                self._mediapipe = mp
                self._cv2 = cv2
                
                # Initialize face mesh for detection and gaze
                self._face_mesh = mp.solutions.face_mesh.FaceMesh(
                    max_num_faces=3,
                    refine_landmarks=True,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                
                print("✅ Proctoring engine loaded (MediaPipe + OpenCV)")
                return True
            except ImportError as e:
                print(f"⚠️ Proctoring dependencies missing: {e}")
                return False
        return True
    
    def analyze_frame(self, frame_bytes: bytes) -> Dict:
        """
        Analyze single video frame for violations
        Returns: {violations: [...], status: str, metrics: {...}}
        """
        if not self.enabled:
            return {"violations": [], "status": "disabled"}
        
        if not self._load_dependencies():
            return {"violations": [], "status": "dependencies_missing"}
        
        violations = []
        metrics = {}
        
        try:
            # Decode frame
            nparr = np.frombuffer(frame_bytes, np.uint8)
            img = self._cv2.imdecode(nparr, self._cv2.IMREAD_COLOR)
            
            if img is None:
                return {"violations": [], "status": "invalid_frame"}
            
            # Convert to RGB for MediaPipe
            rgb = self._cv2.cvtColor(img, self._cv2.COLOR_BGR2RGB)
            h, w, _ = rgb.shape
            
            # Process with MediaPipe
            results = self._face_mesh.process(rgb)
            
            # 1. FACE PRESENCE CHECK
            if not results.multi_face_landmarks:
                violations.append(ViolationEvent(
                    type="FACE_ABSENT",
                    confidence=0.95,
                    timestamp=datetime.utcnow(),
                    details="No face detected in frame"
                ))
                metrics["faces_detected"] = 0
            else:
                num_faces = len(results.multi_face_landmarks)
                metrics["faces_detected"] = num_faces
                
                # 2. MULTIPLE FACES CHECK
                if num_faces > 1:
                    violations.append(ViolationEvent(
                        type="MULTIPLE_FACES",
                        confidence=0.98,
                        timestamp=datetime.utcnow(),
                        details=f"{num_faces} faces detected - possible impersonation"
                    ))
                
                # 3. GAZE DIRECTION CHECK (using first face)
                face_landmarks = results.multi_face_landmarks[0]
                gaze_violation = self._check_gaze_direction(face_landmarks, w, h)
                if gaze_violation:
                    violations.append(gaze_violation)
                    metrics["gaze_status"] = "looking_away"
                else:
                    metrics["gaze_status"] = "focused"
            
            # 4. OBJECT DETECTION (simplified - checks for phone-like shapes)
            object_violation = self._detect_forbidden_objects(img)
            if object_violation:
                violations.append(object_violation)
            
            return {
                "violations": [v.dict() for v in violations],
                "status": "ok",
                "metrics": metrics,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            print(f"Proctoring error: {e}")
            return {"violations": [], "status": "error", "error": str(e)}
    
    def _check_gaze_direction(self, face_landmarks, img_width, img_height) -> Optional[ViolationEvent]:
        """
        Check if student is looking away from screen
        Uses nose tip and eye positions to estimate gaze
        """
        try:
            # Key landmarks for gaze estimation
            nose_tip = face_landmarks.landmark[1]  # Nose tip
            left_eye = face_landmarks.landmark[33]  # Left eye
            right_eye = face_landmarks.landmark[263]  # Right eye
            
            # Convert to pixel coordinates
            nose_x = nose_tip.x * img_width
            nose_y = nose_tip.y * img_height
            
            left_eye_x = left_eye.x * img_width
            right_eye_x = right_eye.x * img_width
            
            # Calculate horizontal gaze deviation
            eye_center_x = (left_eye_x + right_eye_x) / 2
            horizontal_deviation = abs(nose_x - eye_center_x)
            
            # Threshold: if nose is too far from eye center, looking away
            if horizontal_deviation > img_width * 0.15:  # 15% of image width
                return ViolationEvent(
                    type="LOOKING_AWAY",
                    confidence=0.85,
                    timestamp=datetime.utcnow(),
                    details=f"Gaze deviation: {int(horizontal_deviation)}px"
                )
            
            return None
        except Exception as e:
            print(f"Gaze check error: {e}")
            return None
    
    def _detect_forbidden_objects(self, img) -> Optional[ViolationEvent]:
        """
        Detect forbidden objects (phones, books, etc.)
        Simplified version using color/shape detection
        """
        try:
            # Convert to HSV for better object detection
            hsv = self._cv2.cvtColor(img, self._cv2.COLOR_BGR2HSV)
            
            # Detect phone-like rectangular objects (simplified)
            gray = self._cv2.cvtColor(img, self._cv2.COLOR_BGR2GRAY)
            edges = self._cv2.Canny(gray, 50, 150)
            contours, _ = self._cv2.findContours(edges, self._cv2.RETR_EXTERNAL, self._cv2.CHAIN_APPROX_SIMPLE)
            
            # Look for rectangular contours (potential phones/tablets)
            for contour in contours:
                area = self._cv2.contourArea(contour)
                if 1000 < area < 50000:  # Phone-sized objects
                    x, y, w, h = self._cv2.boundingRect(contour)
                    aspect_ratio = float(w) / h
                    
                    # Phones typically have aspect ratio 0.4-0.7
                    if 0.3 < aspect_ratio < 0.8:
                        return ViolationEvent(
                            type="FORBIDDEN_OBJECT",
                            confidence=0.70,
                            timestamp=datetime.utcnow(),
                            details="Rectangular object detected (possible phone/tablet)"
                        )
            
            return None
        except Exception as e:
            print(f"Object detection error: {e}")
            return None
    
    def analyze_audio(self, audio_chunk: bytes) -> Optional[ViolationEvent]:
        """
        Detect audio anomalies (talking, external voices)
        Uses simple energy-based detection
        """
        try:
            # Convert audio bytes to numpy array
            audio_data = np.frombuffer(audio_chunk, dtype=np.int16)
            
            # Calculate RMS energy
            rms = np.sqrt(np.mean(audio_data**2))
            
            # Threshold for speech detection (adjust based on testing)
            if rms > 500:  # Arbitrary threshold
                return ViolationEvent(
                    type="AUDIO_ANOMALY",
                    confidence=0.75,
                    timestamp=datetime.utcnow(),
                    details=f"Audio activity detected (RMS: {int(rms)})"
                )
            
            return None
        except Exception as e:
            print(f"Audio analysis error: {e}")
            return None
    
    def analyze_keystroke_pattern(self, keystroke_data: List[Dict]) -> Dict:
        """
        Behavioral biometrics - detect if typing pattern is anomalous
        Returns: {is_anomalous: bool, score: float}
        """
        try:
            if len(keystroke_data) < 10:
                return {"is_anomalous": False, "score": 0.0, "reason": "insufficient_data"}
            
            # Extract timing features
            dwell_times = []  # Time key is held down
            flight_times = []  # Time between key releases
            
            for i, keystroke in enumerate(keystroke_data):
                dwell = keystroke.get('key_up_time', 0) - keystroke.get('key_down_time', 0)
                dwell_times.append(dwell)
                
                if i > 0:
                    flight = keystroke.get('key_down_time', 0) - keystroke_data[i-1].get('key_up_time', 0)
                    flight_times.append(flight)
            
            # Calculate statistics
            avg_dwell = np.mean(dwell_times)
            std_dwell = np.std(dwell_times)
            avg_flight = np.mean(flight_times) if flight_times else 0
            
            # Simple anomaly detection: very fast typing or very slow typing
            if avg_dwell < 30 or avg_dwell > 500:  # milliseconds
                return {
                    "is_anomalous": True,
                    "score": 0.8,
                    "reason": f"Unusual typing speed (avg dwell: {avg_dwell:.0f}ms)"
                }
            
            return {"is_anomalous": False, "score": 0.0}
        
        except Exception as e:
            print(f"Keystroke analysis error: {e}")
            return {"is_anomalous": False, "score": 0.0, "error": str(e)}
    
    def calculate_risk_score(self, violations: List[Dict]) -> float:
        """
        Calculate overall risk score (0-100) based on violations
        """
        if not violations:
            return 0.0
        
        # Weighted scoring
        weights = {
            "MULTIPLE_FACES": 30,
            "FACE_ABSENT": 15,
            "LOOKING_AWAY": 10,
            "FORBIDDEN_OBJECT": 25,
            "AUDIO_ANOMALY": 15,
            "TAB_SWITCH": 20
        }
        
        score = 0.0
        for violation in violations:
            v_type = violation.get("type", "")
            confidence = violation.get("confidence", 0.5)
            weight = weights.get(v_type, 10)
            score += weight * confidence
        
        return min(score, 100.0)
    
    def enable(self):
        """Enable proctoring"""
        self.enabled = True
        self._load_dependencies()
        print("🔒 AI Proctoring ENABLED")
    
    def disable(self):
        """Disable proctoring"""
        self.enabled = False
        print("🔓 AI Proctoring DISABLED")

# Global singleton
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
