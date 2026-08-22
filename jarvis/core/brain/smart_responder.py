from jarvis.core.brain.knowledge_db import KnowledgeDB
from jarvis.core.brain.background_verifier import BackgroundVerifier, SKIP_SAVE

class SmartResponder:
    def __init__(self, orchestrator, knowledge_db: KnowledgeDB, background_verifier: BackgroundVerifier):
        self.orchestrator = orchestrator
        self.knowledge_db = knowledge_db
        self.verifier = background_verifier

    def process(self, query: str) -> str:
        # Custom testing command
        if query.lower().strip() == "nova verifier status":
            return self.verifier.status()

        # Step 1: KnowledgeDB Check
        cached_answer = self.knowledge_db.search(query)
        if cached_answer:
            print("[SmartResponder] DB HIT! Returning instant answer.")
            return cached_answer

        print("[SmartResponder] DB MISS! Routing to Orchestrator...")
        
        # Step 2: Ask local orchestrator
        agents = self.orchestrator.route_task(query)
        
        # Identify topic for agent filter
        topic = "general_qa"
        if "hermes" in agents: topic = "realtime"
        elif "divya" in agents: topic = "vision"
        elif "yama" in agents: topic = "automation"
        elif "vishwakarma" in agents: topic = "coding"
        
        task = {"query": query}
        results = self.orchestrator.execute_parallel(agents, task)
        local_answer = self.orchestrator.aggregate_results(query, results)

        # Step 3: Background Verifier (async check)
        self.verifier.verify_async(query, local_answer, topic)
        
        return local_answer
