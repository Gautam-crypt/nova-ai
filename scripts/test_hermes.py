import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from jarvis.agents.hermes import HermesAgent

def run_test():
    agent = HermesAgent()
    print("Testing Hermes Web Search...")
    task = {"query": "who is chief minister of uttar pradesh"}
    result = agent.execute(task)
    print(f"Success: {result.success}")
    print(f"Data:\n{result.data}")

if __name__ == "__main__":
    run_test()
