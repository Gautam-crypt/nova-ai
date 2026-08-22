"""
jarvis/core/brain/memory.py
Long-term Memory for NOVA using ChromaDB.
Stores conversation history and extracted facts.
"""

import chromadb
from chromadb.config import Settings
import os
import uuid
import time

class LongTermMemory:
    def __init__(self, db_path="data/memory"):
        os.makedirs(db_path, exist_ok=True)
        # Initialize Persistent Client
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Collection for general conversation history
        self.conv_history = self.client.get_or_create_collection(
            name="conversation_history",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Collection for specific facts about the owner
        self.facts = self.client.get_or_create_collection(
            name="owner_facts",
            metadata={"hnsw:space": "cosine"}
        )
        
        print(f"[MEMORY] Long-term memory initialized at {db_path}")

    def store_interaction(self, user_text: str, nova_text: str):
        """Stores a full interaction (User + Nova)."""
        combined = f"User: {user_text}\nNOVA: {nova_text}"
        self.conv_history.add(
            documents=[combined],
            ids=[str(uuid.uuid4())],
            metadatas=[{"timestamp": time.time()}]
        )

    def store_fact(self, fact: str):
        """Stores a specific fact about the user (e.g., 'Sir likes coffee')."""
        self.facts.add(
            documents=[fact],
            ids=[str(uuid.uuid4())],
            metadatas=[{"timestamp": time.time()}]
        )

    def retrieve_relevant(self, query: str, n_results: int = 3) -> str:
        """Searches both history and facts for relevant context."""
        context = []
        
        # Search Facts
        if self.facts.count() > 0:
            fact_results = self.facts.query(
                query_texts=[query],
                n_results=min(2, self.facts.count())
            )
            if fact_results['documents'] and fact_results['documents'][0]:
                context.append("RELEVANT FACTS:\n" + "\n".join(fact_results['documents'][0]))
            
        # Search History
        if self.conv_history.count() > 0:
            hist_results = self.conv_history.query(
                query_texts=[query],
                n_results=min(n_results, self.conv_history.count())
            )
            if hist_results['documents'] and hist_results['documents'][0]:
                context.append("PAST CONVERSATIONS:\n" + "\n".join(hist_results['documents'][0]))
            
        return "\n\n".join(context) if context else ""

    def clear(self):
        """Wipes the memory clean."""
        self.client.delete_collection("conversation_history")
        self.client.delete_collection("owner_facts")
        print("[MEMORY] All memories cleared.")
