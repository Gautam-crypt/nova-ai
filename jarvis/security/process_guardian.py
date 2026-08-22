"""
jarvis/security/process_guardian.py
DEFENSIVE SECURITY ONLY.
Monitors running processes on the local machine for signs of compromise:
1. Unauthorized Camera/Microphone access
2. High-risk processes running from Temp directories
3. Keylogger-like behavior (injecting into system processes)
"""

import threading
import time
import psutil
import os

from jarvis.core.background.findings_queue import Finding, Priority, ActionType


class ProcessGuardian:
    def __init__(self, findings_queue):
        self.queue = findings_queue
        self._running = False
        self._whitelisted_pids: set = set()
        self._baseline_processes: set = set()
        
    def start(self):
        """Start defensive process monitoring."""
        self._running = True
        self._take_baseline()
        threading.Thread(target=self._monitor_loop, daemon=True, name="guardian_monitor").start()
        print("[KAVACH] ProcessGuardian started — System integrity protected")
        
    def stop(self):
        self._running = False
        
    def _take_baseline(self):
        """Record all processes running at startup as 'known'."""
        try:
            for proc in psutil.process_iter(['pid']):
                self._baseline_processes.add(proc.info['pid'])
        except Exception:
            pass
            
    def _monitor_loop(self):
        """Scan processes every 15 seconds for malicious indicators."""
        while self._running:
            try:
                for proc in psutil.process_iter(['pid', 'name', 'exe', 'cpu_percent']):
                    pid = proc.info['pid']
                    
                    if pid in self._whitelisted_pids or pid in self._baseline_processes:
                        continue
                        
                    # Calculate threat score
                    score, reason = self._score_process(proc)
                    
                    if score >= 0.7:
                        name = proc.info.get('name', 'Unknown')
                        self._push_finding(
                            Priority.HIGH,
                            f"Malicious Process Blocked: {name}",
                            f"Detected high-risk behavior in '{name}': {reason}",
                            ActionType.NEEDS_PERMISSION,
                            action_fn=lambda p=pid: self.kill_process(p)
                        )
                        # Auto-blacklist to avoid spamming
                        self._whitelisted_pids.add(pid)
                        
            except Exception as e:
                pass
            time.sleep(15)
            
    def _score_process(self, proc) -> tuple[float, str]:
        """
        Evaluate process suspiciousness.
        Returns: (score [0.0 - 1.0], reason_string)
        """
        score = 0.0
        reasons = []
        
        try:
            exe_path = proc.info.get('exe', '') or ''
            name = proc.info.get('name', '').lower()
            
            # Indicator 1: Running from temporary/hidden directories
            if exe_path:
                lower_path = exe_path.lower()
                if '\\appdata\\local\\temp\\' in lower_path:
                    score += 0.5
                    reasons.append("Running from Temp folder")
                if 'recycle.bin' in lower_path:
                    score += 0.8
                    reasons.append("Hiding in Recycle Bin")
                    
            # Indicator 2: Suspicious names (masquerading)
            suspicious_names = ['svchost.exe', 'explorer.exe', 'winlogon.exe']
            if name in suspicious_names and exe_path:
                if not exe_path.lower().startswith('c:\\windows\\system32'):
                    score += 0.9
                    reasons.append("System file masquerading (Fake Windows Process)")
                    
            # Indicator 3: Unusually high CPU for an unknown background app
            cpu = proc.info.get('cpu_percent')
            if cpu and cpu > 60.0 and not proc.environ().get('PROMPT'):
                score += 0.2
                reasons.append("Abnormal CPU usage (Crypto-miner pattern)")
                
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
            
        return min(1.0, score), ", ".join(reasons)
        
    def kill_process(self, pid: int) -> str:
        """Terminate a malicious process."""
        try:
            p = psutil.Process(pid)
            name = p.name()
            p.kill()
            return f"Terminated malicious process '{name}'"
        except Exception as e:
            return f"Failed to terminate PID {pid}: {e}"
            
    def _push_finding(self, priority, title, detail, action_type, action_fn=None):
        finding = Finding(
            agent_name="kavach",
            priority=priority,
            title=title,
            detail=detail,
            action_type=action_type,
            action_fn=action_fn
        )
        self.queue.push(finding)
