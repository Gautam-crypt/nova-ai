import httpx
from jarvis.core.agent_base import BaseAgent, AgentResult
from typing import Dict, Any
from jarvis.core.background.findings_queue import Finding, Priority, ActionType
from ddgs import DDGS

class HermesAgent(BaseAgent):
    def __init__(self):
        super().__init__("hermes")
        self.keywords = ["search", "find", "news", "latest", "today", "weather", "kaisa", "kya hai", "batao", "google"]

    def can_handle(self, task: Dict[str, Any]) -> bool:
        query = task.get("query", task.get("task", "")).lower()
        return any(k in query for k in self.keywords)

    def execute(self, task: Dict[str, Any]) -> AgentResult:
        query = task.get("query", task.get("task", ""))
        print(f"[HERMES] Searching web intelligence for: {query}")
        
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=3))
                if results:
                    summary = ""
                    for i, r in enumerate(results):
                        summary += f"{i+1}. {r['title']}: {r['body']}\n"
                    
                    return AgentResult(
                        agent_name=self.name,
                        success=True,
                        data=summary.strip(),
                        confidence=0.9
                    )
                
            return AgentResult(self.name, False, "No results found on the web.", 0.0)
                    
        except Exception as e:
            print(f"[ERROR] HERMES: {str(e)}")
            return AgentResult(self.name, False, f"Search failed: {str(e)}", 0.0)

    def background_scan(self) -> Finding:
        # Silently scan for news
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text("India tech news today", max_results=1))
                if results:
                    r = results[0]
                    return Finding(
                        agent_name=self.name,
                        priority=Priority.LOW,
                        title="HERMES: Found some interesting news",
                        detail=f"Bhai, check this out: {r['title']}",
                        action_type=ActionType.INFO_ONLY
                    )
        except Exception as e:
            # print(f"[BG-ERROR] HERMES: {e}")
            pass
        return None
