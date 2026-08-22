import sqlite3
import chromadb
import hashlib
import time
import json
from pathlib import Path

class KnowledgeDB:
    """
    Dual-store knowledge base:
    - SQLite: full structured data (question, answer, score, metadata)
    - ChromaDB: semantic vector search (find similar questions)
    
    Together they give NOVA permanent self-learning memory.
    """
    
    def __init__(self, chroma_client: chromadb.ClientAPI, db_path: str = "data/nova_knowledge.db"):
        
        # SQLite — permanent structured storage
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self._init_sqlite()
        
        # ChromaDB — semantic similarity search
        self.chroma = chroma_client
        self.collection = self.chroma.get_or_create_collection(
            name="nova_knowledge",
            metadata={"hnsw:space": "cosine"}
        )
        
        print(f"[KNOWLEDGE_DB] Loaded — {self.total_entries()} verified answers in DB")
    
    def _init_sqlite(self):
        """Create tables if not exist"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id              TEXT PRIMARY KEY,
                question        TEXT NOT NULL,
                local_answer    TEXT NOT NULL,
                verified_answer TEXT NOT NULL,
                quality_score   REAL NOT NULL,
                corrections     INTEGER DEFAULT 0,
                times_used      INTEGER DEFAULT 0,
                source          TEXT DEFAULT 'openai_verified',
                topic_tag       TEXT,
                saved_at        REAL NOT NULL,
                last_used_at    REAL
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS learning_stats (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                date            TEXT NOT NULL,
                api_calls_saved INTEGER DEFAULT 0,
                new_entries     INTEGER DEFAULT 0,
                total_entries   INTEGER DEFAULT 0,
                UNIQUE(date)
            )
        """)
        self.conn.commit()
    
    def search(self, question: str, threshold: float = 0.85) -> dict | None:
        """
        Semantic search — similar question DB mein hai?
        Returns full knowledge entry or None.
        """
        try:
            results = self.collection.query(
                query_texts=[question],
                n_results=1,
                include=["distances", "metadatas"]
            )
            
            if not results["ids"] or not results["ids"][0]:
                return None
            
            distance   = results["distances"][0][0]
            similarity = 1 - distance
            
            if similarity < threshold:
                return None
            
            entry_id = results["ids"][0][0]
            
            # SQLite se full data lo
            row = self.conn.execute(
                "SELECT id, question, local_answer, verified_answer, quality_score, corrections, times_used, source, topic_tag, saved_at FROM knowledge WHERE id = ?", 
                (entry_id,)
            ).fetchone()
            
            if not row:
                return None
            
            # times_used update karo
            self.conn.execute(
                """UPDATE knowledge 
                   SET times_used = times_used + 1,
                       last_used_at = ?
                   WHERE id = ?""",
                (time.time(), entry_id)
            )
            self.conn.commit()
            
            return {
                "id":               row[0],
                "question":         row[1],
                "local_answer":     row[2],
                "verified_answer":  row[3],
                "quality_score":    row[4],
                "corrections_made": bool(row[5]),
                "times_used":       row[6] + 1,
                "source":           row[7],
                "topic_tag":        row[8],
                "similarity":       similarity
            }
        except Exception as e:
            print(f"[KNOWLEDGE_DB] Search error: {e}")
            return None
    
    def save(self, question: str, local_answer: str,
             verified_answer: str, quality_score: float,
             corrections_made: bool, source: str = "openai_verified",
             topic_tag: str = None):
        """
        Permanently save to BOTH SQLite and ChromaDB.
        Upsert — same question aaya toh update karo, duplicate nahi.
        """
        entry_id = hashlib.md5(question.lower().strip().encode()).hexdigest()
        now = time.time()
        
        # SQLite mein save
        self.conn.execute("""
            INSERT INTO knowledge 
                (id, question, local_answer, verified_answer, 
                 quality_score, corrections, times_used, 
                 source, topic_tag, saved_at)
            VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                verified_answer = excluded.verified_answer,
                quality_score   = excluded.quality_score,
                corrections     = excluded.corrections,
                source          = excluded.source,
                topic_tag       = excluded.topic_tag
        """, (entry_id, question, local_answer, verified_answer,
              quality_score, int(corrections_made), 
              source, topic_tag, now))
        self.conn.commit()
        
        # ChromaDB mein save (vector embedding ke liye)
        self.collection.upsert(
            ids=[entry_id],
            documents=[question],
            metadatas=[{
                "entry_id":     entry_id,
                "quality_score": str(quality_score),
                "topic_tag":    topic_tag or "general",
                "source":       source
            }]
        )
        
        print(f"[KNOWLEDGE_DB] [OK] Permanently saved — "
              f"score: {quality_score:.2f}, tag: {topic_tag}")
        
        # Stats update
        self._update_daily_stats(new_entry=True)
    
    def total_entries(self) -> int:
        row = self.conn.execute(
            "SELECT COUNT(*) FROM knowledge"
        ).fetchone()
        return row[0] if row else 0
    
    def top_used(self, limit: int = 5) -> list:
        """Most frequently used knowledge entries"""
        rows = self.conn.execute("""
            SELECT question, times_used, quality_score, topic_tag
            FROM knowledge
            ORDER BY times_used DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [{"question": r[0], "times_used": r[1],
                 "quality": r[2], "tag": r[3]} for r in rows]
    
    def stats(self) -> dict:
        total  = self.total_entries()
        row    = self.conn.execute(
            "SELECT SUM(times_used) FROM knowledge"
        ).fetchone()
        saved  = row[0] or 0
        
        # Topic distribution
        topics = self.conn.execute("""
            SELECT topic_tag, COUNT(*) as cnt
            FROM knowledge
            GROUP BY topic_tag
            ORDER BY cnt DESC
            LIMIT 5
        """).fetchall()
        
        return {
            "total_entries":        total,
            "api_calls_saved":      saved,
            "estimated_cost_saved": round(saved * 0.0003, 4),  # gpt-4o-mini estimate
            "top_topics":           [(r[0], r[1]) for r in topics]
        }
    
    def _update_daily_stats(self, new_entry: bool = False,
                             api_saved: bool = False):
        from datetime import date
        today = str(date.today())
        total = self.total_entries()
        
        self.conn.execute("""
            INSERT INTO learning_stats (date, api_calls_saved, new_entries, total_entries)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                api_calls_saved = api_calls_saved + excluded.api_calls_saved,
                new_entries     = new_entries + excluded.new_entries,
                total_entries   = excluded.total_entries
        """, (today, int(api_saved), int(new_entry), total))
        self.conn.commit()
