"""
jarvis/core/brain/llm.py
Grounded Logic & Emotional Intelligence for NOVA.
"""

import ollama
import json
import re
import os
from jarvis.core.brain.prompts import build_system_prompt, TOOL_DESCRIPTIONS
from jarvis.core.brain.memory import LongTermMemory
from jarvis.core.brain.database import db
import httpx
from dotenv import load_dotenv

load_dotenv()
SARVAM_CHAT_KEY = os.getenv("SARVAM_TTS_KEY") # Usually keys work across services

class Brain:
    def __init__(self, model_name="gemma3:4b"):
        # Verify model exists, else fallback
        try:
            raw_models = ollama.list().get('models', []) if isinstance(ollama.list(), dict) else ollama.list().models
            model_names = []
            for m in raw_models:
                if hasattr(m, 'model'): model_names.append(m.model)
                elif isinstance(m, dict): model_names.append(m.get('model') or m.get('name'))

            if model_name not in model_names and f"{model_name}:latest" not in model_names:
                print(f"[WARNING] Model '{model_name}' not found locally. Falling back to 'qwen2.5:7b'.")
                self.model_name = "qwen2.5:7b"
            else:
                self.model_name = model_name
        except:
            self.model_name = "qwen2.5:7b"
            
        self.memory = LongTermMemory()
        self.history = []

    def think(self, user_input: str, emotion: str = "neutral", stress: float = 0.0, pattern: dict = None) -> str:
        """Processes input with emotional context, tools, and dual-DB memory."""
        if pattern is None:
            pattern = {}
            
        # 1. Fetch Hard Identity from SQL DB
        user_name = db.get_profile_value('user_name')
        religion = db.get_profile_value('religion')
        style = db.get_profile_value('language_style')
        
        # 2. Retrieve relevant semantic memories from ChromaDB
        past_context = self.memory.retrieve_relevant(user_input, n_results=5)
        
        # 3. Build system prompt with Hard Rules + Memory
        system = build_system_prompt(emotion, stress, pattern) + "\n" + TOOL_DESCRIPTIONS
        
        # Identity Context (Force)
        identity_str = f"IDENTITY: User is {user_name} ({religion}). Style: {style}. NO SALAAM."
        
        if pattern.get("is_followup"):
            identity_str += "\nNOTE: This is a follow-up after an action. Summarize what you saw/did naturally."
        
        try:
            # FEW-SHOT HISTORY (To force the model to behave)
            messages = [
                {'role': 'system', 'content': f"{system}\n\n{identity_str}"},
                # Mock example 1
                {'role': 'user', 'content': "Hii NOVA"},
                {'role': 'assistant', 'content': "Arre Ram Ram Gautam bhai! Bol kya scene hai aaj ka? Ekdum mast lag raha hai sab."},
                # Mock example 2 (Action)
                {'role': 'user', 'content': "Gaana chalao"},
                {'role': 'assistant', 'content': "Arre bilkul bawa! Abhi ekdum gajab bollywood gaane chala rahi hoon.\nACTION: play_music | param: Bollywood songs"},
                # Real user input
                {'role': 'user', 'content': user_input},
            ]
            
            # Try Sarvam AI first for best Hindi/Hinglish quality
            if SARVAM_CHAT_KEY:
                try:
                    url = "https://api.sarvam.ai/v1/chat/completions"
                    headers = {
                        "api-subscription-key": SARVAM_CHAT_KEY,
                        "Content-Type": "application/json"
                    }
                    payload = {
                        "model": "sarvam-m",
                        "messages": messages,
                        "temperature": 0.7
                    }
                    
                    with httpx.Client() as client:
                        response = client.post(url, json=payload, headers=headers, timeout=15.0)
                        if response.status_code == 200:
                            res_text = response.json()['choices'][0]['message']['content'].strip()
                            print("[NOVA] Using Sarvam AI (Cloud)")
                        else:
                            # Fallback if Sarvam API fails
                            print(f"[SARVAM API ERROR]: {response.status_code}. Falling back to local.")
                            response = ollama.chat(
                                model=self.model_name, 
                                messages=messages,
                                options={
                                    "temperature": 0.6,
                                    "top_p": 0.9,
                                    "repeat_penalty": 1.15,
                                    "top_k": 50
                                }
                            )
                            res_text = response['message']['content'].strip()
                except Exception as e:
                    print(f"[BRAIN ERROR]: {e}. Falling back to local.")
                    response = ollama.chat(model=self.model_name, messages=messages)
                    res_text = response['message']['content'].strip()
            else:
                # Use local Ollama
                response = ollama.chat(
                    model=self.model_name, 
                    messages=messages,
                    options={
                        "temperature": 0.6,
                        "top_p": 0.9,
                        "repeat_penalty": 1.15,
                        "top_k": 50
                    }
                )
                res_text = response['message']['content'].strip()
            
            # --- HARD OUTPUT FILTER (Anti-Hallucination) ---
            
            # 2. PROMPT LEAKAGE FILTER (Remove instructions that the model repeats)
            leakage_patterns = [
                r"If the user wants an action.*",
                r"ACTION:.*\|.*param:.*",
                r"Examples:.*",
                r"STRICT PERSONA RULE:.*",
                r"Actions taken:.*",
                r"Emotional context:.*",
                r"Bhagwaan ke liye.*", # Specific repetitive phrase
                r"Aapko pata nahi ke mujhe apni sachhi tarah.*" # Specific repetitive phrase
            ]
            for pat in leakage_patterns:
                res_text = re.sub(pat, "", res_text, flags=re.IGNORECASE | re.DOTALL)

            # 3. Strip Meta-commentary and Translations
            res_text = re.sub(r"\(Translation:.*?\)", "", res_text, flags=re.DOTALL | re.IGNORECASE)
            res_text = re.sub(r"Translation:.*", "", res_text, flags=re.IGNORECASE)
            res_text = re.sub(r"\[.*?\]", "", res_text) # Remove [brackets]
            # 4. Remove reasoning tags <think>...</think>
            res_text = re.sub(r'<think>.*?</think>', '', res_text, flags=re.DOTALL).strip()
            
            res_text = res_text.strip()
            
            # 3. Save to ChromaDB
            self.memory.store_interaction(user_input, res_text)
            
            return res_text
        except Exception as e:
            print(f"[BRAIN ERROR]: {e}")
            return "Maaf kijiye Sir, kuch dikkat ho gayi."

    def generate_response(self, user_input: str) -> tuple[str, str]:
        # Legacy method for backward compatibility if needed
        res = self.think(user_input)
        return res, "neutral"

    def get_proactive_prompt(self, emotion: str = "neutral", stress: float = 0.0) -> str:
        prompt = "Owner has been silent. Check in naturally in 1 short Hinglish line based on current mood."
        return self.think(prompt, emotion=emotion, stress=stress)
