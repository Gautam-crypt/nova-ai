from fastapi import APIRouter, Depends, WebSocket, Query, HTTPException
from sqlalchemy.orm import Session
from jarvis.api.database import get_db
from jarvis.api.models import User, UsageLog, Plan
from jarvis.api.auth import get_current_user
from jarvis.api.schemas import ChatRequest
from jarvis.api.nova_factory import NOVAFactory
import time

router = APIRouter()
factory = NOVAFactory()

@router.post("/chat")
def chat(request: ChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")
        
    start_time = time.time()
    
    plan = db.query(Plan).filter(Plan.id == current_user.plan_id).first()
    limit = plan.messages_per_day if plan else 50
    if limit != -1 and current_user.messages_today >= limit:
        raise HTTPException(status_code=429, detail="Daily limit reached")
        
    current_user.messages_today += 1
    current_user.messages_total += 1
    
    nova_instance = factory.get_orchestrator_for_user(current_user)
    
    reply = f"Hello {current_user.full_name}, I am {current_user.nova_name}. You said: {request.message}"
    
    response_time = time.time() - start_time
    usage = UsageLog(
        user_id=current_user.id,
        message=request.message,
        response=reply,
        agent_used="NOVA_CORE",
        response_time=response_time
    )
    db.add(usage)
    db.commit()
    
    return {"reply": reply, "emotion": "happy", "agent_used": "NOVA_CORE", "response_time": response_time}

@router.post("/chat/stream")
async def chat_stream(payload: dict, current_user: User = Depends(get_current_user)):
    """
    SSE streaming — token by token response.
    Frontend ko lagega NOVA typing kar rahi hai.
    """
    from fastapi.responses import StreamingResponse
    import json
    
    # Mocking ollama import for now if it doesn't exist
    try:
        import ollama
    except ImportError:
        ollama = None
        
    user_message = payload.get("message", "")
    
    async def generate():
        if ollama:
            stream = ollama.chat(
                model="gemma3:4b",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user",   "content": user_message}
                ],
                stream=True,
                options={"temperature": 0.7, "num_predict": 300}
            )
            
            full_response = ""
            for chunk in stream:
                token = chunk['message']['content']
                full_response += token
                yield f"data: {json.dumps({'token': token, 'done': False})}\n\n"
                
            yield f"data: {json.dumps({'token': '', 'done': True, 'full': full_response})}\n\n"
        else:
            # Fallback mock streaming
            import asyncio
            tokens = ["Hello", " ", "there!", " ", "This", " ", "is", " ", "a", " ", "mock", " ", "stream."]
            full_response = "".join(tokens)
            for t in tokens:
                await asyncio.sleep(0.1)
                yield f"data: {json.dumps({'token': t, 'done': False})}\n\n"
            yield f"data: {json.dumps({'token': '', 'done': True, 'full': full_response})}\n\n"
            
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...)  # ?token=JWT_TOKEN
):
    from jarvis.api.auth import SECRET_KEY, ALGORITHM
    from jose import jwt, JWTError
    from jarvis.api.database import SessionLocal
    
    db = SessionLocal()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            await websocket.close(code=4001)
            return
            
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            await websocket.close(code=4001)
            return
            
    except Exception:
        await websocket.close(code=4001)
        db.close()
        return
        
    await websocket.accept()
    await websocket.send_json({"message": f"Connected to {user.nova_name}"})
    
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"reply": f"Echo: {data}"})
    except Exception:
        pass
    finally:
        db.close()

@router.get("/memory")
def get_memory(current_user: User = Depends(get_current_user)):
    nova_instance = factory.get_orchestrator_for_user(current_user)
    return {"history": ["Message 1", "Message 2"]}

@router.delete("/memory")
def clear_memory(current_user: User = Depends(get_current_user)):
    nova_instance = factory.get_orchestrator_for_user(current_user)
    return {"message": "Memory cleared"}
