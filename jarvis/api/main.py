from fastapi import FastAPI
from fastapi.security import HTTPBearer, APIKeyHeader

from jarvis.api.routes import auth, users, nova, files, openai_compat, pipeline, conversations, admin
from jarvis.api.middleware import ErrorTrackingMiddleware, UsageMiddleware
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="NOVA AI — API",
    description="""
## NOVA AI Personal Assistant API

Apni personalized AI assistant banao.

### Features:
- 🤖 **Personalized NOVA** — har user ki apni AI
- 🧠 **Memory** — conversations yaad rakhti hai
- 🔍 **Agents** — HERMES, VISHWAKARMA, DIVYA, YAMA, MANAS
- 💳 **Subscriptions** — Free, Pro, Enterprise plans

### Authentication:
- **JWT Bearer Token** — login ke baad milta hai
- **API Key** — developers ke liye (X-API-Key header)

### Quick Start:
1. `POST /auth/register` → account banao
2. `POST /auth/login` → token lo
3. `POST /nova/chat` → NOVA se baat karo
    """,
    version="1.0.0",
    contact={
        "name": "Gautam — NOVA Creator",
        "email": "your@email.com"
    },
    license_info={
        "name": "Powered by Gautam Tiwari"
    }
)

app.add_middleware(UsageMiddleware)
app.add_middleware(ErrorTrackingMiddleware)

tags_metadata = [
    {"name": "🔐 Authentication",    "description": "Login, tokens, password"},
    {"name": "👤 Users",             "description": "Profile, settings, API keys"},
    {"name": "🤖 NOVA Chat",         "description": "Chat, streaming, pipeline"},
    {"name": "📁 Files",             "description": "Upload files, chat with docs"},
    {"name": "🧠 Knowledge Base",    "description": "RAG store, search, review"},
    {"name": "💬 Conversations",     "description": "History, CRUD"},
    {"name": "🔌 OpenAI Compatible", "description": "/v1/chat/completions"},
    {"name": "👑 Admin",             "description": "Stats, users, logs, errors"},
]

app.include_router(auth.router,          prefix="/auth",          tags=["🔐 Authentication"])
app.include_router(users.router,         prefix="/users",         tags=["👤 Users"])
app.include_router(nova.router,          prefix="/nova",          tags=["🤖 NOVA Chat"])
app.include_router(files.router,         prefix="/files",         tags=["📁 Files"])
app.include_router(conversations.router, prefix="/conversations", tags=["💬 Conversations"])
app.include_router(openai_compat.router, prefix="",               tags=["🔌 OpenAI Compatible"])
app.include_router(pipeline.router,      prefix="",               tags=["🤖 NOVA Chat"])
app.include_router(admin.router,         prefix="/admin",         tags=["👑 Admin"])

security_bearer = HTTPBearer()
security_apikey = APIKeyHeader(name="X-API-Key")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
