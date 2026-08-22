"""
jarvis/agents/kavach.py
The KAVACH Security Agent.
Routes security queries to the appropriate defensive sub-module.
"""

from jarvis.core.agent_base import BaseAgent, AgentResult
from jarvis.security.network_sentinel import NetworkSentinel
from jarvis.security.process_guardian import ProcessGuardian
from jarvis.security.counter_intel import CounterIntelligence
from jarvis.core.background.findings_queue import Finding, Priority, ActionType


class KavachAgent(BaseAgent):
    def __init__(self, findings_queue):
        super().__init__("kavach")
        self.keywords = [
            "security", "hack", "network", "scan", "block", "firewall",
            "spy", "track", "monitor", "packet", "safe", "threat", 
            "suraksha", "device", "honeypot", "wipe", "clean", "trace", "ip"
        ]
        
        self.sentinel = NetworkSentinel(findings_queue)
        self.guardian = ProcessGuardian(findings_queue)
        self.counter_intel = CounterIntelligence(findings_queue)
        
    def start_all(self):
        """Arm all security modules."""
        self.sentinel.start()
        self.guardian.start()
        self.counter_intel.deploy_honeypots()
        
    def stop_all(self):
        self.sentinel.stop()
        self.guardian.stop()
        
    def can_handle(self, task: dict) -> bool:
        query = task.get("query", task.get("task", "")).lower()
        return any(k in query for k in self.keywords)
        
    def execute(self, task: dict) -> AgentResult:
        query = task.get("query", "").lower()
        
        # Route based on intent
        if any(w in query for w in ["scan network", "network scan", "kaun connected"]):
            result = self.sentinel.scan_network()
            
        elif any(w in query for w in ["block", "firewall"]):
            # Ask for IP clarification if none provided
            import re
            ip_match = re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', query)
            if ip_match:
                result = self.sentinel.block_ip(ip_match.group())
            else:
                result = "Please provide the exact IP address you want to block."
                
        elif any(w in query for w in ["honeypot", "trap"]):
            result = "Honeypots are actively deployed and monitoring for unauthorized access."
            
        elif any(w in query for w in ["wipe", "clean", "saaf", "footprint"]):
            result = self.counter_intel.wipe_digital_footprint()
            
        elif any(w in query for w in ["spyware", "spy", "tracking"]):
            result = self.counter_intel.scan_for_spyware()
            
        elif any(w in query for w in ["trace", "locate", "ip info"]):
            import re
            ip_match = re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', query)
            if ip_match:
                result = self.counter_intel.reverse_ip_lookup(ip_match.group())
            else:
                result = "Please provide an IP address to trace."
                
        else:
            # General security status
            result = "KAVACH is armed. Network Sentinel, Process Guardian, and Counter-Intel are monitoring the system."
            
        return AgentResult(self.name, True, result, 1.0)
