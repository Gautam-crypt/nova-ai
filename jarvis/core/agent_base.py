from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import threading
from typing import Any, Dict

class AgentStatus(Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"

@dataclass
class AgentResult:
    agent_name: str
    success: bool
    data: Any
    confidence: float

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.status = AgentStatus.IDLE
        self._lock = threading.Lock()

    @abstractmethod
    def can_handle(self, task: Dict[str, Any]) -> bool:
        """Determine if this agent can handle the given task."""
        pass

    @abstractmethod
    def execute(self, task: Dict[str, Any]) -> AgentResult:
        """Execute the task and return result."""
        pass

    def run(self, task: Dict[str, Any]) -> AgentResult:
        """Thread-safe execution wrapper."""
        with self._lock:
            self.status = AgentStatus.RUNNING
            print(f"[AGENT] {self.name} started processing task...")
            try:
                result = self.execute(task)
                self.status = AgentStatus.DONE if result.success else AgentStatus.FAILED
                print(f"[AGENT] {self.name} finished: {'Success' if result.success else 'Failed'}")
                return result
            except Exception as e:
                self.status = AgentStatus.FAILED
                print(f"[ERROR] {self.name} encountered an error: {str(e)}")
                return AgentResult(
                    agent_name=self.name,
                    success=False,
                    data={"error": str(e)},
                    confidence=0.0
                )
