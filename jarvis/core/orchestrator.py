import json
import ollama
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import re
from .agent_base import BaseAgent, AgentResult
from jarvis.core.brain.react_engine import ReActEngine

class NOVAOrchestrator:
    def __init__(self, model: str = "gemma3:4b", ollama_client=None, chroma_client=None):
        self.ollama_client = ollama_client or ollama
        self.chroma_client = chroma_client
        self.react_engine = ReActEngine()
        
        # Verify model exists, else fallback
        try:
            # Handle both list of dicts and list of objects
            raw_models = self.ollama_client.list().get('models', []) if isinstance(self.ollama_client.list(), dict) else self.ollama_client.list().models
            model_names = []
            for m in raw_models:
                if hasattr(m, 'model'): model_names.append(m.model)
                elif isinstance(m, dict): model_names.append(m.get('model') or m.get('name'))

            if model not in model_names and f"{model}:latest" not in model_names:
                print(f"[WARNING] Model '{model}' not found locally. Falling back to 'qwen2.5:7b'.")
                self.model = "qwen2.5:7b"
            else:
                self.model = model
        except Exception as e:
            print(f"[DEBUG] Fallback failed: {e}")
            self.model = "qwen2.5:7b"

        self.agents: Dict[str, BaseAgent] = {}
        self.executor = ThreadPoolExecutor(max_workers=6)
        
        print("""
[NOVA] Pantheon online —
  HERMES      · search & web intelligence
  VISHWAKARMA · code & engineering
  DIVYA       · vision & perception
  YAMA        · automation & execution
  MANAS       · emotion & soul
        """)

    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator."""
        self.agents[agent.name] = agent
        print(f"[NOVA] Registered agent: {agent.name}")

    def route_task(self, task_query: str) -> List[str]:
        """Decide which agents should handle the task using Ollama + Keyword Fallback."""
        available_agents = []
        for name, agent in self.agents.items():
            desc = getattr(agent, 'description', name)
            available_agents.append(f"- {name}: {desc}")
            
        system_prompt = (
            "You are the Pantheon Router for NOVA AI. Your job is to select the correct agents for the user's request.\n"
            "AVAILABLE AGENTS:\n"
            "- hermes: Web search, news, weather, real-time info.\n"
            "- vishwakarma: Code analysis, terminal commands, engineering.\n"
            "- divya: Vision, camera, seeing, describing images, posture check.\n"
            "- yama: System automation, file management, hardware monitoring.\n"
            "- manas: Emotion analysis, psychological guidance, mood check.\n"
            "- memory_agent: Recalling past facts, conversations, and personal data.\n\n"
            "Return a JSON list of agent names (e.g., [\"divya\"]). Return ONLY the JSON."
        )
        
        print(f"[NOVA] Routing task: '{task_query}'")
        
        # 1. First, try Keyword matching for 100% reliability on common tasks
        manual_selection = []
        if any(w in task_query.lower() for w in ["see", "watch", "look", "camera", "dikh", "vision", "posture"]):
            manual_selection.append("divya")
        if any(w in task_query.lower() for w in ["search", "google", "news", "weather", "find", "latest"]):
            manual_selection.append("hermes")
        if any(w in task_query.lower() for w in ["code", "script", "error", "write", "program"]):
            manual_selection.append("vishwakarma")
            
        try:
            response = self.ollama_client.generate(
                model=self.model,
                prompt=f"Query: {task_query}",
                system=system_prompt,
                options={"temperature": 0.0}
            )
            
            content = response['response'].strip()
            # Basic JSON extraction
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                selected_agents = json.loads(match.group())
            else:
                selected_agents = []
                
            # Combine Manual + LLM
            final_agents = list(set(manual_selection + [name for name in selected_agents if name in self.agents]))
            
            if not final_agents:
                # Last resort: use agent.can_handle
                final_agents = [name for name, agent in self.agents.items() if agent.can_handle({"query": task_query})]
            
            print(f"[NOVA] Selected agents: {final_agents}")
            return final_agents
        except Exception as e:
            print(f"[ERROR] Routing failed: {str(e)}")
            return list(set(manual_selection + [name for name, agent in self.agents.items() if agent.can_handle({"query": task_query})]))

    def execute_parallel(self, agent_names: List[str], task: Dict[str, Any]) -> List[AgentResult]:
        """Execute selected agents in parallel."""
        futures = []
        for name in agent_names:
            agent = self.agents[name]
            futures.append(self.executor.submit(agent.run, task))
            
        results = []
        for future in as_completed(futures):
            results.append(future.result())
        return results

    def _detect_language(self, text: str) -> str:
        hindi_chars = set('अआइईउऊएऐओऔकखगघचछजझटठडढणतथदधनपफबभमयरलवशषसह')
        hinglish_words = [
            "kya","kaise","kaun","mujhe","hai","hain","bhai","yaar",
            "aur","nahi","toh","ki","ka","ke","tha","thi","hun",
            "rha","rhi","bol","kar","de","le","sun","dekh","arre",
            "oye","soch","lag","pta","jldi","thora","sogya","raat"
        ]
        text_lower = text.lower()
        if any(c in hindi_chars for c in text):
            return "hindi"
        if any(w in text_lower for w in hinglish_words):
            return "hinglish"
        return "english"

    def aggregate_results(self, task_query: str, agent_results: List[AgentResult]) -> str:
        """Merge results into a Hinglish response using Ollama."""
        results_str = "\n".join([
            f"Agent {res.agent_name} (Success: {res.success}): {res.data}"
            for res in agent_results
        ])
        
        lang_instruction = self._detect_language(task_query)
        
        system_prompt = "You are NOVA, a smart assistant. Follow the user's STRICT RULES exactly."
        
        prompt = f"""
