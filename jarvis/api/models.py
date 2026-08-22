from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
import enum
import datetime

Base = declarative_base()

class PlanType(enum.Enum):
    FREE       = "free"        # 50 messages/day, no memory
    PRO        = "pro"         # 500 messages/day, full memory
    ENTERPRISE = "enterprise"  # unlimited, custom personality

class UserRole(enum.Enum):
    ADMIN = "admin"
    USER  = "user"

class Plan(Base):
    __tablename__ = "plans"
    
    id                = Column(String, primary_key=True)  # uuid
    name              = Column(String)   # "Free", "Pro", "Enterprise"
    plan_type         = Column(Enum(PlanType))
    price_monthly     = Column(Float)    # 0, 9.99, 49.99
    price_yearly      = Column(Float)    # 0, 99.99, 499.99
    messages_per_day  = Column(Integer)  # 50, 500, -1 (unlimited)
    memory_enabled    = Column(Boolean, default=False)
    custom_personality= Column(Boolean, default=False)
    agents_enabled    = Column(Text)     # JSON list of allowed agents
    stripe_price_id   = Column(String)   # Stripe price ID
    is_active         = Column(Boolean, default=True)

class User(Base):
    __tablename__ = "users"
    
    id               = Column(String, primary_key=True)   # uuid
    email            = Column(String, unique=True)
    hashed_password  = Column(String)
    full_name        = Column(String)
    role             = Column(Enum(UserRole), default=UserRole.USER)
    
    # Plan & Billing
    plan_id          = Column(String, ForeignKey("plans.id"))
    stripe_customer_id = Column(String)
    subscription_id  = Column(String)   # Stripe subscription ID
    subscription_status = Column(String, default="inactive")
    billing_cycle    = Column(String)   # "monthly" / "yearly"
    next_billing_date = Column(DateTime)
    
    # NOVA Personalization
    nova_name        = Column(String, default="NOVA")
    nova_language    = Column(String, default="hinglish")
    nova_personality = Column(Text)     # JSON custom personality
    nova_memory_collection = Column(String)  # unique ChromaDB collection
    
    # Usage Tracking
    messages_today   = Column(Integer, default=0)
    messages_total   = Column(Integer, default=0)
    last_active      = Column(DateTime)
    
    # Account
    is_active        = Column(Boolean, default=True)
    email_verified   = Column(Boolean, default=False)
    created_at       = Column(DateTime, default=datetime.datetime.utcnow)

class UsageLog(Base):
    __tablename__ = "usage_logs"
    
    id           = Column(Integer, primary_key=True, autoincrement=True)
    user_id      = Column(String, ForeignKey("users.id"))
    message      = Column(Text)
    response     = Column(Text)
    agent_used   = Column(String)
    response_time= Column(Float)
    timestamp    = Column(DateTime, default=datetime.datetime.utcnow)

class APIKey(Base):
    __tablename__ = "api_keys"
    
    id         = Column(String, primary_key=True)
    user_id    = Column(String, ForeignKey("users.id"))
    key_hash   = Column(String, unique=True)  # hashed API key
    name       = Column(String)   # "My Mobile App", "VS Code Plugin"
    last_used  = Column(DateTime)
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class SystemError(Base):
    __tablename__ = "system_errors"
    
    id          = Column(Integer, primary_key=True, autoincrement=True)
    error_type  = Column(String)
    message     = Column(Text)
    traceback   = Column(Text)
    endpoint    = Column(String)
    user_id     = Column(String, nullable=True)
    status      = Column(String, default="open")  # open/resolved/ignored
    created_at  = Column(DateTime, default=datetime.datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

class Conversation(Base):
    __tablename__ = "conversations"
    
    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(String, ForeignKey("users.id"))
    title      = Column(String, default="New Conversation")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"
    
    id              = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role            = Column(String)   # user / assistant
    content         = Column(Text)
    agent_used      = Column(String, nullable=True)
    response_time   = Column(Float, nullable=True)
    created_at      = Column(DateTime, default=datetime.datetime.utcnow)

class UploadedFile(Base):
    __tablename__ = "uploaded_files"
    
    id           = Column(String, primary_key=True) # uuid
    user_id      = Column(String, ForeignKey("users.id"))
    filename     = Column(String)
    filepath     = Column(String)
    content_type = Column(String)
    size_mb      = Column(Float)
    chunks       = Column(Integer)
    uploaded_at  = Column(DateTime, default=datetime.datetime.utcnow)
