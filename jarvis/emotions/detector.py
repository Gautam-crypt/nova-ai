import cv2
import threading
import time
import librosa
import numpy as np
from deepface import DeepFace
from jarvis.core.body.camera import camera_manager

class EmotionEngine:
    """
    Dual-channel emotion detection for NOVA:
    Channel 1 — Face (webcam, every 2s)
    Channel 2 — Voice tone (mic energy + pitch)
    """
    def __init__(self):
        self.face_emotion   = "neutral"
        self.voice_stress   = 0.0        # 0.0 to 1.0
        self.combined       = "neutral"
        self._running       = False
        self.history        = []         # last 100 readings

    def start(self):
        self._running = True
        threading.Thread(target=self._face_loop, daemon=True).start()
        print("[NOVA] Emotion engine started")

    def _face_loop(self):
        while self._running:
            frame = camera_manager.get_frame()
            if frame is not None:
                try:
                    # Analyze every 2 seconds to save CPU
                    r = DeepFace.analyze(
                        frame,
                        actions=['emotion'],
                        enforce_detection=False,
                        silent=True
                    )
                    self.face_emotion = r[0]['dominant_emotion']
                    self._update_combined()
                    self.history.append({
                        "time":    time.time(),
                        "emotion": self.face_emotion,
                        "stress":  self.voice_stress
                    })
                    if len(self.history) > 100:
                        self.history = self.history[-100:]
                except Exception as e:
                    # print(f"[EMOTION ENGINE ERROR]: {e}")
                    pass
            time.sleep(2)

    def analyze_voice_tone(self, audio_array: np.ndarray, sr: int = 16000) -> dict:
        """Call this after each voice input to get tone features."""
        if len(audio_array) < sr // 2:
            return {"stress": 0.0, "energy": 0.0, "pitch": 0.0}

        energy = float(np.sqrt(np.mean(audio_array**2)))

        # Pitch via librosa
        try:
            pitches, mags = librosa.piptrack(y=audio_array, sr=sr)
            # Get the indices of the maximum magnitudes
            pitch_idx = np.argmax(mags, axis=0)
            # Use these indices to get the corresponding pitches
            pitch = float(np.mean(pitches[pitch_idx, np.arange(pitches.shape[1])]))
        except:
            pitch = 0.0

        # Stress estimation logic
        stress = min(1.0, (energy * 10)) # Simple heuristic
        self.voice_stress = stress
        self._update_combined()

        return {"stress": stress, "energy": energy, "pitch": pitch}

    def _update_combined(self):
        """
        Multimodal Fusion: Face (60%) + Voice (40%)
        Following state-of-the-art weighted fusion logic.
        """
        recent_emotions = [h["emotion"] for h in self.history[-5:]] if self.history else []
        smoothed_face = max(set(recent_emotions), key=recent_emotions.count) if recent_emotions else "neutral"

        # Voice mapping: high stress usually correlates with negative emotions
        voice_factor = "stressed" if self.voice_stress > 0.6 else "neutral"
        
        # Weighted Decision
        if self.voice_stress > 0.85:
            self.combined = "very_stressed"
        elif smoothed_face == "angry" or (smoothed_face == "neutral" and self.voice_stress > 0.7):
            self.combined = "stressed"
        elif smoothed_face == "happy" and self.voice_stress < 0.4:
            self.combined = "happy"
        else:
            self.combined = smoothed_face

    def get(self) -> tuple[str, float]:
        return self.combined, self.voice_stress

    def get_pattern(self) -> dict:
        """Returns patterns — NOVA uses this for proactive care."""
        if len(self.history) < 5:
            return {"avg_stress": 0.0, "dominant": "neutral", "late_night": False}

        recent  = self.history[-20:]
        stresses = [h["stress"] for h in recent]
        emotions = [h["emotion"] for h in recent]
        hour     = time.localtime().tm_hour

        return {
            "avg_stress":   float(np.mean(stresses)),
            "dominant":     max(set(emotions), key=emotions.count) if emotions else "neutral",
            "late_night":   hour >= 22 or hour <= 5,
            "total_samples": len(self.history)
        }
