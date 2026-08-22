from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from jarvis.api.models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nova_admin:nova_password@localhost:5432/nova_db")

# check_same_thread is needed only for SQLite
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
