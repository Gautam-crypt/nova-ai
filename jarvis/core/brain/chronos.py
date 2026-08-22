"""
jarvis/core/brain/chronos.py
CHRONOS — Predictive Intelligence Engine.
Learns the user's daily patterns and proactively suggests actions.
Stores history locally in SQLite.
"""
import sqlite3
import time
from datetime import datetime
from pathlib import Path


class Chronos:
    def __init__(self, db_path: str = "data/chronos.db"):
        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()
    
    def _init_db(self):
        """Create schema for pattern tracking."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT, 
                hour INTEGER, 
                day_of_week INTEGER,
                action_type TEXT, 
                action_detail TEXT,
                emotion TEXT, 
                app_in_use TEXT
            )
        """)
        self.db.commit()
    
    def record(self, action_type: str, action_detail: str, 
               emotion: str = "neutral", app: str = ""):
        """
        Record a user action for pattern learning.
        Call this whenever the user gives a command or performs a significant action.
        """
        now = datetime.now()
        try:
            self.db.execute(
                """INSERT INTO patterns 
                   (timestamp, hour, day_of_week, action_type, action_detail, emotion, app_in_use)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (now.isoformat(), now.hour, now.weekday(), 
                 action_type, action_detail, emotion, app)
            )
            self.db.commit()
        except Exception as e:
            print(f"[CHRONOS] Error recording pattern: {e}")
    
    def predict_next_action(self) -> str:
        """
        Based on the current time and day, what does the user usually do?
        Returns a predictive suggestion.
        """
        now = datetime.now()
        try:
            rows = self.db.execute(
                """SELECT action_type, action_detail, COUNT(*) as cnt
                   FROM patterns 
                   WHERE hour = ? AND day_of_week = ?
                   GROUP BY action_type, action_detail
                   ORDER BY cnt DESC LIMIT 1""",
                (now.hour, now.weekday())
            ).fetchall()
            
            if not rows:
                return None
                
            most_common = rows[0]
            # Need at least 3 occurrences to consider it a strong pattern
            if most_common[2] >= 3:
                return f"Usually at {now.strftime('%I %p')} on {now.strftime('%A')}, you focus on: {most_common[1]}"
                
        except Exception as e:
            print(f"[CHRONOS] Prediction error: {e}")
            
        return None
    
    def detect_anomaly(self) -> str:
        """
        Detect if current behavior deviates from normal patterns (e.g., awake at 3 AM).
        """
        now = datetime.now()
        try:
            # Check how much activity usually happens at this hour
            result = self.db.execute(
                """SELECT COUNT(*) FROM patterns 
                   WHERE hour = ?""",
                (now.hour,)
            ).fetchone()
            
            usual_activity = result[0] if result else 0
            
            # If zero past activity and it's late night
            if usual_activity == 0 and 1 <= now.hour <= 5:
                return "Bhai, tu is waqt usually soya hota hai. Neend nahi aa rahi kya? Sab theek hai?"
                
        except Exception as e:
            print(f"[CHRONOS] Anomaly detection error: {e}")
            
        return None
