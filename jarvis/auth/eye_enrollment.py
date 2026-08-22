"""
jarvis/auth/eye_enrollment.py
Run: python scripts/enroll.py
"""

import cv2
import mediapipe as mp
import numpy as np
import pickle
import pathlib
import time
import sys

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions

MODEL_PATH = "data/models/face_landmarker.task"

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

SAVE_PATH = pathlib.Path("data/biometrics/eye_data")
SAVE_PATH.mkdir(parents=True, exist_ok=True)


def extract_embedding(frame: np.ndarray) -> np.ndarray | None:
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


def enroll_owner(samples: int = 150) -> bool:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Camera nahi mili.")
        return False

    print("\n" + "="*50)
    print("  JARVIS — EYE ENROLLMENT")
    print("="*50)
    print(f"Camera ko seedha dekho. {samples} samples lenge.\n")
    time.sleep(1.5)

    templates  = []
    fail_count = 0

    while len(templates) < samples:
        ret, frame = cap.read()
        if not ret:
            continue

        emb = extract_embedding(frame)

        # Live progress bar
        display  = frame.copy()
        progress = int((len(templates) / samples) * (frame.shape[1] - 40))
        cv2.rectangle(display, (20, 15), (frame.shape[1]-20, 45), (30, 30, 30), -1)
        cv2.rectangle(display, (20, 15), (20 + progress, 45), (0, 200, 80), -1)
        label = f"Capturing {len(templates)}/{samples}" if emb is not None else "Face not found — move closer"
        cv2.putText(display, label, (25, 37), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (255, 255, 255) if emb is not None else (0, 100, 255), 1)
        cv2.imshow("JARVIS Enrollment  |  Q = cancel", display)

        if emb is not None:
            templates.append(emb)
            fail_count = 0
        else:
            fail_count += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            return False

    cap.release()
    cv2.destroyAllWindows()

    arr       = np.array(templates)
    mean_tmpl = arr.mean(axis=0)
    dists     = [float(np.linalg.norm(t - mean_tmpl)) for t in arr]
    threshold = float(np.mean(dists) + 2.5 * np.std(dists))

    payload = {
        "mean":      mean_tmpl,
        "threshold": threshold,
        "samples":   samples,
    }
    out = SAVE_PATH / "owner_template.pkl"
    with open(out, "wb") as f:
        pickle.dump(payload, f)

    print(f"\n[OK] Enrollment done! Template saved -> {out}")
    print(f"[OK] Auto threshold set -> {threshold:.4f}")
    print("\nAb run karo: python main.py\n")
    return True