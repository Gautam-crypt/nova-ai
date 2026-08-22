from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from pydantic import BaseModel
import uuid

from jarvis.api.database import get_db
from jarvis.api.models import User, APIKey, Plan
from jarvis.api.auth import get_current_user, hash_password
from jarvis.api.schemas import UserResponse, ProfileUpdate

router = APIRouter()

class APIKeyCreate(BaseModel):
    name: str

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
def update_me(profile: ProfileUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if profile.full_name is not None:
        current_user.full_name = profile.full_name
    if profile.nova_name is not None:
        current_user.nova_name = profile.nova_name
    if profile.nova_language is not None:
        current_user.nova_language = profile.nova_language
    if profile.nova_personality is not None:
        current_user.nova_personality = profile.nova_personality
        
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/me/usage")
def get_usage(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.id == current_user.plan_id).first()
    limit = plan.messages_per_day if plan else 50
    return {
        "messages_today": current_user.messages_today,
        "messages_total": current_user.messages_total,
        "limit": limit,
        "percent_used": (current_user.messages_today / limit * 100) if limit > 0 else 0,
        "reset_time": "Midnight UTC"
    }

@router.get("/me/api-keys")
def list_api_keys(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    keys = db.query(APIKey).filter(APIKey.user_id == current_user.id, APIKey.is_active == True).all()
    return [{"id": k.id, "name": k.name, "created_at": k.created_at} for k in keys]

@router.post("/me/api-keys")
def create_api_key(key_data: APIKeyCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plain_key = f"nova_key_{uuid.uuid4().hex}"
    hashed_key = hash_password(plain_key)
    
    new_key = APIKey(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        key_hash=hashed_key,
        name=key_data.name
    )
    db.add(new_key)
    db.commit()
    
    return {"id": new_key.id, "name": new_key.name, "api_key": plain_key, "message": "Save this key, it will not be shown again."}

@router.delete("/me/api-keys/{key_id}")
def delete_api_key(key_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    key = db.query(APIKey).filter(APIKey.id == key_id, APIKey.user_id == current_user.id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API Key not found")
        
    key.is_active = False
    db.commit()
    return {"message": "API Key revoked"}
