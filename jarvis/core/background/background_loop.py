import threading
import time
from typing import Dict
from .findings_queue import FindingsQueue

class BackgroundAgentLoop:
    """
    Runs each agent on its own daemon thread with a configurable interval.
    Agents push Findings to the shared FindingsQueue.
    """
    
    def __init__(self, findings_queue: FindingsQueue, agents: Dict):
        self.queue = findings_queue
        self.agents = agents
        self._threads = {}
        self._running = False
    
    def start(self):
        """Start all agent background threads"""
        self._running = True
        intervals = {
            "hermes":       300,   # every 5 min — web scan
            "vishwakarma":  600,   # every 10 min — code health
            "divya":        60,    # every 1 min — screen watch
            "yama":         120,   # every 2 min — system monitor
            "manas":        30,    # every 30 sec — mood check
            "memory_agent": 600    # Default for others
        }
        
        for name, agent in self.agents.items():
            # Only start if agent has background_scan method
            if hasattr(agent, 'background_scan'):
                interval = intervals.get(name, 120)
                t = threading.Thread(
                    target=self._agent_loop,
                    args=(name, agent, interval),
                    daemon=True,
                    name=f"bg_{name}"
                )
                t.start()
                self._threads[name] = t
                print(f"[BG] {name.upper()} background thread started (interval: {interval}s)")
    
    def _agent_loop(self, name, agent, interval):
        """Each agent runs its background_scan() on a timer"""
        while self._running:
            try:
                finding = agent.background_scan()
                if finding:
                    self.queue.push(finding)
                    print(f"[BG] {name.upper()} pushed finding: {finding.title}")
            except Exception as e:
                print(f"[BG-ERROR] {name}: {e}")
            
            # Check every second for shutdown responsiveness
            for _ in range(interval):
                if not self._running:
                    break
                time.sleep(1)
    
    def stop(self):
        self._running = False
        print("[BG] All background threads stopping...")
    
    def status(self) -> dict:
        """Return status of all background threads"""
        return {
            name: "alive" if t.is_alive() else "dead"
            for name, t in self._threads.items()
        }
