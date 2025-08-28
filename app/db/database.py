# app/db/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get DATABASE_URL from environment (Supabase PostgreSQL)
DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback to SQLite if no DATABASE_URL provided
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./chatbot.db"
else:
    # Convert postgres:// to postgresql:// for psycopg2 compatibility
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # Add SSL parameters if not present for Supabase
    if "supabase.com" in DATABASE_URL and "sslmode=" not in DATABASE_URL:
        separator = "&" if "?" in DATABASE_URL else "?"
        DATABASE_URL += f"{separator}sslmode=require&connect_timeout=30"

# Create engine with appropriate settings
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    # PostgreSQL/Supabase configuration optimized for Vercel
    connect_args = {
        "sslmode": "require",
        "connect_timeout": 30,
        "application_name": "chatbot_vercel"
    }
    
    engine = create_engine(
        DATABASE_URL, 
        echo=False,
        pool_pre_ping=True,
        pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "280")),
        pool_size=int(os.getenv("DB_POOL_SIZE", "2")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "3")),
        pool_timeout=30,
        connect_args=connect_args
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    """Test database connection with detailed error reporting"""
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT 1 as test")
            row = result.fetchone()
            return True, f"Connection successful - Test result: {row[0]}"
    except Exception as e:
        error_msg = str(e)
        if "Cannot assign requested address" in error_msg:
            return False, f"IPv6 networking issue: {error_msg}"
        elif "timeout" in error_msg.lower():
            return False, f"Connection timeout: {error_msg}"
        else:
            return False, f"Database error: {error_msg}"