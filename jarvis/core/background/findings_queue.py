from dataclasses import dataclass, field
from enum import Enum
import queue
import time
from typing import Any, List, Optional, Callable

class Priority(Enum):
    LOW    = 3   # Higher value means lower priority in queue.PriorityQueue
    MEDIUM = 2
    HIGH   = 1

class ActionType(Enum):
    INFO_ONLY   = "info"
    NEEDS_PERMISSION = "permission"

@dataclass(order=True)
class Finding:
    priority_val: int = field(init=False)
    priority: Priority = field(compare=False)
    agent_name: str = field(compare=False)
    title: str = field(compare=False)
    detail: str = field(compare=False)
    action_type: ActionType = field(compare=False)
    action_fn: Optional[Callable] = field(default=None, compare=False)
    timestamp: float = field(default_factory=time.time, compare=False)

    def __post_init__(self):
        self.priority_val = self.priority.value

class FindingsQueue:
    """Thread-safe priority queue for agent findings"""
    def __init__(self):
        self._queue = queue.PriorityQueue()
        self._low_priority_storage = []

    def push(self, finding: Finding):
        """Push a finding into the queue"""
        if finding.priority == Priority.LOW:
            self._low_priority_storage.append(finding)
        else:
            self._queue.put(finding)

    def pop_highest(self) -> Optional[Finding]:
        """Pop the highest priority finding (non-blocking)"""
        try:
            return self._queue.get_nowait()
        except queue.Empty:
            return None

    def pop_all_low(self) -> List[Finding]:
        """Drain low priority findings for summary"""
        findings = self._low_priority_storage[:]
        self._low_priority_storage.clear()
        return findings

    def size(self) -> int:
        """Total size of queue (excluding low priority storage)"""
        return self._queue.qsize() + len(self._low_priority_storage)
