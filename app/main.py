# app/main.py
import os
import uvicorn
import logging
import json
import asyncio
from typing import List, Dict, Optional, Any
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

# --- Core Application Imports ---
try:
    from app.core.advanced_features import ProductionChatbotEngine, ColoredFormatter
    ADVANCED_FEATURES_AVAILABLE = True
except ImportError as e:
    logging.error(f"Import error for advanced features: {e}")
    # Fallback to basic engine
    from app.core.chatbot_core import ChatbotEngine as ProductionChatbotEngine
    ADVANCED_FEATURES_AVAILABLE = False
    
    class ColoredFormatter(logging.Formatter):
        def format(self, record):
            return super().format(record)

from app.db import crud, models, database
from app.db.database import get_db

# --- Logging Setup ---
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# --- Global Engine Instance ---
production_engine: Optional[ProductionChatbotEngine] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup and shutdown events."""
    global production_engine
    logger.info("🚀 Starting Enhanced FastAPI Chatbot Server...")

    try:
        logger.info("Initializing database tables...")
        models.Base.metadata.create_all(bind=database.engine)
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not found - running in demo mode")
            # Don't fail, just log warning
        
        redis_url = os.getenv("REDIS_URL")
        persona_file = os.getenv("PERSONA_FILE_PATH", "persona.txt")
        
        # Initialize with fallback for missing API key
        if api_key:
            production_engine = ProductionChatbotEngine(
                openai_api_key=api_key,
                persona_file_path=persona_file,
                redis_url=redis_url
            )
            logger.info("✅ Enhanced Chatbot Engine initialized successfully")
        else:
            logger.info("⚠️ Running without OpenAI API key - limited functionality")
            
    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        # Don't raise - allow server to start even with initialization issues
    
    yield
    
    logger.info("🔄 Shutting down server...")
    if production_engine and hasattr(production_engine, 'shutdown'):
        try:
            await production_engine.shutdown()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    logger.info("✅ Shutdown complete.")

# --- FastAPI App Initialization ---
app = FastAPI(
    title="AI Persona Chatbot API - Production",
    description="Advanced AI chatbot API with persona replication, conversation management, and production features.",
    version="3.0.0",
    lifespan=lifespan
)

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class ConversationCreateRequest(BaseModel):
    conversation_id: str
    user_id: str

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    conversation_id: str

class PersonaUpdateRequest(BaseModel):
    persona_content: str = Field(..., min_length=10)

# --- Dependency for Engine ---
async def get_engine() -> ProductionChatbotEngine:
    if production_engine is None:
        raise HTTPException(status_code=503, detail="Chatbot engine is not available. Please check OPENAI_API_KEY configuration.")
    return production_engine

# =================================================================
# --- API ENDPOINTS ---
# =================================================================

# --- Core Chat Endpoints ---

@app.post("/chat/enhanced")
async def enhanced_chat(
    request: ChatRequest,
    engine: ProductionChatbotEngine = Depends(get_engine),
    db: Session = Depends(get_db)
):
    try:
        if hasattr(engine, 'chat_enhanced'):
            response = await engine.chat_enhanced(db_session=db, conversation_id=request.conversation_id, user_input=request.message)
        else:
            # Fallback for basic engine
            response = await engine.chat(db=db, conversation_id=request.conversation_id, user_input=request.message)
        return response
    except Exception as e:
        logger.error(f"Chat endpoint error for conversation {request.conversation_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/enhanced/stream")
async def enhanced_chat_stream(
    request: ChatRequest,
    engine: ProductionChatbotEngine = Depends(get_engine),
    db: Session = Depends(get_db)
):
    """Streaming chat endpoint."""
    async def generate_stream():
        try:
            if hasattr(engine, 'chat_enhanced'):
                result = await engine.chat_enhanced(db_session=db, conversation_id=request.conversation_id, user_input=request.message)
            else:
                result = await engine.chat(db=db, conversation_id=request.conversation_id, user_input=request.message)
                
            if result.get('success') and result.get('response'):
                response_text = result['response']
                # Stream the response in chunks
                for i in range(0, len(response_text), 50):
                    chunk = response_text[i:i+50]
                    yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"
                    await asyncio.sleep(0.05)
                # Send completion signal
                yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"
            else:
                yield f"data: {json.dumps({'error': result.get('error'), 'done': True})}\n\n"
        except Exception as e:
            logger.error(f"Stream error: {e}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"

    return StreamingResponse(generate_stream(), media_type="text/event-stream")

# --- Conversation Management Endpoints ---

@app.post("/conversations", status_code=201)
def create_conversation(
    request: ConversationCreateRequest,
    db: Session = Depends(get_db)
):
    try:
        crud.get_or_create_conversation(db=db, conversation_id=request.conversation_id, user_id=request.user_id)
        return {"status": "success", "conversation_id": request.conversation_id}
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations/{conversation_id}/history")
def get_history(conversation_id: str, db: Session = Depends(get_db)):
    try:
        messages = crud.get_conversation_messages(db=db, conversation_id=conversation_id)
        return [{"role": msg.role, "content": msg.content, "timestamp": msg.created_at} for msg in messages]
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations/{conversation_id}/summaries")
def get_summaries(conversation_id: str, db: Session = Depends(get_db)):
    try:
        summary = crud.get_latest_summary(db=db, conversation_id=conversation_id)
        if summary:
            return [{"summary_text": summary.summary_text, "created_at": summary.created_at}]
        return []
    except Exception as e:
        logger.error(f"Error getting summaries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    try:
        conversation = crud.get_conversation(db, conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        crud.delete_conversation(db, conversation_id)
        return {"status": "success", "message": "Conversation deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Persona & System Management Endpoints ---

@app.get("/persona")
async def get_persona():
    try:
        if production_engine and hasattr(production_engine, 'persona_manager'):
            return {"persona_content": production_engine.persona_manager.persona_content}
        else:
            # Fallback response
            return {"persona_content": "You are a helpful AI assistant."}
    except Exception as e:
        logger.error(f"Error getting persona: {e}")
        return {"persona_content": "You are a helpful AI assistant."}

@app.put("/persona")
async def update_persona(request: PersonaUpdateRequest):
    try:
        if production_engine and hasattr(production_engine, 'persona_manager'):
            production_engine.persona_manager.update_persona(request.persona_content)
            return {"status": "success", "message": "Persona updated"}
        else:
            return {"status": "warning", "message": "Persona update not available - engine not initialized"}
    except Exception as e:
        logger.error(f"Error updating persona: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    try:
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "components": {},
            "message": "Service is running"
        }
        
        # Check database
        try:
            with database.SessionLocal() as db:
                db.execute("SELECT 1")
            health_status["components"]["database"] = {"status": "healthy"}
        except Exception as e:
            health_status["components"]["database"] = {"status": "error", "error": str(e)}
            health_status["overall_status"] = "degraded"
        
        # Check engine
        if production_engine:
            if hasattr(production_engine, 'health_checker'):
                try:
                    with database.SessionLocal() as db:
                        engine_health = await production_engine.health_checker.run_comprehensive_health_check(db)
                    health_status["components"]["engine"] = engine_health["components"]
                except Exception as e:
                    health_status["components"]["engine"] = {"status": "error", "error": str(e)}
            else:
                health_status["components"]["engine"] = {"status": "healthy", "type": "basic"}
        else:
            health_status["components"]["engine"] = {"status": "not_initialized"}
            health_status["overall_status"] = "degraded"
        
        # Check API key
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            health_status["components"]["openai_api"] = {"status": "configured"}
        else:
            health_status["components"]["openai_api"] = {"status": "not_configured"}
            health_status["overall_status"] = "degraded"
        
        status_code = 200 if health_status["overall_status"] == "healthy" else 503
        return JSONResponse(content=health_status, status_code=status_code)
        
    except Exception as e:
        logger.error(f"Health check error: {e}", exc_info=True)
        return JSONResponse(content={
            "timestamp": datetime.now().isoformat(),
            "overall_status": "error",
            "error": str(e),
            "message": "Health check failed"
        }, status_code=503)

@app.get("/system/status")
async def get_system_status():
    try:
        status = {
            "timestamp": datetime.now().isoformat(),
            "status": "running",
            "features": {
                "advanced_features": ADVANCED_FEATURES_AVAILABLE,
                "engine_initialized": production_engine is not None,
                "api_key_configured": bool(os.getenv("OPENAI_API_KEY"))
            }
        }
        
        if production_engine and hasattr(production_engine, 'get_comprehensive_status'):
            comprehensive_status = await production_engine.get_comprehensive_status()
            status.update(comprehensive_status)
        
        return status
    except Exception as e:
        logger.error(f"System status error: {e}")
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": str(e),
            "message": "System status check failed"
        }

# --- Root endpoint for basic connectivity test ---
@app.get("/")
async def root():
    return {
        "message": "AI Persona Chatbot API is running",
        "version": "3.0.0",
        "status": "healthy",
        "endpoints": {
            "health": "/health",
            "chat": "/chat/enhanced",
            "docs": "/docs"
        }
    }

# --- Main Entry Point ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)