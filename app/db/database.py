# app/db/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use SQLite for local/Vercel deployment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chatbot.db")

# Create engine with appropriate settings for SQLite
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """FastAPI dependency that provides a database session for each API request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()