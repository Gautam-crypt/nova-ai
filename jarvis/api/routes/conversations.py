from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jarvis.api.database import get_db
from jarvis.api.models import User, Conversation, Message
from jarvis.api.auth import get_current_user

router = APIRouter()

@router.get("/")
def list_conversations(skip: int = 0, limit: int = 20, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    convos = db.query(Conversation).filter(Conversation.user_id == current_user.id).order_by(Conversation.updated_at.desc()).offset(skip).limit(limit).all()
    return convos

@router.get("/{id}/messages")
def get_messages(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    convo = db.query(Conversation).filter(Conversation.id == id, Conversation.user_id == current_user.id).first()
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    messages = db.query(Message).filter(Message.conversation_id == id).order_by(Message.created_at.asc()).all()
    return messages

@router.patch("/{id}/title")
def rename_conversation(id: int, payload: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    convo = db.query(Conversation).filter(Conversation.id == id, Conversation.user_id == current_user.id).first()
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    new_title = payload.get("title")
    if new_title:
        convo.title = new_title
        db.commit()
        db.refresh(convo)
    return convo

@router.delete("/{id}")
def delete_conversation(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    convo = db.query(Conversation).filter(Conversation.id == id, Conversation.user_id == current_user.id).first()
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    db.query(Message).filter(Message.conversation_id == id).delete()
    db.delete(convo)
    db.commit()
    return {"message": "Conversation deleted"}

@router.patch("/messages/{id}")
def edit_message(id: int, payload: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    msg = db.query(Message).join(Conversation).filter(Message.id == id, Conversation.user_id == current_user.id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
        
    new_content = payload.get("content")
    if new_content:
        msg.content = new_content
        db.commit()
        db.refresh(msg)
    return msg
