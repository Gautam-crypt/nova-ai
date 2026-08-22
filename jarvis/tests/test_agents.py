import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import threading
from concurrent.futures import ThreadPoolExecutor

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from jarvis.core.orchestrator import NOVAOrchestrator
from jarvis.agents.memory_agent import MemoryAgent
from jarvis.agents.hermes import HermesAgent
from jarvis.agents.vishwakarma import VishwakarmaAgent
from jarvis.agents.divya import DivyaAgent
from jarvis.agents.yama import YamaAgent
from jarvis.agents.manas import ManasAgent

class TestAgents(unittest.TestCase):

    def setUp(self):
        self.orchestrator = NOVAOrchestrator(model="qwen2.5:7b")
        self.memory_agent = MemoryAgent()
        self.hermes_agent = HermesAgent()
        self.vishwakarma_agent = VishwakarmaAgent()
        self.divya_agent = DivyaAgent()
        self.yama_agent = YamaAgent()
        self.manas_agent = ManasAgent()

    # --- Unit Tests: can_handle ---

    def test_memory_agent_can_handle(self):
        self.assertTrue(self.memory_agent.can_handle({"query": "anything"}))

    def test_hermes_agent_can_handle(self):
        self.assertTrue(self.hermes_agent.can_handle({"query": "latest weather news"}))
        self.assertTrue(self.hermes_agent.can_handle({"query": "search for AI"}))
        self.assertFalse(self.hermes_agent.can_handle({"query": "play music"}))

    def test_vishwakarma_agent_can_handle(self):
        self.assertTrue(self.vishwakarma_agent.can_handle({"query": "fix this python bug"}))
        self.assertFalse(self.vishwakarma_agent.can_handle({"query": "how are you"}))

    def test_divya_agent_can_handle(self):
        self.assertTrue(self.divya_agent.can_handle({"query": "what can you see?"}))
        self.assertFalse(self.divya_agent.can_handle({"query": "write a story"}))

    def test_yama_agent_can_handle(self):
        self.assertTrue(self.yama_agent.can_handle({"query": "open notepad"}))
        self.assertFalse(self.yama_agent.can_handle({"query": "translate this"}))

    def test_manas_agent_can_handle(self):
        self.assertTrue(self.manas_agent.can_handle({"query": "I am feeling sad"}))
        self.assertFalse(self.manas_agent.can_handle({"query": "calculate 2+2"}))

    # --- Mocks: execute ---

    @patch("httpx.Client.get")
    def test_hermes_agent_execute_mock(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"AbstractText": "Cloudy with a chance of meatballs"}
        mock_get.return_value = mock_response
        
        result = self.hermes_agent.execute({"query": "weather"})
        self.assertTrue(result.success)
        self.assertIn("Cloudy", result.data)

    @patch("cv2.VideoCapture")
    @patch("ollama.generate")
    def test_divya_agent_execute_mock(self, mock_ollama, mock_cv2):
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, MagicMock())
        mock_cv2.return_value = mock_cap
        
        mock_ollama.return_value = {"response": "A person sitting at a desk."}
        
        result = self.divya_agent.execute({"query": "look"})
        self.assertTrue(result.success)
        self.assertEqual(result.data, "A person sitting at a desk.")

    # --- Integration & Thread Safety ---

    @patch("ollama.generate")
    def test_orchestrator_routing_integration(self, mock_ollama):
        # Mocking routing response to return hermes
        mock_ollama.side_effect = [
            {"response": '["hermes"]'}, # Routing call
            {"response": "Bhai, Delhi mein mast weather hai."} # Aggregation call
        ]
        
        self.orchestrator.register_agent(self.hermes_agent)
        
        with patch.object(HermesAgent, 'execute') as mock_exec:
            mock_exec.return_value = MagicMock(success=True, data="Mocked Search Result", agent_name="hermes")
            
            response = self.orchestrator.process("aaj ka weather kaisa hai Delhi mein?")
            self.assertIsInstance(response, str)
            self.assertTrue(len(response) > 0)
            mock_exec.assert_called_once()

    @patch("jarvis.core.orchestrator.NOVAOrchestrator.route_task")
    @patch("jarvis.core.orchestrator.NOVAOrchestrator.aggregate_results")
    def test_thread_safety(self, mock_agg, mock_route):
        mock_route.return_value = ["memory_agent"]
        mock_agg.return_value = "Thread safe response"
        
        self.orchestrator.register_agent(self.memory_agent)
        
        def run_proc():
            return self.orchestrator.process("test query")

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(run_proc) for _ in range(5)]
            results = [f.result() for f in futures]
            
        for res in results:
            self.assertEqual(res, "Thread safe response")
        self.assertEqual(len(results), 5)

if __name__ == "__main__":
    unittest.main()
