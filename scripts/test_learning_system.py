import sys
import pathlib
import time
import os

# Make jarvis/ importable
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv('c:/Users/GAUTAM/Desktop/Project X/.env')

import chromadb
from jarvis.core.learning.knowledge_db import KnowledgeDB
from jarvis.core.learning.background_verifier import BackgroundVerifier
from jarvis.core.learning.smart_responder import SmartResponder

class DummyOrchestrator:
    def process(self, query: str):
        # Mocks the local LLM answer (gemma)
        print("  [Dummy Orchestrator] Generating local answer...")
        time.sleep(1)
        if "asman neela" in query.lower():
            return "Asman neela hota hai kyunki sooraj ki roshni bikhar jati hai (Rayleigh scattering)."
        return "Mujhe lagta hai yeh theek hai."

def run_test():
    print("=== INITIALIZING SELF LEARNING SYSTEM ===")
    chroma_client = chromadb.PersistentClient(path="./data/chroma_test")
    knowledge_db = KnowledgeDB(chroma_client=chroma_client, db_path="data/nova_knowledge_test.db")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY is missing!")
        return
        
    verifier = BackgroundVerifier(knowledge_db=knowledge_db, openai_api_key=api_key)
    orchestrator = DummyOrchestrator()
    
    smart = SmartResponder(orchestrator=orchestrator, knowledge_db=knowledge_db, verifier=verifier)
    
    question = "Asman neela kyun hota hai?"
    
    print("\n--- TURN 1: Naya Sawal (No DB Hit Expected) ---")
    result1 = smart.respond(question)
    print(f"Result 1 Answer: {result1['answer']}")
    print(f"Source: {result1['source']}")
    
    print("\n[Waiting 5 seconds for Background Verifier to call Groq and save to DB...]")
    # Wait for the background thread to finish calling the LLM API
    for _ in range(10):
        if verifier.pending_count() == 0:
            break
        time.sleep(1)
        
    print("\n--- TURN 2: Same Sawal (DB Hit Expected) ---")
    result2 = smart.respond(question)
    print(f"Result 2 Answer: {result2['answer']}")
    print(f"Source: {result2['source']}")
    print(f"DB Hit: {result2['db_hit']}")
    if result2['db_hit']:
        print(f"Quality Score from Groq: {result2['quality_score']}")
        
    print("\n--- SYSTEM STATS ---")
    stats = knowledge_db.stats()
    print(f"Total Entries in DB: {stats['total_entries']}")
    print(f"API Calls Saved: {stats['api_calls_saved']}")
    print("Test Complete.")

if __name__ == "__main__":
    run_test()
