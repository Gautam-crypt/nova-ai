"""
jarvis/core/senses/vision/eye_auth.py
"""

import cv2
import mediapipe as mp
import numpy as np
import pickle
import pathlib
import sys
import msvcrt # Windows-specific for keyboard detection

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions

MODEL_PATH = "data/models/face_landmarker.task"
TEMPLATE_PATH = pathlib.Path("data/biometrics/eye_data/owner_template.pkl")

# Pre-flight check
if not pathlib.Path(MODEL_PATH).exists():
    print(f"[ERROR] Model file missing: {MODEL_PATH}")
    print("Please download it first using the provided command.")
    sys.exit(1)

options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    num_faces=1,
    output_face_blendshapes=False,
    output_facial_transformation_matrixes=False
)
face_landmarker = FaceLandmarker.create_from_options(options)

LEFT_IRIS  = [474, 475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]
LEFT_EYE   = [33, 133, 160, 159, 158, 144, 145, 153]
RIGHT_EYE  = [362, 263, 387, 386, 385, 373, 374, 380]

THRESHOLD_MULT = 1.1   # Still intense, but humanly possible
MAX_ATTEMPTS   = 300   # Give more time to align properly


def _embed(frame: np.ndarray) -> np.ndarray | None:
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    results = face_landmarker.detect(mp_image)
    if not results.face_landmarks:
        return None

    h, w = frame.shape[:2]
    lm = results.face_landmarks[0]

    face_width = abs(lm[234].x - lm[454].x) * w
    if face_width < 10:
        return None

    def get_norm(indices):
        pts = np.array([[lm[i].x * w, lm[i].y * h] for i in indices], dtype=np.float32)
        center = pts.mean(axis=0)
        return ((pts - center) / face_width).flatten()

    return np.concatenate([
        get_norm(LEFT_IRIS),
        get_norm(RIGHT_IRIS),
        get_norm(LEFT_EYE),
        get_norm(RIGHT_EYE),
    ])


def verify_eye(show_window: bool = True) -> tuple[bool, float]:
    if not TEMPLATE_PATH.exists():
        print("[ERROR] Template nahi mila. Pehle chalao: python scripts/enroll.py")
        return False, 0.0

    with open(TEMPLATE_PATH, "rb") as f:
        data = pickle.load(f)

    mean_tmpl = data["mean"]
    threshold = data["threshold"] * THRESHOLD_MULT

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Camera accessible nahi hai.")
        return False, 0.0

    streak    = 0
    NEED      = 10      # 10 consecutive matches = verified (intense but fair)
    best_dist = float("inf")

    for attempt in range(MAX_ATTEMPTS):
        ret, frame = cap.read()
        if not ret:
            continue

        emb   = _embed(frame)
        color = (80, 80, 80)
        label = "Scanning..."

        if emb is not None:
            dist      = float(np.linalg.norm(emb - mean_tmpl))
            best_dist = min(best_dist, dist)

            if dist < threshold:
                streak += 1
                color   = (0, 220, 80)
                label   = f"Match {streak}/{NEED}"
            else:
                streak = 0
                color  = (0, 120, 255)
                label  = f"Checking... ({dist:.2f}/{threshold:.2f})"

            if streak >= NEED:
                cap.release()
                if show_window:
                    cv2.destroyAllWindows()
                conf = max(0.0, 1.0 - (best_dist / threshold))
                print(f"[AUTH] PASS — confidence {conf:.1%}")
                return True, conf
        else:
            streak = 0
            label  = "Face not detected — camera ke paas aao"

        if show_window:
            display = frame.copy()
            cv2.rectangle(display, (0, 0), (frame.shape[1], 55), (18, 18, 18), -1)
            cv2.putText(display, f"JARVIS AUTH  |  {label}",
                        (14, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2)
            # timeout bar
            bar = int((attempt / MAX_ATTEMPTS) * frame.shape[1])
            cv2.rectangle(display, (0, 50), (bar, 55), (60, 60, 60), -1)
            cv2.imshow("JARVIS — Identity Verification  |  Q = exit", display)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            # If user hits any other key, switch to password mode
            if msvcrt.kbhit():
                print("\n[AUTH] Keyboard hit detected. Switching to password mode...")
                cap.release()
                if show_window:
                    cv2.destroyAllWindows()
                return "PASSWORD_MODE", 0.0

    cap.release()
    if show_window:
        cv2.destroyAllWindows()
    print(f"[AUTH] FAIL — best dist {best_dist:.4f}, threshold {threshold:.4f}")
    return False, 0.0