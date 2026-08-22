from fastapi import APIRouter, Depends
from jarvis.api.auth import get_current_user
from jarvis.api.models import User

router = APIRouter()

try:
    import ollama
except ImportError:
    ollama = None

@router.post("/pipeline")
async def pipeline_endpoint(
    payload: dict,
    current_user: User = Depends(get_current_user)
):
    query = payload.get("query", "")
    
    print(f"[PIPELINE] Stage 1: Planning...")
    if ollama:
        plan_response = ollama.chat(
            model="gemma3:4b",
            messages=[{
                "role": "system",
                "content": "You are a software architect. Create an implementation plan."
            }, {
                "role": "user",
                "content": f"Plan this: {query}"
            }],
            options={"temperature": 0.3, "num_predict": 400}
        )
        plan = plan_response['message']['content']
    else:
        plan = "Mock plan: 1. Do A 2. Do B"
        
    print(f"[PIPELINE] Plan ready: {plan[:100]}...")
    
    print(f"[PIPELINE] Stage 2: Implementing...")
    if ollama:
        code_response = ollama.chat(
            model="qwen2.5-coder:7b",
            messages=[{
                "role": "system",
                "content": "You are an expert programmer. Implement the plan."
            }, {
                "role": "user",
                "content": f"Original request: {query}\n\nImplementation plan:\n{plan}\n\nNow write the complete code:"
            }],
            options={"temperature": 0.2, "num_predict": 2000}
        )
        code = code_response['message']['content']
    else:
        code = "def mock_implementation():\n    pass"
        
    return {
        "query":  query,
        "plan":   plan,
        "code":   code,
        "stages": ["gemma3:4b (planner)", "qwen2.5-coder:7b (coder)"],
        "agent":  "VISHWAKARMA"
    }
