# NOVA v2.0 - Testing Walkthrough & Guide

This guide will walk you through how to start and test the newly implemented features in the NOVA v2.0 architecture. 

> [!NOTE]
> Ensure you have [Ollama](https://ollama.com/) running locally with the `llama3.1:8b` (or your configured model) before starting.

---

## 1. Starting the System

To boot up the system, run your main entry point from your terminal:

```bash
cd "C:\Users\GAUTAM\Desktop\Project X"
python main.py
```

**What happens on boot:**
1. You will be greeted and asked for camera permissions (if your auth module is active).
2. You will see `[KAVACH] All defensive security modules armed.` indicating that Network Sentinel, Process Guardian, and Counter-Intel are active in the background.
3. The ReAct Engine will initialize and register all the tools from `system_tools.py` and `os_controller.py`.

---

## 2. Testing Phase 1: ReAct Engine & Dynamic Execution

NOVA is no longer restricted to hardcoded commands. It uses a **Think → Act → Observe** loop.

### Test 1: Using Pre-built System Tools
Speak or type: 
> *"Open notepad and type 'Hello NOVA, the system is online'."*

**Expected Behavior:** 
- The ReAct Engine will decide to use the `open_app` tool with parameter `notepad`.
- It will wait 1-2 seconds, then use the `type_text` tool to write the text.

### Test 2: Dynamic Code Generation (The Omniscient Engine)
Speak or type:
> *"Create a new folder on my Desktop called 'NOVA_TEST' and put a text file inside it saying 'Test successful'."*

**Expected Behavior:**
- NOVA will realize it doesn't have a single pre-built tool for this exact sequence.
- It will generate a dynamic Python script using the `os` module.
- It will ask for your permission: `[PERMISSION] PHANTOM wants to execute generated code. Allow?`
- If you say "yes", it will execute the code and create the folder/file.

> [!CAUTION]
> NOVA has full OS access. It will prompt you before running dynamic code or destructive tools (like `close_app` or `delete_file`). Always review the preview carefully.

---

## 3. Testing Phase 2: KAVACH (Defensive Security)

KAVACH modules run silently in the background (`network_sentinel.py`, `process_guardian.py`, `counter_intel.py`).

### Test 1: Honeypots & Counter-Intelligence
1. Go to your Desktop and find the newly created `passwords_backup.txt` (this is a decoy file deployed by Counter-Intel).
2. Open it using Notepad.
3. **Expected Behavior:** Within 5 seconds, KAVACH will detect that a process accessed the honeypot. It will push a `HIGH` priority finding to the queue, alerting you that the system might be compromised, and will ask for permission to wipe the digital footprint.

### Test 2: Network Audit
Speak or type:
> *"Scan my network and tell me what devices are connected."*

**Expected Behavior:**
- The KAVACH agent will intercept this query.
- It will trigger `NetworkSentinel.scan_network()`.
- It will read the ARP table and report back a list of local IP and MAC addresses currently on your network.

---

## 4. Testing Phase 3: Ghost Mode & Chronos

### Test 1: Ghost Mode (Silent Execution)
Speak or type:
> *"Ghost mode on"*

**Expected Behavior:** 
- You will see `[GHOST] Mode activated`.
- Now give a command: *"Open calculator"*
- You will NOT hear NOVA speak. The task will be queued and executed completely silently in the background.
- Finally, type: *"Ghost mode off"* to receive a summary of all tasks executed silently.

### Test 2: Chronos (Predictive Intelligence)
Chronos tracks your habits in `data/chronos.db`.
1. Give a few normal commands (e.g., *"Open VS Code"*, *"What's the weather"*).
2. Chronos silently records these alongside the current hour, day, and your emotional state.
3. **Anomaly Detection:** If you use the system at an unusual hour (e.g., 3:00 AM) and Chronos has no previous data for that hour, it will automatically prepend its response with: *"Bhai, tu is waqt usually soya hota hai. Neend nahi aa rahi kya? Sab theek hai?"*

---

> [!TIP]
> **Logs & Debugging:** Keep an eye on your terminal output. The ReAct engine prints `[REACT]` logs showing exactly what the LLM is thinking, the JSON it generated, and the code it's executing. This is highly useful for debugging prompt mismatches.

