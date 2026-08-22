"""
jarvis/security/counter_intel.py
DEFENSIVE SECURITY ONLY.
Active Counter-Intelligence for self-defense.
1. Deploys Honeypots (fake files that trigger alerts if accessed)
2. Scans for known spyware/adware registry keys
3. Digital footprint wiping (anti-forensics for privacy)
"""

import os
import time
import json
import threading
import shutil
import urllib.request
from pathlib import Path

from jarvis.core.background.findings_queue import Finding, Priority, ActionType


class CounterIntelligence:
    def __init__(self, findings_queue):
        self.queue = findings_queue
        self.honeypot_files = {}
        
    def deploy_honeypots(self):
        """
        Creates fake 'attractive' files. If any process reads these files,
        it indicates the system is compromised by data-stealing malware.
        """
        user_dir = os.path.expanduser("~")
        
        targets = [
            (os.path.join(user_dir, "Desktop", "passwords_backup.txt"), "BANK_LOGIN: admin:password123"),
            (os.path.join(user_dir, "Documents", "crypto_wallet_keys.txt"), "WALLET_SEED: apple banana orange..."),
            (os.path.join(user_dir, "Downloads", "confidential_financials.csv"), "Account,Balance\n1234,50000")
        ]
        
        for path, content in targets:
            try:
                with open(path, 'w') as f:
                    f.write(content)
                # Store the last access time
                self.honeypot_files[path] = os.path.getatime(path)
            except Exception:
                pass
                
        # Start monitoring thread
        threading.Thread(target=self._monitor_honeypots, daemon=True, name="honeypot_monitor").start()
        print("[KAVACH] Counter-Intel: Honeypots deployed.")
        
    def _monitor_honeypots(self):
        """Check if any honeypot file was accessed."""
        while True:
            for path, initial_atime in list(self.honeypot_files.items()):
                try:
                    if not os.path.exists(path):
                        continue
                    current_atime = os.path.getatime(path)
                    
                    # If access time changed by more than 2 seconds
                    if current_atime - initial_atime > 2.0:
                        self._push_finding(
                            Priority.HIGH,
                            "HONEYPOT TRIGGERED - System Compromised",
                            f"An unknown process accessed the decoy file: {path}. Malware is actively searching your files.",
                            ActionType.NEEDS_PERMISSION,
                            action_fn=self.wipe_digital_footprint
                        )
                        # Update time to prevent spam
                        self.honeypot_files[path] = current_atime
                except Exception:
                    pass
            time.sleep(5)
            
    def scan_for_spyware(self) -> str:
        """Scan system startup locations for unauthorized trackers."""
        # Simple registry scan simulation (requires winreg in production)
        suspicious = []
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
            for i in range(1024):
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    # Check if running from appdata temp or similar
                    if 'temp' in value.lower() or 'appdata\\roaming' in value.lower():
                        suspicious.append(f"{name}: {value}")
                except WindowsError:
                    break
        except Exception:
            pass
            
        if suspicious:
            return "WARNING: Suspicious startup programs detected:\n" + "\n".join(suspicious)
        return "System clean. No suspicious startup trackers found."
        
    def wipe_digital_footprint(self) -> str:
        """Clear temporary files, browser caches (simulated), and clipboard."""
        cleared = 0
        try:
            # Clear clipboard
            import win32clipboard
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.CloseClipboard()
            cleared += 1
            
            # Clear Windows Temp
            temp_dir = os.environ.get('TEMP')
            if temp_dir and os.path.exists(temp_dir):
                for item in os.listdir(temp_dir):
                    item_path = os.path.join(temp_dir, item)
                    try:
                        if os.path.isfile(item_path):
                            os.remove(item_path)
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path, ignore_errors=True)
                    except Exception:
                        pass
                cleared += 1
                
            return f"Digital footprint wiped. Clipboard and Temp directories cleared."
        except Exception as e:
            return f"Error wiping footprint: {e}"
            
    def reverse_ip_lookup(self, ip: str) -> str:
        """Get geographical info about an attacking IP."""
        try:
            with urllib.request.urlopen(f"http://ip-api.com/json/{ip}", timeout=5) as response:
                data = json.loads(response.read().decode())
                if data.get("status") == "success":
                    return f"IP: {ip}\nLocation: {data.get('city')}, {data.get('country')}\nISP: {data.get('isp')}"
        except Exception:
            pass
        return f"Could not trace IP: {ip}"
        
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
