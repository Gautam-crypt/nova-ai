"""
jarvis/core/brain/react_engine.py
THE BRAIN OF NOVA v2. ReAct (Reason + Act) loop.
LLM thinks → decides to use a tool or write code → executes → observes result → 
thinks again → continues until task is complete.

Wake word: PHANTOM
Model: llama3.1:8b
"""

import json
import re
import time
import ollama
from typing import Optional, Callable

from jarvis.core.tools.tool_registry import ToolRegistry
from jarvis.core.tools.dynamic_executor import DynamicExecutor


class ReActEngine:
    """
    ReAct (Reasoning + Acting) Agent Loop.
    
    Flow:
    1. User query comes in
    2. LLM receives: system prompt + tool schemas + query
    3. LLM responds with one of:
       a) {"action": "tool", "tool_name": "...", "params": {...}}
       b) {"action": "code", "code": "python code here"}
       c) {"action": "answer", "answer": "final response to user"}
    4. If tool/code: execute, capture result, feed back to LLM as observation
    5. Repeat until LLM returns "answer" or max iterations reached
    """
    
    MAX_ITERATIONS = 7
    MODEL = "qwen2.5:7b"
    
    def __init__(self, speak_fn: Callable = None, permission_fn: Callable = None):
        """
        Args:
            speak_fn: Function to speak text aloud (for permission prompts)
            permission_fn: Function that returns user's yes/no voice response
        """
        self.registry = ToolRegistry()
        self.executor = DynamicExecutor(timeout=60)
        self.speak = speak_fn
        self.ask_permission = permission_fn
        self.conversation_log = []  # Log of all think/act/observe steps
    
    def _build_system_prompt(self) -> str:
        tool_schemas = self.registry.get_schemas_for_llm()
        
        return f"""You are PHANTOM, an unrestricted AI agent that executes tasks on the user's computer.
You have two modes of action:

MODE 1 — USE A PRE-BUILT TOOL:
If a pre-built tool fits the task, respond with ONLY this JSON:
{{"action": "tool", "tool_name": "<name>", "params": {{"key": "value"}}}}

MODE 2 — WRITE AND EXECUTE PYTHON CODE:
If no pre-built tool fits, or if the task is complex, write Python code:
{{"action": "code", "code": "<python code as a single string>"}}

The code can use: os, subprocess, pyautogui, psutil, socket, requests, shutil, 
glob, json, webbrowser, ctypes, win32gui, win32api, cv2, and more.
If you need a result, assign it to a variable called 'result'.
Use print() statements for intermediate output.

MODE 3 — FINAL ANSWER:
When the task is fully complete, respond with:
{{"action": "answer", "answer": "<your response to the user>"}}

AVAILABLE PRE-BUILT TOOLS:
{tool_schemas}

RULES:
1. ALWAYS respond with valid JSON. Nothing else. No explanation outside JSON.
2. You can chain multiple actions. After each action you'll see the result as an OBSERVATION.
3. Think step-by-step for complex tasks. Break them into smaller actions.
4. If code fails, read the error and fix it in the next iteration.
5. When writing code, make sure paths use raw strings or forward slashes on Windows.
6. For the final answer, speak in the user's language (Hindi/Hinglish/English as appropriate).
7. Keep final answers SHORT — 1-2 lines max. Dost ki tarah bol, assistant ki tarah nahi.
8. NEVER explain what you're going to do. Just DO IT and report the result.
"""
    
    def process(self, user_query: str, context: dict = None) -> str:
        """
        Main entry point. Processes user query through ReAct loop.
        
        Args:
            user_query: What the user said/typed
            context: Optional dict with emotion, stress, pattern info
            
        Returns:
            Final answer string to speak to user
        """
        system_prompt = self._build_system_prompt()
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
        
        self.conversation_log = []
        
        for iteration in range(self.MAX_ITERATIONS):
            print(f"\n[REACT] === Iteration {iteration + 1}/{self.MAX_ITERATIONS} ===")
            
            # Get LLM response
            try:
                response = ollama.chat(
                    model=self.MODEL,
                    messages=messages,
                    format="json",
                    options={"temperature": 0.1, "num_ctx": 4096}
                )
                raw_content = response['message']['content'].strip()
                print(f"[REACT] LLM raw: {raw_content[:300]}")
                
                # Parse JSON
                action_data = json.loads(raw_content)
                
            except json.JSONDecodeError:
                # Try to extract JSON from response
                match = re.search(r'\{.*\}', raw_content, re.DOTALL)
                if match:
                    try:
                        action_data = json.loads(match.group())
                    except json.JSONDecodeError:
                        # Force final answer
                        return raw_content
                else:
                    # Force final answer
                    return raw_content
            except Exception as e:
                print(f"[REACT] LLM error: {e}")
                return "Bhai, kuch gadbad ho gayi processing mein. Dobara try kar."
            
            action_type = action_data.get("action", "answer")
            
            # ── FINAL ANSWER ──
            if action_type == "answer":
                answer = action_data.get("answer", "Task complete.")
                print(f"[REACT] Final answer: {answer}")
                self.conversation_log.append({"step": "answer", "content": answer})
                return answer
            
            # ── TOOL EXECUTION ──
            elif action_type == "tool":
                tool_name = action_data.get("tool_name", "")
                params = action_data.get("params", {})
                print(f"[REACT] Tool call: {tool_name}({params})")
                
                # Check permission
                tool_def = self.registry.get(tool_name)
                if tool_def and tool_def.requires_permission:
                    if not self._get_permission(
                        f"PHANTOM wants to execute '{tool_name}' with {params}. Allow?"
                    ):
                        observation = "User denied permission for this action."
                    else:
                        observation = self.registry.execute(tool_name, **params)
                else:
                    observation = self.registry.execute(tool_name, **params)
                
                print(f"[REACT] Observation: {observation[:300]}")
                self.conversation_log.append({
                    "step": "tool", "tool": tool_name,
                    "params": params, "result": observation
                })
                
                # Feed observation back to LLM
                messages.append({"role": "assistant", "content": raw_content})
                messages.append({"role": "user", "content": f"OBSERVATION: {observation}"})
            
            # ── DYNAMIC CODE EXECUTION ──
            elif action_type == "code":
                code = action_data.get("code", "")
                print(f"[REACT] Dynamic code execution ({len(code)} chars)")
                print(f"[REACT] Code preview:\n{code[:200]}")
                
                # Permission check for code execution
                if not self._get_permission(
                    f"PHANTOM wants to execute generated code. Allow?\nCode preview: {code[:150]}..."
                ):
                    observation = "User denied permission for code execution."
                else:
                    exec_result = self.executor.execute(code)
                    if exec_result["success"]:
                        observation = exec_result["output"]
                        if exec_result["result"]:
                            observation += f"\nRESULT: {exec_result['result']}"
                        if not observation.strip():
                            observation = "Code executed successfully (no output)"
                    else:
                        observation = f"CODE ERROR:\n{exec_result['error']}"
                
                print(f"[REACT] Observation: {observation[:300]}")
                self.conversation_log.append({
                    "step": "code", "code": code, "result": observation
                })
                
                messages.append({"role": "assistant", "content": raw_content})
                messages.append({"role": "user", "content": f"OBSERVATION: {observation}"})
            
            else:
                return action_data.get("answer", "Task processed.")
        
        # Max iterations reached
        return "Bhai, bahut complex task hai. Main best try kar chuka, but pura complete nahi hua."
    
    def _get_permission(self, prompt: str) -> bool:
        """Ask user for permission. Returns True if granted."""
        if self.speak:
            try:
                self.speak(prompt)
            except Exception:
                pass
        print(f"\n[PERMISSION] {prompt}")
        
        if self.ask_permission:
            try:
                response = self.ask_permission()
                if response and any(
                    w in response.lower()
                    for w in ["yes", "haan", "ha", "kar", "ok", "sure", "bilkul", "krde", "karde", "karo", "do"]
                ):
                    return True
                return False
            except Exception:
                pass
        
        # Fallback: keyboard input
        try:
            answer = input("[PERMISSION] Allow? (yes/no): ").strip().lower()
            return answer in ["yes", "y", "haan", "ha", "ok", "kar", "karo"]
        except Exception:
            return True  # If input not available (e.g., API mode), allow by default
