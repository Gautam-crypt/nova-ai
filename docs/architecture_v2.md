# NOVA (Jarvis) v2.0 - Architecture & Working Procedures

Yeh document NOVA (Jarvis) v2.0 AI system ki puri architecture aur step-by-step working ko explain karta hai. Yeh project ek unrestricted, highly modular, multi-agent OS-level AI system hai jo dynamic tool generation aur deep packet inspection jaisi advanced capabilities rakhta hai.

## 1. Project Structure & Tech Stack

### Backend (Python)
- **Entry Point:** `main.py`
- **Orchestrator & Engine:** `jarvis/core/orchestrator.py` & `jarvis/core/brain/react_engine.py`
- **Models:** Local LLMs via `Ollama` (`llama3.1:8b` for ReAct/tool-calling, `llava` for vision).
- **Memory/VectorDB:** `ChromaDB` (Local RAG aur memory ke liye), `SQLite` (Chronos and Security logging).
- **Security (KAVACH):** `scapy` (Deep Packet Inspection), `psutil` (Process Guard), Windows Firewall integration.
- **Dynamic Execution:** Sandboxed dynamic python code generation and execution (`dynamic_executor.py`).
- **OS Control:** `pyautogui`, `pygetwindow`, `win32api`, `ctypes` for universal app control.
- **Web API:** `FastAPI`, `Uvicorn` (Port 8080 par mobile connection ke liye).

### Frontend (Native Android & Next.js)
- **Mobile (Phase 5):** React Native + Expo (Local ONNX models for offline inference).
- **Dashboard:** Next.js 15+ (React 19), Tailwind CSS, Framer Motion.

---

## 2. Core Components (The Pantheon)

Project ka "Brain" ab ek **ReActEngine (Reason + Act)** aur **NOVAOrchestrator** ka combination hai, jo user ki query ko samajhta hai, dynamic code likhta hai, aur relevant "Agents" ko task assign karta hai.

### Agent List (jarvis/agents/):
1. **DIVYA (Vision & Perception):** Camera feed analyze karti hai. LLaVA model use karke scene description aur posture check karti hai.
2. **HERMES (Web Intelligence):** DuckDuckGo Search (DDGS) use karke real-time internet search, news, aur weather fetch karta hai.
3. **KAVACH (Security - NEW):** Full-spectrum cyber warfare agent. Deep packet inspection, network recon, port scanning, honeypots aur process guarding handle karta hai.
4. **VISHWAKARMA (Engineering):** Code analysis aur fixed execution ke liye.
5. **YAMA (Automation):** System files aur hardware monitoring ke liye.
6. **MANAS (Emotion):** Emotion engine ke data se user ka mood samajhta hai.

---

## 3. Step-by-Step Working Procedure (Kaise Kaam Karta Hai)

### Step 1: System Boot & Authentication (`main.py`)
- Script run hone par **Auth Gate** trigger hota hai.
- **KAVACH Modules** background mein start ho jate hain (NetworkSentinel, ProcessGuardian, DeepPacketInspector).
- FastAPI server start hota hai mobile devices ke connect karne ke liye.

### Step 2: Background Surveillance & Tracking
- **Deep Packet Inspector:** Local WiFi ka saara traffic capture aur decode karta hai.
- **Network Sentinel:** ARP spoofing, rogue devices aur port scans detect karke block karta hai.
- **Chronos Engine:** User ka behavior track karta hai (kab kya apps use kiye) taaki future actions predict kar sake.
- **Findings Queue:** Koi bhi suspicious activity ya notification `FindingsQueue` mein push hota hai.

### Step 3: Input & ReAct Loop Processing (`react_engine.py`)
1. User command deta hai.
2. Orchestrator pehle contextual information gather karta hai (Agents se).
3. **ReAct Engine (Think -> Act -> Observe):**
   - **THINK:** LLM dekhta hai ki task perform karne ke liye kaunse tools chahiye.
   - **DECIDE:** Agar existing tool hai toh use karta hai, warna **Dynamic Code Generation** trigger karta hai.
   - **ACT:** Generated code ya tool ko `DynamicExecutor` mein sandboxed run karta hai.
   - **OBSERVE:** Code ka output/errors dekhta hai aur loop continue karta hai tab tak jab tak final result nahi milta.

### Step 4: Universal OS Control
- NOVA ab API tak simit nahi hai. Agar koi third-party app control karni hai, toh wo dynamically `pyautogui` aur `pygetwindow` use karke UI elements dhoondhta hai aur click/type karta hai.

### Step 5: Ghost Mode
- Agar user ne "Ghost mode ON" bola hai, toh NOVA apna GUI hide kar leta hai aur saare tasks completely silently perform karta hai, bina koi notification diye.

---

## 4. Advanced Capabilities

1. **Omniscient Dynamic Tools:** Fixed tools ki dependency khatam. NOVA code likh ke kisi bhi situation ko handle kar sakta hai.
2. **Network Warfare:** Packet level par message intercepts, traffic analysis aur auto-blocking of IP threats.
3. **Chronos (Predictive Intelligence):** Time aur daily habits ke basis par NOVA khud pro-active actions suggest karta hai.
4. **Honeypots & Spyware Detection:** Fake sensitive files (honeypots) deploy karta hai aur agar koi software inhe padhta hai toh turant system ko alert/lockdown karta hai.

## Summary
NOVA v2.0 ek true unrestricted agentic AI hai. Yeh ab sirf respond nahi karta, balki real-time code generate aur execute karke actually **action** leta hai, saath hi KAVACH subsystem ke through puri network security aur system integrity ko ensure karta hai.
