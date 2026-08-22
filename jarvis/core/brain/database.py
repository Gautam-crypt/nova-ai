"""
jarvis/core/brain/database.py
Structured SQL Database for NOVA using SQLite.
Stores user profiles, settings, and permanent rules.
"""

import sqlite3
import os

class NovaDB:
    def __init__(self, db_path="data/nova_system.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._setup_tables()
        self._init_default_profile()

    def _setup_tables(self):
        # User Profile Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS profile (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        # Reminders / Tasks Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def _init_default_profile(self):
        """Sets up Gautam's profile if it doesn't exist."""
        defaults = [
            ('user_name', 'Gautam'),
            ('religion', 'Hindu'),
            ('language_style', 'UP-style Hinglish'),
            ('greeting_pref', 'Namaste / Kya haal hai'),
            ('identity_locked', 'True')
        ]
        for key, val in defaults:
            self.cursor.execute('INSERT OR IGNORE INTO profile (key, value) VALUES (?, ?)', (key, val))
        self.conn.commit()

    def get_profile_value(self, key):
        self.cursor.execute('SELECT value FROM profile WHERE key = ?', (key,))
        res = self.cursor.fetchone()
        return res[0] if res else None

    def update_profile(self, key, value):
        self.cursor.execute('INSERT OR REPLACE INTO profile (key, value) VALUES (?, ?)', (key, value))
        self.conn.commit()

    def add_task(self, task_text):
        self.cursor.execute('INSERT INTO tasks (task) VALUES (?)', (task_text,))
        self.conn.commit()
        return f"Task '{task_text}' save kar liya hai, Sir."

    def get_pending_tasks(self):
        self.cursor.execute('SELECT task FROM tasks WHERE status = "pending"')
        return [row[0] for row in self.cursor.fetchall()]

# Global Instance
db = NovaDB()
