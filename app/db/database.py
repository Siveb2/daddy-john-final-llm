# app/db/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database configuration with SQLite default
DATABASE_URL = os.getenv("DATABASE_URL")

# Force SQLite if no DATABASE_URL is provided or if it's a PostgreSQL URL without psycopg2
if not DATABASE_URL or DATABASE_URL.startswith("postgres://"):
    # Use SQLite for Vercel deployment
    DATABASE_URL = "sqlite:///./chatbot.db"

# Create engine with SQLite-specific settings
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()