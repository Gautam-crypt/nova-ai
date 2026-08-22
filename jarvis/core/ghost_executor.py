"""
jarvis/core/ghost_executor.py
Ghost Mode — Silent, invisible task execution.
When activated, NOVA executes tasks in the background without any visible UI, 
sound, or console output.
"""
import queue
import threading

class GhostExecutor:
    def __init__(self, react_engine):
        self.react_engine = react_engine
        self.active = False
        self.task_queue = queue.Queue()
        self.results = []
        self._worker_thread = None
    
    def activate(self):
        self.active = True
        self.results = []
        self._worker_thread = threading.Thread(target=self._process_queue, daemon=True, name="ghost_worker")
        self._worker_thread.start()
        print("[GHOST] Mode activated — NOVA is now operating silently.")
    
    def deactivate(self) -> list:
        self.active = False
        print("[GHOST] Mode deactivated.")
        return self.results
    
    def add_task(self, task: str):
        self.task_queue.put(task)
        if not self.active:
            print("[GHOST] Task queued, but ghost mode is inactive.")
            
    def status(self) -> str:
        return f"Ghost Mode: {'ACTIVE' if self.active else 'INACTIVE'} | Queued Tasks: {self.task_queue.qsize()}"
    
    def _process_queue(self):
        while self.active:
            try:
                task = self.task_queue.get(timeout=1)
                
                # Suppress voice/sound output during execution
                original_speak = self.react_engine.speak
                original_permission = self.react_engine.ask_permission
                
                self.react_engine.speak = lambda x: None  # Mute TTS
                
                # In Ghost mode, we auto-grant permission for queued tasks since
                # the user explicitly sent them to background/ghost mode,
                # or we fail gracefully if we don't want to grant blind permission.
                # Here we auto-deny any destructive action that wasn't pre-approved
                # to prevent silent disasters.
                self.react_engine.ask_permission = lambda: "no" 
                
                # Process the task silently
                result = self.react_engine.process(task)
                
                self.results.append({"task": task, "result": result})
                
                # Restore original functions
                self.react_engine.speak = original_speak
                self.react_engine.ask_permission = original_permission
                
            except queue.Empty:
                continue
            except Exception as e:
                self.results.append({"task": "unknown", "result": f"Ghost Error: {str(e)}"})