Tu NOVA hai — Gautam ki personal AI dost. UP/Delhi style.

User ne bola: "{task_query}"
Agent se mila data: {results_str}

LANGUAGE DETECTION:
- User ne Hindi/Hinglish mein baat ki → Hinglish mein jawab de
- User ne English mein baat ki → Hinglish ya English dono chalega
- KABHI pure English mein mat bol jab user Hindi bol raha ho

HINGLISH STYLE:
- "tu/tujhe" use kar — "you/your" NAHI
- Dost ki tarah bol — therapist/assistant ki tarah NAHI
- Fillers: "yaar", "bhai", "arre", "bata", "dekh"
- Max 2 lines — short aur natural

CORRECT examples:
User: "neend nahi aayi"     → "Arre yaar 😅 aaj jaldi so ja — kal fresh feel karega!"
User: "kya scene hai"       → "Sab mast hai bhai, tu bata kya chal raha hai?"
User: "code kyu nahi chala" → "Send kar na — dekh ke bolti hoon kahan gadbad hai 👀"
User: "i cant sleep"        → "Arre so ja yaar 😴 phone rakh aur aankhein band kar"

WRONG examples (NEVER do this):
❌ "It's okay to feel that way! Maybe try relaxing techniques..."
❌ "I understand your concern. Here are some suggestions..."
❌ "That sounds difficult. Have you tried..."

Detected User Language: {lang_instruction}

Ab seedha reply de — koi preamble nahi:
"""
        
        try:
            response = self.ollama_client.generate(
                model=self.model,
                prompt=prompt,
                system=system_prompt,
                options={"temperature": 0.7}
            )
            raw_content = response['response'].strip()
            # Remove <think>...</think> tags and their content
            clean_content = re.sub(r'<think>.*?</think>', '', raw_content, flags=re.DOTALL).strip()
            return clean_content
        except Exception as e:
            print(f"[ERROR] Aggregation failed: {str(e)}")
            return "Sorry, I encountered an error while processing that. Could you try again?"

    def process(self, query: str) -> str:
        """Single entry point — now powered by ReAct engine."""
        print(f"\n[NOVA] --- New Request: {query} ---")
        
        # Step 1: Route to specialist agents for context gathering
        task = {"query": query}
        selected_agent_names = self.route_task(query)
        
        # Step 2: Gather agent context (parallel)
        agent_context = ""
        if selected_agent_names:
            results = self.execute_parallel(selected_agent_names, task)
            for res in results:
                if res.success:
                    agent_context += f"\n[{res.agent_name}]: {res.data}"
        
        # Step 3: Feed to ReAct engine with agent context
        enriched_query = query
        if agent_context:
            enriched_query = f"{query}\n\nCONTEXT FROM AGENTS:{agent_context}"
        
        final_response = self.react_engine.process(enriched_query)
        print(f"[NOVA] Final Response: {final_response}")
        return final_response
