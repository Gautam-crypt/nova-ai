"""
scripts/setup_nova.py
Initializes NOVA's memory with real identity facts.
Run this once to 'train' her behavior.
"""

import chromadb
import os
import uuid
import time

def setup():
    db_path = "data/memory"
    os.makedirs(db_path, exist_ok=True)
    client = chromadb.PersistentClient(path=db_path)
    
    # Collection for facts
    facts = client.get_or_create_collection(name="owner_facts")
    
    # Clear old junk to avoid confusion
    print("[SETUP] Cleaning old identity data...")
    # (Optional: client.delete_collection("owner_facts"))
    
    identity_facts = [
        "User name is Gautam. He is the owner and master of NOVA.",
        "Gautam is Hindu. Never use Muslim greetings like Assalamu alaikum. Use Namaste or Kya haal hai.",
        "Gautam likes UP-style Hinglish. Speak like a local from UP/Delhi (Bhai, Arre, Scene, System).",
        "NOVA is a female AI assistant, witty, loyal, and very desi in her talk.",
        "Gautam lives in UP and prefers a companion-like tone, not a robotic servant tone.",
        "Strict Rule: No formal Hindi. No Salaam. Only casual, friendly Hinglish."
    ]
    
    print("[SETUP] Injecting real identity facts into database...")
    for fact in identity_facts:
        facts.add(
            documents=[fact],
            ids=[str(uuid.uuid4())],
            metadatas=[{"source": "manual_setup", "timestamp": time.time()}]
        )
        
    print("[SETUP] Done! NOVA now knows exactly who you are and how to speak.")

if __name__ == "__main__":
    setup()
