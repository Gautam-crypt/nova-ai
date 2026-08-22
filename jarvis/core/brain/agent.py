"""
jarvis/core/brain/agent.py
Orchestration layer for executing tools and managing the thought-action loop.
"""

import re
from jarvis.core.brain.llm import Brain
from jarvis.core.senses.vision.analyzer import VisionAnalyzer
from jarvis.api.bridge import send_event

class NovaAgent:
    def __init__(self):
        self.brain = Brain()
        self.vision = VisionAnalyzer()
        
    def execute_action(self, action_str: str) -> str:
        """Parses and executes an ACTION: tool | param: value string."""
        try:
            pattern = r"ACTION:\s*(\w+)\s*\|\s*param:\s*(.*)"
            match = re.search(pattern, action_str)
            
            if not match:
                return ""
            
            tool_name = match.group(1).strip()
            param = match.group(2).strip()
            
            print(f"[AGENT] Executing: {tool_name} with param: {param}")
            
            if tool_name == "describe_scene":
                # Call the vision analyzer
                return self.vision.describe_current_frame(param or "Describe what you see.")
            
            elif tool_name == "play_music":
                send_event("music_control", {"action": "play", "query": param})
                return f"Playing {param}."
                
            elif tool_name == "open_app":
                import os
                # Simple implementation for Windows
                os.system(f"start {param}")
                return f"Opening {param}."
            
            # Add more tools as needed...
            return f"Action {tool_name} executed."
            
        except Exception as e:
            return f"Error executing tool: {e}"

    def run(self, user_input: str) -> str:
        """The main loop: Think -> Act -> Observe -> Finish."""
        # 1. Think
        response = self.brain.think(user_input)
        
        # 2. Check for Actions
        if "ACTION:" in response:
            # Execute action
            observation = self.execute_action(response)
            
            # 3. Inform the brain of the observation
            # We call the brain again with the observation to get a final natural response
            final_response = self.brain.think(
                f"SYSTEM OBSERVATION: {observation}\nNow give a natural response to the user based on this.",
                pattern={"is_followup": True}
            )
            return final_response
            
        return response

# Global instance
agent = NovaAgent()
