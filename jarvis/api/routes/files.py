import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from jarvis.api.auth import get_current_user
from jarvis.api.models import User, UploadedFile
from jarvis.api.database import get_db
from sqlalchemy.orm import Session
from jarvis.api.nova_factory import chroma_client

router = APIRouter()

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_TYPES = {
    "application/pdf":  "pdf",
    "text/plain":       "txt",
    "text/markdown":    "md",
    "application/json": "json",
    "text/csv":         "csv"
}

MAX_SIZE_MB = 10

def extract_text(filepath: Path, content_type: str) -> str:
    if content_type == "application/pdf":
        import pypdf
        reader = pypdf.PdfReader(str(filepath))
        return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    else:
        return filepath.read_text(encoding="utf-8", errors="ignore")

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    words  = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload file → extract text → store in user's RAG collection"""
    
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_SIZE_MB:
        raise HTTPException(400, f"File too large: {size_mb:.1f}MB > {MAX_SIZE_MB}MB")
    
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"File type not allowed: {file.content_type}")
    
    file_id  = str(uuid.uuid4())
    ext      = ALLOWED_TYPES[file.content_type]
    filepath = UPLOAD_DIR / f"{file_id}.{ext}"
    
    with open(filepath, "wb") as f:
        f.write(contents)
    
    text = extract_text(filepath, file.content_type)
    
    user_collection = chroma_client.get_or_create_collection(
        name=f"nova_{current_user.id}_files"
    )
    
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    for i, chunk in enumerate(chunks):
        user_collection.add(
            ids=[f"{file_id}_chunk_{i}"],
            documents=[chunk],
            metadatas=[{
                "file_id":   file_id,
                "filename":  file.filename,
                "chunk":     i,
                "user_id":   str(current_user.id)
            }]
        )
    
    uploaded_file_record = UploadedFile(
        id=file_id,
        user_id=current_user.id,
        filename=file.filename,
        filepath=str(filepath),
        content_type=file.content_type,
        size_mb=size_mb,
        chunks=len(chunks)
    )
    db.add(uploaded_file_record)
    db.commit()
    
    return {
        "file_id":  file_id,
        "filename": file.filename,
        "chunks":   len(chunks),
        "size_mb":  round(size_mb, 2),
        "message":  f"File stored — {len(chunks)} chunks indexed in NOVA's memory"
    }

@router.post("/chat/with-file")
async def chat_with_file(payload: dict, current_user: User = Depends(get_current_user)):
    message  = payload.get("message", "")
    file_ids = payload.get("file_ids", [])
    
    user_collection = chroma_client.get_or_create_collection(
        name=f"nova_{current_user.id}_files"
    )
    
    where_filter = {"file_id": {"$in": file_ids}} if file_ids else None
    
    results = user_collection.query(
        query_texts=[message],
        n_results=3,
        where=where_filter
    )
    
    file_context = ""
    if results["documents"] and len(results["documents"]) > 0 and len(results["documents"][0]) > 0:
        file_context = "\n\n".join(results["documents"][0])
    
    # Fake response for now, should call real orchestrator or ollama
    reply = f"Context used: {bool(file_context)}. Mock answer based on files."
    
    return {"reply": reply, "file_context_used": bool(file_context)}
