import threading
from typing import Callable, Dict, List, Any

class MessageBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._lock = threading.Lock()

    def subscribe(self, topic: str, callback: Callable[[Any], None]):
        """Subscribe a callback to a specific topic."""
        with self._lock:
            if topic not in self._subscribers:
                self._subscribers[topic] = []
            self._subscribers[topic].append(callback)
            print(f"[NOVA] Subscribed to topic: {topic}")

    def publish(self, topic: str, data: Any):
        """Publish data to all subscribers of a topic."""
        with self._lock:
            if topic in self._subscribers:
                print(f"[NOVA] Publishing to topic: {topic}")
                for callback in self._subscribers[topic]:
                    try:
                        # Callbacks should ideally be lightweight or async
                        callback(data)
                    except Exception as e:
                        print(f"[ERROR] Error in callback for topic {topic}: {str(e)}")
            else:
                print(f"[NOVA] No subscribers for topic: {topic}")
