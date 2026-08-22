from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from jarvis.api.database import get_db
from jarvis.api.models import User, SystemError, Plan, UsageLog
from jarvis.api.auth import require_admin
import os
from pathlib import Path

router = APIRouter()

@router.get("/stats")
def get_stats(current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    active_today = db.query(UsageLog).filter(UsageLog.timestamp >= f"{date.today()} 00:00:00").distinct(UsageLog.user_id).count()
    total_messages = db.query(UsageLog).count()
    messages_today = db.query(UsageLog).filter(UsageLog.timestamp >= f"{date.today()} 00:00:00").count()
    errors_open = db.query(SystemError).filter(SystemError.status == "open").count()
    
    return {
        "total_users":          total_users,
        "active_today":         active_today,
        "total_messages":       total_messages,
        "messages_today":       messages_today,
        "knowledge_db_entries": 0, 
        "api_calls_saved":      0, 
        "top_agents_used":      {}, 
        "avg_response_time":    "0.0s", 
        "errors_open":          errors_open,
        "system": {
            "cpu_percent":      0.0,
            "memory_percent":   0.0,
            "disk_percent":     0.0,
            "ollama_status":    "unknown"
        }
    }

@router.get("/errors")
def get_errors(status: str = "open", limit: int = 50, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    errors = db.query(SystemError).filter(SystemError.status == status).order_by(SystemError.created_at.desc()).limit(limit).all()
    return {"errors": errors, "total": len(errors)}

@router.patch("/errors/{error_id}")
def update_error(error_id: int, payload: dict, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    sys_err = db.query(SystemError).filter(SystemError.id == error_id).first()
    if not sys_err:
        raise HTTPException(status_code=404, detail="Error not found")
        
    new_status = payload.get("status", "resolved")
    sys_err.status = new_status
    if new_status == "resolved":
        from datetime import datetime
        sys_err.resolved_at = datetime.utcnow()
    db.commit()
    return {"message": f"Error {error_id} marked as {new_status}"}

@router.get("/system/logs")
def get_system_logs(current_user: User = Depends(require_admin)):
    log_path = Path("debug.log")
    if not log_path.exists():
        return {"logs": []}
        
    with open(log_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return {"logs": lines[-100:]}

@router.get("/review-pipeline")
def get_review_pipeline(current_user: User = Depends(require_admin)):
    return []
