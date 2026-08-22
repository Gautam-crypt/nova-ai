from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
from datetime import date
from sqlalchemy.orm import Session

from jarvis.api.database import SessionLocal
from jarvis.api.models import UsageLog, Plan, User
from jarvis.api.auth import ALGORITHM, SECRET_KEY
from jarvis.core.error_tracker import ErrorTracker
from jose import jwt, JWTError

def get_user_from_token(request: Request, db: Session):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            if user_id:
                return db.query(User).filter(User.id == user_id).first()
        except JWTError:
            pass
    return None

class UsageMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if "/nova/chat" in str(request.url):
            db = SessionLocal()
            try:
                user = get_user_from_token(request, db)
                if user:
                    today = date.today().isoformat()
                    # Count today's messages for this user
                    count = db.query(UsageLog).filter(
                        UsageLog.user_id == user.id,
                        UsageLog.timestamp >= f"{today} 00:00:00"
                    ).count()
                    
                    plan = db.query(Plan).filter(Plan.id == user.plan_id).first()
                    limit = plan.messages_per_day if plan else 50
                    
                    if limit != -1 and count >= limit:
                        return JSONResponse(
                            status_code=429,
                            content={"error": "Daily limit reached"}
                        )
            finally:
                db.close()
                
        return await call_next(request)

class ErrorTrackingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            db = SessionLocal()
            try:
                user = get_user_from_token(request, db)
                user_id = user.id if user else ""
                tracker = ErrorTracker(db)
                tracker.log(e, endpoint=str(request.url), user_id=user_id)
            finally:
                db.close()
            raise
