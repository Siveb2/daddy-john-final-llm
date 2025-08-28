# app/db/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import urlparse, urlunparse

# Get DATABASE_URL from environment (Supabase PostgreSQL)
DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback to SQLite if no DATABASE_URL provided
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./chatbot.db"
else:
    # Convert postgres:// to postgresql:// for psycopg2 compatibility
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # Add SSL and connection parameters if not present for Supabase
    if "supabase.co" in DATABASE_URL and "sslmode=" not in DATABASE_URL:
        separator = "&" if "?" in DATABASE_URL else "?"
        DATABASE_URL += f"{separator}sslmode=require&connect_timeout=10"

# Create engine with appropriate settings
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    # PostgreSQL/Supabase configuration with psycopg2
    # Enhanced connection settings for better reliability
    connect_args = {}
    
    if "supabase" in DATABASE_URL:
        connect_args = {
            "sslmode": "require",
            "connect_timeout": 15,
            "application_name": "chatbot_app",
            # Force IPv4 to avoid IPv6 issues
            "host": DATABASE_URL.split("@")[1].split(":")[0] if "@" in DATABASE_URL else None
        }
    
    engine = create_engine(
        DATABASE_URL, 
        echo=False,
        pool_pre_ping=True,
        pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "300")),
        pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
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
    """Test database connection"""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True, "Connection successful"
    except Exception as e:
        return False, str(e)