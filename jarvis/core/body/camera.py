import cv2
import threading
import time

class CameraManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(CameraManager, cls).__new__(cls)
                cls._instance.cap = None
                cls._instance.last_frame = None
                cls._instance.running = False
        return cls._instance

    def get_frame(self):
        """Thread-safe way to get the latest frame without multiple opens."""
        with self._lock:
            if self.cap is None or not self.cap.isOpened():
                self.cap = cv2.VideoCapture(0)
            
            ret, frame = self.cap.read()
            if ret:
                self.last_frame = frame
                return frame
            return self.last_frame

    def release(self):
        with self._lock:
            if self.cap:
                self.cap.release()
                self.cap = None

camera_manager = CameraManager()
