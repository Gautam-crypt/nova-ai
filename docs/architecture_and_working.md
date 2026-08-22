# NOVA (Jarvis) - Architecture & Working Procedures

Yeh document NOVA (Jarvis) AI system ki puri architecture aur step-by-step working ko explain karta hai. Yeh project ek highly modular, multi-agent AI system hai jo voice, vision, aur local LLMs karkeko combine  ek personal assistant (UP/Delhi style Hinglish) create karta hai.

## 1. Project Structure & Tech Stack

### Backend (Python)
- **Entry Point:** `main.py`
- **Orchestrator:** `jarvis/core/orchestrator.py`
- **Models:** Local LLMs via `Ollama` (gemma3:4b, qwen2.5:7b, llava for vision).
- **Memory/VectorDB:** `ChromaDB` (Local RAG aur memory ke liye).
- **Vision:** `OpenCV`, `MediaPipe` (Pose/Face tracking), `DeepFace` (Emotion detection).
- **Voice/Audio:** `SpeechRecognition`, `OpenAI-Whisper`, `pyttsx3` (TTS).
- **Web API:** `FastAPI`, `Uvicorn` (Port 8080 par mobile connection ke liye).

### Frontend (Next.js)
- **Framework:** Next.js 15+ (React 19)
- **Styling & UI:** Tailwind CSS, Framer Motion (Animations), `@react-three/fiber` (3D Elements).
- **State Management:** `Zustand`.
- **Communication:** Axios (to talk with the FastAPI backend).

---

## 2. Core Components (The Pantheon)

Project ka "Brain" ek **NOVAOrchestrator** hai, jo user ki query ko samajhta hai aur relevant "Agents" ko task assign karta hai.

### Agent List (jarvis/agents/):
1. **DIVYA (Vision & Perception):** Camera feed analyze karti hai. LLaVA model use karke scene description aur posture check karti hai.
2. **HERMES (Web Intelligence):** DuckDuckGo Search (DDGS) use karke real-time internet search, news, aur weather fetch karta hai.
3. **VISHWAKARMA (Engineering):** Code analysis, execution aur terminal commands ke liye.
4. **YAMA (Automation):** System files, automation, aur hardware monitoring ke liye.
5. **MANAS (Emotion):** Emotion engine ke data se user ka mood samajhta hai aur psychological guidance deta hai.
6. **MEMORY_AGENT:** ChromaDB se past facts aur context retrieve karta hai.
7. **LIBRARIAN:** Knowledge management aur naye documents ingest karne ka kaam.

---

## 3. Step-by-Step Working Procedure (Kaise Kaam Karta Hai)

### Step 1: System Boot & Authentication (`main.py`)
- Script run hone par sabse pehle **Auth Gate** trigger hota hai (Face ID ya passcode check).
- **Camera Permission:** User se camera on karne ki permission maangi jaati hai ("Sir, security is clear...").
- **Emotion Engine:** Agar camera on hai, toh background mein EmotionEngine start ho jata hai jo continuously user ka mood aur stress detect karta hai.
- **FastAPI Server:** Mobile/Remote app ke liye port 8080 par API server background thread mein chalu ho jata hai.

### Step 2: Background Loop & Findings Queue
- System idle hone par ek **BackgroundAgentLoop** run karta hai.
- Agents (jaise Divya, Hermes) background mein chizein scan karte hain (e.g., posture checking, latest news).
- Agar kuch milta hai, toh wo ek **FindingsQueue** mein push karte hain.
- High priority finding turant boli jaati hai, aur Low priority findings har 10 turns ke baad summarize karke batai jaati hain.

### Step 3: Input Capture (Listening)
- User ya toh **Wake Word** bolega ya **Keyboard** se input dega.
- Microphone se Whisper model ke through speech-to-text convert hota hai.

### Step 4: Orchestration & Routing (`orchestrator.py`)
- User ka prompt jab Orchestrator ke paas aata hai, toh wo decide karta hai ki is task ke liye kaunsa/kaunse Agent(s) best rahenge.
- Pehle **Keyword Matching** hoti hai (e.g., "dekh" -> Divya, "search" -> Hermes).
- Phir LLM (gemma3/qwen) ka use karke secondary routing hoti hai taaki smart decision liya ja sake.

### Step 5: Parallel Execution
- Orchestrator selected agents ko **ThreadPoolExecutor** ke through parallel mein execute karta hai.
- Har agent apna task complete karke `AgentResult` return karta hai.

### Step 6: Response Aggregation & Persona
- Saare agents ka raw data milne ke baad, Orchestrator use ek single LLM prompt mein daalta hai.
- **Personality Engine:** Yeh sabse important part hai. Yahan prompt mein instructions hoti hain ki NOVA ko "UP/Delhi style Hinglish" mein dost ki tarah baat karni hai (e.g., "tu/tujhe", "yaar", "bhai" use karna).
- LLM data ko process karke ek short, natural response generate karta hai.

### Step 7: Action Execution & TTS
- Agar response mein koi Action (jaise `ACTION: open_app | param: chrome`) hai, toh use execute kiya jata hai.
- Final clean text ko `pyttsx3` (Text-to-Speech) ke through bol diya jata hai.
- Frontend ko WebSockets/Events ke through "EMOTION_UPDATE" bheji jaati hai taaki avatar ka expression change ho.

---

## 4. Smart Learning System
- `jarvis/core/learning/` mein KnowledgeDB aur SmartResponder maujood hain.
- NOVA pichli conversations se seekhti hai aur ChromaDB mein save karti hai taaki har baar mehnge API calls ya slow generation ki zarurat na pade (cost saving).

## Summary
Yeh project ek offline-first, highly capable agentic assistant hai jo sunta hai (Whisper), dekhta hai (Mediapipe + LLaVA), sochta hai (Multiple Agents + Ollama), aur react karta hai (Hinglish TTS + Actions), saath hi ek Next.js 3D dashboard par user ko visual interface provide karta hai.
