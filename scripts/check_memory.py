"""
scripts/check_memory.py
Simple utility to view what's stored in NOVA's ChromaDB.
"""

import chromadb
import os
import sys
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def check_db():
    db_path = "data/memory"
    if not os.path.exists(db_path):
        print(f"Error: Database path '{db_path}' not found.")
        return

    client = chromadb.PersistentClient(path=db_path)
    
    collections = client.list_collections()
    if not collections:
        print("No collections found in the database.")
        return

    print(f"\n--- NOVA MEMORY EXPLORER ---")
    for col in collections:
        print(f"\n[Collection: {col.name}]")
        data = col.get()
        
        if not data['documents']:
            print("  (Empty)")
            continue

        for i in range(len(data['documents'])):
            doc = data['documents'][i]
            meta = data['metadatas'][i] if data['metadatas'] else {}
            ts = meta.get('timestamp', 0)
            dt = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') if ts else "N/A"
            
            print(f"  > [{dt}] {doc[:200]}...")

if __name__ == "__main__":
    check_db()
