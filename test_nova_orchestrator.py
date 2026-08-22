import sys
import pathlib

# Make jarvis/ importable from project root
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from jarvis.core.orchestrator import NOVAOrchestrator
from jarvis.agents.memory_agent import MemoryAgent
from jarvis.agents.search_agent import SearchAgent
from jarvis.agents.code_agent import CodeAgent
from jarvis.agents.vision_agent import VisionAgent
from jarvis.agents.automation_agent import AutomationAgent
from jarvis.agents.emotion_agent import EmotionAgent

def test_system():
    # Initialize Orchestrator
    # Note: Ensure Ollama is running with qwen2.5:7b
    nova = NOVAOrchestrator(model="qwen2.5:7b")

    # Register Agents
    nova.register_agent(MemoryAgent())
    nova.register_agent(SearchAgent())
    nova.register_agent(CodeAgent())
    nova.register_agent(VisionAgent())
    nova.register_agent(AutomationAgent())
    nova.register_agent(EmotionAgent())

    # Test Query 1: Search + Emotion
    query1 = "Bhai, search for latest AI news and tell me if you are happy today."
    print("\n" + "="*50)
    print(f"TEST 1: {query1}")
    response1 = nova.process(query1)
    print(f"RESPONSE 1: {response1}")

    # Test Query 2: Code + Memory
    query2 = "Remember the code I asked you to fix earlier? Can you show me?"
    print("\n" + "="*50)
    print(f"TEST 2: {query2}")
    response2 = nova.process(query2)
    print(f"RESPONSE 2: {response2}")

if __name__ == "__main__":
    test_system()
