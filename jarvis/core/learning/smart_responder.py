from .knowledge_db import KnowledgeDB
from .background_verifier import BackgroundVerifier
import time


class SmartResponder:
    """
    Single entry point for all NOVA responses.
    
    Priority order:
    1. KnowledgeDB (permanent verified answers) — instant, zero API
    2. Local Orchestrator (Hermes, Vishwakarma, etc. via gemma3:4b/qwen2.5:7b)
    3. Background verification → DB mein save (for next time)
    """
    
    def __init__(self, orchestrator, knowledge_db: KnowledgeDB, verifier: BackgroundVerifier):
        self.orchestrator = orchestrator
        self.db = knowledge_db
        self.verifier = verifier
        self._turn_count = 0
    
    def respond(self, question: str) -> dict:
        """
        Returns:
        {
            "answer":        str,
            "source":        "db" | "local_orchestrator",
            "db_hit":        bool,
            "quality_score": float | None,
            "times_used":    int | None
        }
        """
        self._turn_count += 1
        
        # STEP 1 — DB check (permanent knowledge)
        entry = self.db.search(question, threshold=0.85)
        if entry:
            print(f"\\n[SMART] [OK] DB HIT — similarity: {entry['similarity']:.2f}, used {entry['times_used']}x before, topic: {entry['topic_tag']}")
            return {
                "answer":        entry["verified_answer"],
                "source":        "db",
                "db_hit":        True,
                "quality_score": entry["quality_score"],
                "times_used":    entry["times_used"]
            }
        
        # STEP 2 — Local Orchestrator
        print(f"\\n[SMART] DB miss — routing query via Orchestrator...")
        start_time = time.time()
        local_answer = self.orchestrator.process(question)
        elapsed = time.time() - start_time
        print(f"[SMART] Orchestrator finished in {elapsed:.2f}s")
        
        # STEP 3 — Background verify + save to DB (async)
        self.verifier.verify_async(question, local_answer)
        
        # Every 10 turns — print DB growth stats
        if self._turn_count % 10 == 0:
            stats = self.db.stats()
            print(f"\\n[SMART] DB stats — {stats['total_entries']} entries, {stats['api_calls_saved']} calls saved, ~${stats['estimated_cost_saved']} saved")
        
        return {
            "answer":        local_answer,
            "source":        "local_orchestrator",
            "db_hit":        False,
            "quality_score": None,
            "times_used":    None
        }
