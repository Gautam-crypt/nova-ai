import json
import chromadb
import os
from jarvis.api.models import User, Plan
from jarvis.api.database import SessionLocal

chroma_client = chromadb.PersistentClient(path="data/memory")

class DummyOrchestrator:
    def chat(self, *args, **kwargs):
        return "I am the orchestrator"

orchestrator = DummyOrchestrator()

class NOVAFactory:
    """
    Har user ke liye alag NOVA instance banata hai.
    Unka apna memory, personality, agents.
    """
    
    def get_nova_config(self, user: User, plan: Plan) -> dict:
        personality = json.loads(user.nova_personality or "{}")
        
        system_prompt = f"""
Tu {user.nova_name} hai — {user.full_name} ki personal AI assistant.
Language: {user.nova_language}
Style: {personality.get('style', 'friendly and casual')}
"""
        
        allowed_agents = json.loads(plan.agents_enabled or "[]") if plan else []
        
        return {
            "system_prompt":      system_prompt,
            "memory_collection":  user.nova_memory_collection,
            "allowed_agents":     allowed_agents,
            "messages_limit":     plan.messages_per_day if plan else 50,
            "memory_enabled":     plan.memory_enabled if plan else False
        }

    def get_orchestrator_for_user(self, user: User):
        user_collection = chroma_client.get_or_create_collection(
            name=user.nova_memory_collection
        )
        
        db = SessionLocal()
        plan = db.query(Plan).filter(Plan.id == user.plan_id).first()
        db.close()
        
        config = self.get_nova_config(user, plan)
        system_prompt = config["system_prompt"]
        
        return {
            "orchestrator": orchestrator,  
            "memory":       user_collection,
            "prompt":       system_prompt,
            "agents":       config["allowed_agents"]
        }
