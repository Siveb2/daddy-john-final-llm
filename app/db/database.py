# app/db/database.py
import os
import socket
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

def resolve_hostname_to_ipv4(hostname):
    """Resolve hostname to IPv4 address to avoid IPv6 issues"""
    try:
        # Force IPv4 resolution
        result = socket.getaddrinfo(hostname, None, socket.AF_INET)
        if result:
            return result[0][4][0]  # Return first IPv4 address
    except Exception:
        pass
    return hostname

def create_ipv4_database_url(original_url):
    """Convert database URL to use IPv4 address instead of hostname"""
    if not original_url or "supabase.co" not in original_url:
        return original_url
    
    try:
        parsed = urlparse(original_url)
        hostname = parsed.hostname
        
        if hostname and "supabase.co" in hostname:
            ipv4_address = resolve_hostname_to_ipv4(hostname)
            if ipv4_address != hostname:
                # Replace hostname with IPv4 address
                netloc = parsed.netloc.replace(hostname, ipv4_address)
                new_parsed = parsed._replace(netloc=netloc)
                return urlunparse(new_parsed)
    except Exception as e:
        print(f"Warning: Could not resolve IPv4 for {original_url}: {e}")
    
    return original_url

# Create IPv4-optimized DATABASE_URL
if DATABASE_URL and not DATABASE_URL.startswith("sqlite"):
    DATABASE_URL = create_ipv4_database_url(DATABASE_URL)

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
    connect_args = {
        "sslmode": "require",
        "connect_timeout": 20,
        "application_name": "chatbot_app"
    }
    
    engine = create_engine(
        DATABASE_URL, 
        echo=False,
        pool_pre_ping=True,
        pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "300")),
        pool_size=int(os.getenv("DB_POOL_SIZE", "3")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "5")),
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
            result = conn.execute("SELECT 1")
            return True, "Connection successful"
    except Exception as e:
        return False, str(e)