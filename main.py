"""
main.py
"""

import sys
import pathlib
import time

# Make jarvis/ importable from project root
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from jarvis.auth.guardian import run_auth_gate
from jarvis.core.body.voice.speaker import speak
from jarvis.core.senses.voice.listener import listen, check_for_wake_word
from jarvis.core.brain.llm import Brain
from jarvis.emotions.detector import EmotionEngine
from jarvis.api.bridge import send_event
import threading
import sys

# Agent Imports
from jarvis.core.orchestrator import NOVAOrchestrator
from jarvis.agents.memory_agent import MemoryAgent
from jarvis.agents.hermes import HermesAgent
from jarvis.agents.vishwakarma import VishwakarmaAgent
from jarvis.agents.divya import DivyaAgent
from jarvis.agents.yama import YamaAgent
from jarvis.agents.manas import ManasAgent
from jarvis.agents.librarian import LibrarianAgent
from jarvis.core.background.findings_queue import FindingsQueue, Priority
from jarvis.core.background.background_loop import BackgroundAgentLoop
from jarvis.core.background.permission_handler import PermissionHandler

def main():
    # ── API GATE ─────────────────────────────────────────────
    pass

    # ── AUTH GATE — nothing runs before this ─────────────────
    if not run_auth_gate(speak_fn=speak):
        sys.exit(1)

    # ── BOOT NOVA ─────────────────────────────────────────────
    brain = Brain(model_name="gemma3:4b")
    import ollama
    import chromadb
    chroma_client = chromadb.PersistentClient(path="./data/chroma")
    
    orchestrator = NOVAOrchestrator(model="gemma3:4b", ollama_client=ollama, chroma_client=chroma_client)
    orchestrator.register_agent(MemoryAgent(chroma_client=chroma_client))
    orchestrator.register_agent(HermesAgent())
    orchestrator.register_agent(VishwakarmaAgent())
    orchestrator.register_agent(DivyaAgent())
    orchestrator.register_agent(YamaAgent())
    orchestrator.register_agent(ManasAgent())
    orchestrator.register_agent(LibrarianAgent(chroma_client=chroma_client))
    
    # ── BACKGROUND FINDINGS QUEUE ─────────────────────────────
    from jarvis.core.background.findings_queue import FindingsQueue, Priority
    findings_queue = FindingsQueue()
    
    # Register KAVACH Agent (Defensive Security)
    from jarvis.agents.kavach import KavachAgent
    kavach = KavachAgent(findings_queue)
    orchestrator.register_agent(kavach)
    
    # Start all defensive modules
    kavach.start_all()
    print("[KAVACH] All defensive security modules armed.")

    # Initialize Chronos (Predictive Intelligence)
    from jarvis.core.brain.chronos import Chronos
    chronos = Chronos()
    
    # Initialize Ghost Mode
    from jarvis.core.ghost_executor import GhostExecutor
    ghost = GhostExecutor(orchestrator.react_engine)
    
    # Import and register all pre-built tools for ReAct Engine
    import jarvis.core.tools.system_tools
    import jarvis.core.tools.os_controller

    # Set permission functions on ReAct engine
    orchestrator.react_engine.speak = speak
    
    # ── SELF-LEARNING SYSTEM ──────────────────────────────────
    from jarvis.core.learning.knowledge_db import KnowledgeDB
    from jarvis.core.learning.background_verifier import BackgroundVerifier
    from jarvis.core.learning.smart_responder import SmartResponder
    import os

    knowledge_db = KnowledgeDB(chroma_client=chroma_client)
    openai_key = os.getenv("OPENAI_API_KEY", "")
    verifier = BackgroundVerifier(knowledge_db=knowledge_db, openai_api_key=openai_key)
    smart_responder = SmartResponder(orchestrator=orchestrator, knowledge_db=knowledge_db, verifier=verifier)



    engine = EmotionEngine()

    # Initialize the listener for permission check
    from jarvis.core.senses.voice.listener import get_listener
    ls = get_listener()
    ls.set_microphone(None) 
    ls.calibrate()

    orchestrator.react_engine.ask_permission = ls.listen_for_command

    # ── CAMERA PERMISSION ────────────────────────────────────
    speak("Sir, security is clear. May I turn on the camera to see you?")
    permission_granted = False
    
    # Simple check for 'yes' or 'theek hai' or 'haan'
    response = ls.listen_for_command()
    if response and any(word in response.lower() for word in ["yes", "theek", "haan", "sure", "ok", "karlo"]):
        print("[NOVA] Camera permission granted.")
        engine.start()
        permission_granted = True
    else:
        print("[NOVA] Camera permission denied or not heard. Continuing in private mode.")

    print("[NOVA] Authenticating greeting...")
    # Get current emotion if camera is on, else default to happy
    current_emotion = "happy"
    if permission_granted:
        current_emotion, _ = engine.get()
        
    greeting = brain.think("The user has just passed security. Give a short, warm, and professional welcome back message in English.", emotion=current_emotion)
    speak(greeting, emotion=current_emotion)
    
    print("[NOVA] All systems online.")
    
    # ── BACKGROUND AGENT LOOP ────────────────────────────────
    agents_dict = {
        "hermes": orchestrator.agents.get("hermes"),
        "vishwakarma": orchestrator.agents.get("vishwakarma"),
        "divya": orchestrator.agents.get("divya"),
        "yama": orchestrator.agents.get("yama"),
        "manas": orchestrator.agents.get("manas")
    }
    # Remove None values in case some agents are disabled/unregistered
    agents_dict = {k: v for k, v in agents_dict.items() if v}
    
    bg_loop = BackgroundAgentLoop(findings_queue, agents_dict)
    bg_loop.start()
    
    permission_handler = PermissionHandler(nova_speak_fn=speak, nova_listen_fn=ls.listen_for_command)
    
    turn_count = 0
    
    import msvcrt 
    last_interaction_time = time.time()
    IDLE_TIMEOUT = 300 # 5 minutes

    # Start mobile API server in background thread
    from jarvis.api.server import app, init_nova
    import threading
    import uvicorn
    import socket

    def start_mobile_server():
        init_nova(orchestrator, speak, knowledge_db, findings_queue)
        uvicorn.run(app, host="0.0.0.0", port=8080, log_level="warning")

    mobile_thread = threading.Thread(target=start_mobile_server, daemon=True)
    mobile_thread.start()
    print("[MOBILE] API server started — connect phone on port 8080")

    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"[MOBILE] Phone pe ye URL use karo: http://{local_ip}:8080")

    while True:
        # Step 0: Proactive Check (if idle)
        if time.time() - last_interaction_time > IDLE_TIMEOUT:
            emotion, stress = engine.get()
            proactive_msg = brain.get_proactive_prompt(emotion=emotion, stress=stress)
            speak(proactive_msg, emotion=emotion)
            last_interaction_time = time.time()

        # print(f"[NOVA] Listening... (Current Mood: {engine.get()[0]})")
        send_event("STATUS_UPDATE", {"status": "LISTENING"})
        
        # Step 1: Wait for Wake Word (with Findings Check)
        trigger_detected = False
        while not trigger_detected:
            # Check HIGH priority findings immediately
            finding = findings_queue.pop_highest()
            if finding:
                permission_handler.handle_finding(finding)
            
            # Check for wake word
            trigger_detected = ls.listen_for_wake_word_streaming()
            
            # Non-blocking keyboard check
            if msvcrt.kbhit():
                break
            time.sleep(0.1) # Small sleep to prevent CPU spike and allow key hits
        
        if not trigger_detected and not msvcrt.kbhit():
            continue

        if msvcrt.kbhit():
            # Keyboard mode
            msvcrt.getch() 
            send_event("STATUS_UPDATE", {"status": "THINKING"})
            speak("Keyboard mode active. How can I help, Sir?")
            command = input("[YOU]: ")
        else:
            # Voice mode
            send_event("STATUS_UPDATE", {"status": "SPEAKING"})
            speak("Yes, Sir?")
            send_event("STATUS_UPDATE", {"status": "LISTENING"})
            command = ls.listen_for_command()

        turn_count += 1
        
        # Every 10 turns, give LOW priority summary
        if turn_count % 10 == 0:
            low_findings = findings_queue.pop_all_low()
            if low_findings:
                summary = ", ".join([f.title for f in low_findings])
                speak(f"Sir, a quick update from the background: {summary}")

        if not command:
            send_event("STATUS_UPDATE", {"status": "IDLE"})
            continue
            
        last_interaction_time = time.time()
        
        # ── Emotion Analysis ──────────────────────────────────
        # Optional: Analyze voice tone of the current command
        # This requires the listener to return the raw audio array
        # For now, we rely on the continuous face detection
        current_emotion, current_stress = engine.get()
        current_pattern = engine.get_pattern()
        
        # ── LLM Brain Processing (ReAct Engine) ─────────────────
        send_event("STATUS_UPDATE", {"status": "THINKING"})
        
        stop_loading = False
        def loading_animation():
            chars = [".", "..", "...", "   "]
            idx = 0
            while not stop_loading:
                sys.stdout.write(f"\r[NOVA] Thinking{chars[idx % 4]}")
                sys.stdout.flush()
                idx += 1
                time.sleep(0.4)
            sys.stdout.write("\r" + " " * 30 + "\r") # Clear line

        start_time = time.time()
        loading_thread = threading.Thread(target=loading_animation, daemon=True)
        loading_thread.start()
        
        try:
            if "agent status" in command.lower() or "background" in command.lower():
                status = bg_loop.status()
                q_size = findings_queue.size()
                response = f"All background agents are online: {status}. There are currently {q_size} findings in the queue."
            elif any(w in command.lower() for w in ["kitna seekhi", "db stats", "knowledge"]):
                stats = knowledge_db.stats()
                response = (
                    f"Bhai ab tak {stats['total_entries']} verified answers mere paas hain. "
                    f"{stats['api_calls_saved']} baar API call bach gayi. "
                    f"~${stats['estimated_cost_saved']} save hua OpenAI pe."
                )
            else:
                # USE REACT ENGINE — the new brain
                context = {
                    "emotion": current_emotion,
                    "stress": current_stress,
                    "pattern": current_pattern
                }
                
                # Check for ghost mode trigger
                if "ghost mode on" in command.lower() or "silent mode" in command.lower():
                    ghost.activate()
                    response = "Ghost mode activated."
                elif "ghost mode off" in command.lower():
                    results = ghost.deactivate()
                    response = f"Ghost mode deactivated. Executed {len(results)} silent tasks."
                else:
                    if ghost.active:
                        ghost.add_task(command)
                        response = "" # No vocal response in ghost mode
                        sys.stdout.write(f"\r[GHOST] Task added to queue.\n")
                    else:
                        response = orchestrator.process(command)
                        # Record pattern
                        chronos.record(action_type="command", action_detail=command, emotion=current_emotion)
                        
                        # Check for anomalies
                        anomaly = chronos.detect_anomaly()
                        if anomaly:
                            response = f"{anomaly}\n\n{response}"
                            
        except Exception as e:
            print(f"[ERROR] ReAct engine failed, falling back: {e}")
            # Fallback to direct ollama chat
            fb_response = ollama.chat(model="qwen2.5:7b", messages=[{"role": "user", "content": command}])
            response = fb_response['message']['content']
        finally:
            stop_loading = True
            loading_thread.join()
            elapsed = time.time() - start_time
            print(f"[NOVA] Response generated in {elapsed:.2f}s")
        # ===REPLACE END===
        
        # ── Action Execution ──────────────────────────────────
        speech_output = response
        
        # Find action (case-insensitive)
        import re
        action_match = re.search(r"ACTION:\s*(\w+)\s*\|\s*param:\s*(.*)", response, re.IGNORECASE)
        
        if action_match:
            try:
                tool_name = action_match.group(1).strip().lower()
                param = action_match.group(2).strip()
                
                print(f"[NOVA ACTION]: Detected {tool_name} with param: {param}")
                
                # Execute
                from jarvis.core.body.tools import execute_tool
                tool_result = execute_tool(tool_name, **({"app_name": param, "query": param, "level": param, "url": param, "file_path": param}))
                
                print(f"[NOVA TOOL RESULT]: {tool_result}")

                # Clean speech from action line
                speech_output = re.sub(r"ACTION:.*", "", response, flags=re.IGNORECASE).strip()
                if not speech_output:
                    speech_output = tool_result
            except Exception as e:
                print(f"[ACTION ERROR]: {e}")

        # Sync emotion with Frontend Avatar
        send_event("EMOTION_UPDATE", {"emotion": current_emotion})
        
        speak(speech_output, emotion=current_emotion)
        send_event("STATUS_UPDATE", {"status": "IDLE"})

if __name__ == "__main__":
    main()