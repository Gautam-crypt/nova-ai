import sqlite3
import os

def clean_english_responses(db_path: str = "data/nova_knowledge.db"):
    # Fix the path to be absolute or relative to the project root
    # since this script might be run from different locations
    if not os.path.isabs(db_path):
        import pathlib
        project_root = pathlib.Path(__file__).parent.parent.parent
        db_path = str(project_root / db_path)
        
    conn = sqlite3.connect(db_path)
    
    hinglish_markers = [
        "yaar","bhai","hai","nahi","kar","tha","thi",
        "hun","kya","aur","toh","arre","dekh"
    ]
    
    rows = conn.execute(
        "SELECT id, verified_answer FROM knowledge"
    ).fetchall()
    
    deleted = 0
    for row_id, answer in rows:
        answer_lower = answer.lower()
        is_hinglish = any(w in answer_lower for w in hinglish_markers)
        
        if not is_hinglish:
            conn.execute("DELETE FROM knowledge WHERE id = ?", (row_id,))
            deleted += 1
            print(f"[CLEAN] Deleted English-only entry: {answer[:60]}...")
    
    conn.commit()
    conn.close()
    print(f"[CLEAN] Done — {deleted} English entries removed from DB")

if __name__ == "__main__":
    clean_english_responses()
