from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime
from jarvis.api.models import PlanType, UserRole

class PlanBase(BaseModel):
    name: str
    plan_type: PlanType
    price_monthly: float
    price_yearly: float
    messages_per_day: int
    memory_enabled: bool = False
    custom_personality: bool = False
    agents_enabled: str
    stripe_price_id: str
    is_active: bool = True

class PlanCreate(PlanBase):
    id: str

class PlanResponse(PlanBase):
    id: str
    class Config:
        from_attributes = True

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: UserRole
    plan_id: str
    subscription_status: str
    nova_name: str
    nova_language: str
    messages_today: int
    messages_total: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None

class RefreshRequest(BaseModel):
    refresh_token: str

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    nova_name: Optional[str] = None
    nova_language: Optional[str] = None
    nova_personality: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    file_ids: Optional[List[str]] = []

class ConversationBase(BaseModel):
    title: str

class ConversationResponse(ConversationBase):
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    role: str
    content: str
    agent_used: Optional[str] = None
    response_time: Optional[float] = None

class MessageResponse(MessageBase):
    id: int
    conversation_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class UploadedFileResponse(BaseModel):
    id: str
    filename: str
    content_type: str
    size_mb: float
    chunks: int
    uploaded_at: datetime
    class Config:
        from_attributes = True

class SystemErrorResponse(BaseModel):
    id: int
    error_type: str
    message: str
    endpoint: Optional[str] = None
    user_id: Optional[str] = None
    status: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    class Config:
        from_attributes = True
