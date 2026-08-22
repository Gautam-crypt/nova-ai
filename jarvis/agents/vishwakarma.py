import ollama
from jarvis.core.agent_base import BaseAgent, AgentResult
from typing import Dict, Any
import os
import py_compile
from jarvis.core.background.findings_queue import Finding, Priority, ActionType

class VishwakarmaAgent(BaseAgent):
    def __init__(self):
        super().__init__("vishwakarma")
        self.keywords = ["code", "function", "bug", "error", "script", "python", "fix", "debug", "implement"]
        self.model = "qwen2.5:7b"
        self.system_prompt = "You are an expert coding assistant. Give short, working code with brief explanation."

    def can_handle(self, task: Dict[str, Any]) -> bool:
        query = task.get("query", task.get("task", "")).lower()
        return any(k in query for k in self.keywords)

    def execute(self, task: Dict[str, Any]) -> AgentResult:
        query = task.get("query", task.get("task", ""))
        print(f"[VISHWAKARMA] Engineering code solution: {query}")
        
        try:
            response = ollama.generate(
                model=self.model,
                prompt=query,
                system=self.system_prompt,
                options={"temperature": 0.2}
            )
            
            return AgentResult(
                agent_name=self.name,
                success=True,
                data=response['response'].strip(),
                confidence=0.9
            )
        except Exception as e:
            print(f"[ERROR] VISHWAKARMA: {str(e)}")
            return AgentResult(self.name, False, str(e), 0.0)

    def background_scan(self) -> Finding:
        # Silently check code health
        try:
            # Scan last modified .py files in current directory
            py_files = [f for f in os.listdir('.') if f.endswith('.py')]
            for f in py_files:
                try:
                    py_compile.compile(f, doraise=True)
                except py_compile.PyCompileError as e:
                    return Finding(
                        agent_name=self.name,
                        priority=Priority.MEDIUM,
                        title=f"VISHWAKARMA: Syntax error in {f}",
                        detail=f"I found a syntax error while scanning your code: {str(e)[:100]}...",
                        action_type=ActionType.INFO_ONLY
                    )
        except Exception as e:
            print(f"[BG-ERROR] VISHWAKARMA: {e}")
        return None
