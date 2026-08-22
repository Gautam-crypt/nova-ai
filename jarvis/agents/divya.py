import cv2
import ollama
import os
import tempfile
import time
import threading
from jarvis.core.agent_base import BaseAgent, AgentResult
from jarvis.core.body.camera import camera_manager
from typing import Dict, Any
from jarvis.core.background.findings_queue import Finding, Priority, ActionType

# Safe MediaPipe Import
HAS_MEDIAPIPE = False
try:
    import mediapipe as mp
    # Try legacy solutions
    if hasattr(mp, 'solutions'):
        mp_face = mp.solutions.face_detection
        mp_pose = mp.solutions.pose
        HAS_MEDIAPIPE = True
    else:
        # Try tasks API as fallback for newer versions
        from mediapipe.tasks import python as mp_python
        from mediapipe.tasks.python import vision
        HAS_MEDIAPIPE = "tasks"
except Exception as e:
    # print(f"[DIVYA] MediaPipe initialization failed: {e}. Falling back to standard vision.")
    pass

class DivyaAgent(BaseAgent):
    """
    DIVYA: Real-time Vision Intelligence.
    Uses LLaVA for semantic analysis and MediaPipe (if available) for tracking.
    """
    def __init__(self):
        super().__init__("divya")
        self.keywords = ["dekh", "camera", "kya dikh", "describe", "screen", "image", "photo", "see", "watch", "posture", "expression"]
        self.vision_model = "llava"
        
        # Tracking Initialization
        self.has_tracking = False
        if HAS_MEDIAPIPE == True:
            try:
                self.face_detector = mp_face.FaceDetection(model_selection=0, min_detection_confidence=0.5)
                self.pose_detector = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5)
                self.has_tracking = True
            except:
                self.has_tracking = False
            
        self.last_seen_time = time.time()
        self.current_scene_description = "Awaiting visual data."
        self.last_semantic_scan = 0
        
    def can_handle(self, task: Dict[str, Any]) -> bool:
        query = task.get("query", task.get("task", "")).lower()
        return any(k in query for k in self.keywords)

    def execute(self, task: Dict[str, Any]) -> AgentResult:
        query = task.get("query", task.get("task", ""))
        print(f"[DIVYA] Executing deep visual analysis: {query}")
        
        frame = camera_manager.get_frame()
        if frame is None:
            return AgentResult(self.name, False, "I can't access the camera right now, Sir.", 0.0)
            
        try:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                cv2.imwrite(tmp.name, frame)
                img_path = tmp.name
            
            print(f"[DIVYA] Analyzing frame with {self.vision_model}...")
            response = ollama.generate(
                model=self.vision_model,
                prompt=(
                    "TASK: Look at the webcam frame carefully. "
                    "Describe exactly what you see: posture, facial expression, clothing, and objects. "
                    "Be specific. If you see a person, describe their appearance and mood."
                ),
                images=[img_path]
            )
            
            if os.path.exists(img_path):
                os.remove(img_path)
            
            res_data = response['response'].strip()
            print(f"[DIVYA] Model Output: {res_data}")
            
            return AgentResult(
                agent_name=self.name,
                success=True,
                data=res_data,
                confidence=1.0
            )
        except Exception as e:
            print(f"[ERROR] DIVYA: {str(e)}")
            return AgentResult(self.name, False, f"Vision analysis failed: {str(e)}", 0.0)

    def background_scan(self) -> Finding:
        frame = camera_manager.get_frame()
        if frame is None:
            return None

        # 1. Spatial Tracking
        if self.has_tracking:
            try:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_results = self.face_detector.process(rgb_frame)
                if face_results and face_results.detections:
                    self.last_seen_time = time.time()
            except:
                pass
        else:
            self.last_seen_time = time.time()

        # 2. Semantic Analysis (LLaVA) - Every 60 seconds
        finding = None
        if time.time() - self.last_semantic_scan > 60:
            self.last_semantic_scan = time.time()
            try:
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                    cv2.imwrite(tmp.name, frame)
                    img_path = tmp.name
                
                res = ollama.generate(
                    model=self.vision_model,
                    prompt="Describe the user's current posture and mood in 5 words.",
                    images=[img_path]
                )
                self.current_scene_description = res['response'].strip()
                
                if os.path.exists(img_path):
                    os.remove(img_path)
                
                if any(word in self.current_scene_description.lower() for word in ["tired", "sleeping", "stressed", "slumped"]):
                    finding = Finding(
                        agent_name=self.name,
                        priority=Priority.MEDIUM,
                        title="DIVYA: Visual health check",
                        detail="Bhai thoda stretch kar le — screen se thoda break le 🪑",
                        action_type=ActionType.INFO_ONLY
                    )
            except:
                pass
                
        return finding
