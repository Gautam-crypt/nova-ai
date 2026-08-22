from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
import asyncio
import os

from jarvis.api.main import app

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global NOVA orchestrator reference
nova_orchestrator = None
nova_speak = None
nova_knowledge_db = None
nova_findings_queue = None

def init_nova(orchestrator, speak_fn, knowledge_db=None, findings_queue=None):
    global nova_orchestrator, nova_speak, nova_knowledge_db, nova_findings_queue
    nova_orchestrator = orchestrator
    nova_speak = speak_fn
    nova_knowledge_db = knowledge_db
    nova_findings_queue = findings_queue

@app.post("/chat")
async def chat(payload: dict):
    """
    Phone se text message aayega → NOVA process karegi → response
    """
    user_message = payload.get("message", "")
    if not user_message:
        return {"reply": "Kuch bola nahi tune", "emotion": "neutral"}
    
    # NOVA se process karo
    result = nova_orchestrator.process(user_message)
    
    return {
        "reply":   result,
        "emotion": "neutral",  # MANAS se aayega baad mein
        "source":  "nova"
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Real-time conversation via WebSocket
    """
    await websocket.accept()
    print("[MOBILE] Phone connected via WebSocket")
    
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            user_msg = payload.get("message", "")
            
            # Process
            response = nova_orchestrator.process(user_msg)
            
            await websocket.send_text(json.dumps({
                "reply":   response,
                "emotion": "neutral"
            }))
    except Exception as e:
        print(f"[MOBILE] Connection closed: {e}")

@app.get("/status")
async def status():
    """Phone se check karo — NOVA online hai?"""
    return {
        "status": "online",
        "agents": ["hermes","vishwakarma","divya","yama","manas"],
        "message": "NOVA online hai bhai 🔥"
    }

@app.get("/knowledge/stats")
async def knowledge_stats():
    """Phone se check karo — NOVA kitna seekhi"""
    if nova_knowledge_db:
        return nova_knowledge_db.stats()
    return {"message": "Stats endpoint — wire up with knowledge_db"}

@app.get("/findings")
async def get_findings():
    """Phone se check karo — KAVACH security alerts"""
    if not nova_findings_queue:
        return {"findings": []}
    
    # Return all findings without removing them from queue for monitoring
    findings = []
    # Peek at all items safely
    with nova_findings_queue.lock:
        items = list(nova_findings_queue.queue)
        for _, _, f in sorted(items, key=lambda x: x[0]):
            findings.append({
                "title": f.title,
                "detail": f.detail,
                "priority": f.priority.value,
                "timestamp": f.timestamp
            })
    return {"findings": findings}

@app.post("/feedback")
async def feedback(payload: dict):
    """
    Phone se thumbs up/down do — NOVA seekhegi
    """
    question = payload.get("question")
    answer   = payload.get("answer")
    rating   = payload.get("rating", 3)
    
    # 4+ rating → directly save to knowledge_db
    if rating >= 4 and nova_knowledge_db:
        nova_knowledge_db.save(
            question         = question,
            local_answer     = answer,
            verified_answer  = answer,
            quality_score    = rating / 5.0,
            corrections_made = False,
            source           = "user_approved_mobile",
            topic_tag        = "user_feedback"
        )
        return {"status": "saved", "message": "NOVA ne seekh liya! 🧠"}
    
    return {"status": "skipped", "message": "Theek hai, skip kar diya"}

static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/", StaticFiles(directory=static_dir, html=True))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
