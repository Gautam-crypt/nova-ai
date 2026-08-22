from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
import uuid
import json
import time

from jarvis.api.auth import get_current_user
from jarvis.api.models import User

router = APIRouter()

try:
    import ollama
except ImportError:
    ollama = None

@router.post("/v1/chat/completions")
async def openai_chat(
    data: dict,
    current_user: User = Depends(get_current_user)  # Assuming we use normal JWT for now, API key middleware can inject this too
):
    messages    = data.get("messages", [])
    model       = data.get("model", "gemma3:4b")
    stream      = data.get("stream", False)
    max_tokens  = data.get("max_tokens", 1000)
    temperature = data.get("temperature", 0.7)
    
    user_message = next(
        (m["content"] for m in reversed(messages) if m["role"] == "user"),
        ""
    )
    
    if stream:
        async def generate():
            chat_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
            if ollama:
                stream_resp = ollama.chat(
                    model=model,
                    messages=messages,
                    stream=True,
                    options={"temperature": temperature, "num_predict": max_tokens}
                )
                for chunk in stream_resp:
                    token = chunk['message']['content']
                    payload = {
                        "id":      chat_id,
                        "object":  "chat.completion.chunk",
                        "created": int(time.time()),
                        "model":   model,
                        "choices": [{
                            "delta":         {"content": token},
                            "index":         0,
                            "finish_reason": None
                        }]
                    }
                    yield f"data: {json.dumps(payload)}\n\n"
            else:
                # Mock streaming
                import asyncio
                for token in ["Mock", " ", "OpenAI", " ", "Stream"]:
                    await asyncio.sleep(0.1)
                    payload = {
                        "id": chat_id, "object": "chat.completion.chunk", "created": int(time.time()),
                        "model": model, "choices": [{"delta": {"content": token}, "index": 0, "finish_reason": None}]
                    }
                    yield f"data: {json.dumps(payload)}\n\n"
            
            yield f"data: {json.dumps({'choices': [{'delta': {}, 'finish_reason': 'stop'}]})}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(generate(), media_type="text/event-stream")
    else:
        if ollama:
            response = ollama.chat(
                model=model,
                messages=messages,
                options={"temperature": temperature, "num_predict": max_tokens}
            )
            content = response['message']['content']
        else:
            content = "Mock OpenAI Response"
            
        return {
            "id":      f"chatcmpl-{uuid.uuid4().hex[:8]}",
            "object":  "chat.completion",
            "created": int(time.time()),
            "model":   model,
            "choices": [{
                "message":       {"role": "assistant", "content": content},
                "index":         0,
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens":     len(user_message.split()),
                "completion_tokens": len(content.split()),
                "total_tokens":      len(user_message.split()) + len(content.split())
            }
        }
