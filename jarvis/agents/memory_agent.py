import chromadb
from jarvis.core.agent_base import BaseAgent, AgentResult
from typing import Dict, Any

class MemoryAgent(BaseAgent):
    def __init__(self, chroma_client=None):
        super().__init__("memory_agent")
        try:
            self.client = chroma_client or chromadb.PersistentClient(path="./data/chroma")
            self.collection = self.client.get_or_create_collection(name="nova_memory")
        except Exception as e:
            print(f"[ERROR] memory_agent: ChromaDB init failed: {str(e)}")
            self.collection = None

    def can_handle(self, task: Dict[str, Any]) -> bool:
        # Fallback agent, always returns True
        return True

    def execute(self, task: Dict[str, Any]) -> AgentResult:
        print(f"[{self.name.upper()}] Searching memory...")
        query = task.get("query", task.get("task", ""))
        
        if not self.collection:
            return AgentResult(self.name, False, "ChromaDB not initialized", 0.0)
            
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=2
            )
            
            documents = results.get("documents", [[]])[0]
            if documents:
                memory_str = " | ".join(documents)
                return AgentResult(
                    agent_name=self.name,
                    success=True,
                    data=f"Past Context: {memory_str}",
                    confidence=0.6
                )
            else:
                return AgentResult(self.name, True, "No relevant past context found.", 0.6)
                
        except Exception as e:
            print(f"[ERROR] {self.name}: {str(e)}")
            return AgentResult(self.name, False, str(e), 0.0)
