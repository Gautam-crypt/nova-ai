import chromadb
from jarvis.core.agent_base import BaseAgent, AgentResult
from typing import Dict, Any

class LibrarianAgent(BaseAgent):
    """
    Agent responsible for storing information into Long-Term Memory.
    Activated when the user says "remember this", "save this", or "feed this into your database".
    """
    def __init__(self, chroma_client=None):
        super().__init__("librarian")
        try:
            self.client = chroma_client or chromadb.PersistentClient(path="./data/chroma")
            self.collection = self.client.get_or_create_collection(name="nova_memory")
        except Exception as e:
            print(f"[ERROR] librarian: ChromaDB init failed: {str(e)}")
            self.collection = None

        self.keywords = ["save", "remember", "feed", "store", "index", "database mein", "yaad rakho", "seekho"]

    def can_handle(self, task: Dict[str, Any]) -> bool:
        query = task.get("query", task.get("task", "")).lower()
        return any(k in query for k in self.keywords)

    def execute(self, task: Dict[str, Any]) -> AgentResult:
        query = task.get("query", task.get("task", ""))
        content_to_save = task.get("content_to_save")
        
        if not content_to_save:
            # If no specific content, try to extract from query
            # (e.g., "save that the meeting is at 5pm")
            content_to_save = query
            
        print(f"[LIBRARIAN] Feeding information into long-term memory...")
        
        if not self.collection:
            return AgentResult(self.name, False, "ChromaDB not initialized", 0.0)
            
        try:
            import uuid
            self.collection.add(
                documents=[content_to_save],
                ids=[str(uuid.uuid4())],
                metadatas=[{"source": "user_request", "type": "learned_fact"}]
            )
            
            return AgentResult(
                agent_name=self.name,
                success=True,
                data=f"I have successfully stored that information in my long-term memory, Sir. I will recall it when needed.",
                confidence=1.0
            )
                
        except Exception as e:
            print(f"[ERROR] LIBRARIAN: {str(e)}")
            return AgentResult(self.name, False, str(e), 0.0)
