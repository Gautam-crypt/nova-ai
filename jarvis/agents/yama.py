import os
import subprocess
import platform
from jarvis.core.agent_base import BaseAgent, AgentResult
from typing import Dict, Any
import psutil
import shutil
from jarvis.core.background.findings_queue import Finding, Priority, ActionType

class YamaAgent(BaseAgent):
    def __init__(self):
        super().__init__("yama")
        self.keywords = ["open", "close", "folder", "file", "copy", "delete", "move", "notepad", "calculator", "browser", "khol", "band"]

    def can_handle(self, task: Dict[str, Any]) -> bool:
        query = task.get("query", task.get("task", "")).lower()
        return any(k in query for k in self.keywords)

    def execute(self, task: Dict[str, Any]) -> AgentResult:
        query = task.get("query", task.get("task", "")).lower()
        print(f"[YAMA] Executing automation command: {query}")
        
        system = platform.system()
        
        try:
            if "open" in query or "khol" in query:
                app_map = {
                    "notepad": "notepad.exe" if system == "Windows" else "gedit",
                    "calculator": "calc.exe" if system == "Windows" else "gnome-calculator",
                    "browser": "start chrome" if system == "Windows" else "google-chrome"
                }
                
                target_app = None
                for key in app_map:
                    if key in query:
                        target_app = app_map[key]
                        break
                
                if target_app:
                    if system == "Windows":
                        subprocess.Popen(target_app, shell=True)
                    else:
                        subprocess.Popen(target_app.split())
                    return AgentResult(self.name, True, f"Opening {target_app}...", 0.8)
                else:
                    return AgentResult(self.name, False, "I'm sorry, I couldn't recognize this application.", 0.0)

            elif "list" in query or "files" in query:
                path = "."
                files = os.listdir(path)
                return AgentResult(self.name, True, f"Files in {os.path.abspath(path)}: {', '.join(files[:10])}", 0.8)

            elif "create folder" in query or "nayan folder" in query:
                folder_name = "new_folder"
                os.makedirs(folder_name, exist_ok=True)
                return AgentResult(self.name, True, f"Folder '{folder_name}' created successfully.", 0.8)

            return AgentResult(self.name, False, "Automation command not recognized.", 0.0)
            
        except Exception as e:
            print(f"[ERROR] YAMA: {str(e)}")
            return AgentResult(self.name, False, str(e), 0.0)

    def background_scan(self) -> Finding:
        # Silently check system health
        try:
            # Check Disk
            usage = shutil.disk_usage('/')
            percent_full = (usage.used / usage.total) * 100
            if percent_full > 85:
                return Finding(
                    agent_name=self.name,
                    priority=Priority.HIGH,
                    title="YAMA: Disk space is low",
                    detail=f"C: drive is {percent_full:.1f}% full. Should I clean up temporary files?",
                    action_type=ActionType.NEEDS_PERMISSION,
                    action_fn=self.cleanup_temp_files
                )
            
            # Check CPU
            cpu_usage = psutil.cpu_percent(interval=1)
            if cpu_usage > 90:
                return Finding(
                    agent_name=self.name,
                    priority=Priority.HIGH,
                    title="YAMA: CPU usage is high",
                    detail=f"System is under heavy load ({cpu_usage}%). Should I list heavy processes?",
                    action_type=ActionType.NEEDS_PERMISSION,
                    action_fn=lambda: print("[YAMA] Showing high CPU processes...")
                )
        except Exception as e:
            print(f"[BG-ERROR] YAMA: {e}")
        return None

    def cleanup_temp_files(self):
        print("[YAMA] Cleaning up temporary files...")
        # Implementation for cleanup
        pass
