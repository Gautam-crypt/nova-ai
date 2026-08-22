from .findings_queue import Finding, ActionType, Priority

class PermissionHandler:
    """
    NOVA uses this to ask Gautam before executing agent actions.
    Works with both voice and text input.
    """
    
    def __init__(self, nova_speak_fn, nova_listen_fn):
        self.speak = nova_speak_fn
        self.listen = nova_listen_fn
    
    def request_permission(self, finding: Finding) -> bool:
        """
        Ask Gautam. Return True if approved, False if rejected.
        """
        question = f"{finding.title}. {finding.detail}. Should I proceed?"
        self.speak(question)
        print(f"[PERMISSION] Waiting for Gautam's response to: {finding.title}")
        
        # In a real system, we'd use the provided listen_fn which might be blocking
        response = self.listen() 
        
        if not response:
            self.speak("I didn't hear a response, so I'll skip it for now.")
            return False
        
        approved_words = ["haan", "ha", "yes", "kar", "karo", "theek", "ok", "bilkul", "proceed", "sure"]
        rejected_words = ["nahi", "no", "mat", "ruk", "baad mein", "not now", "cancel"]
        
        response_lower = response.lower()
        if any(w in response_lower for w in approved_words):
            self.speak("Alright, I'm on it.")
            return True
        elif any(w in response_lower for w in rejected_words):
            self.speak("Okay, I won't do it.")
            return False
        else:
            self.speak("I didn't quite catch that, so I'll skip it.")
            return False
    
    def handle_finding(self, finding: Finding):
        """Main method — call this for every HIGH/MEDIUM priority finding"""
        if finding.action_type == ActionType.INFO_ONLY:
            self.speak(f"Quick update: {finding.title}. {finding.detail}")
            return
        
        if finding.action_type == ActionType.NEEDS_PERMISSION:
            approved = self.request_permission(finding)
            if approved and finding.action_fn:
                try:
                    finding.action_fn()
                    print(f"[PERMISSION] {finding.agent_name} action executed.")
                except Exception as e:
                    self.speak(f"I ran into an error while trying to execute that: {e}")
