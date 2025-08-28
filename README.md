# AI Persona Chatbot Server

Production-ready LLM chatbot server with persona-based responses, conversation management, and database persistence.

## Features

- **Persona-based AI responses** using OpenRouter API
- **Conversation management** with full history tracking
- **Automatic summarization** for long conversations
- **Database persistence** using SQLite
- **Redis caching support** (optional)
- **Health monitoring** and performance metrics
- **RESTful API** with FastAPI
- **Vercel deployment ready**

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd chatbot_ai_server
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory:
```env
# Required
OPENAI_API_KEY=your_openrouter_api_key_here

# Optional
DATABASE_URL=sqlite:///./chatbot.db
REDIS_URL=redis://localhost:6379
PERSONA_FILE_PATH=persona.txt
```

### 4. Set Your Persona
Edit `persona.txt` to define your chatbot's personality.

### 5. Run Locally
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Deployment on Vercel

1. Push code to GitHub
2. Connect GitHub repo to Vercel
3. Set environment variables in Vercel dashboard
4. Deploy

## API Endpoints

### Core Chat Endpoints

#### 1. **POST /chat/enhanced**
Send a message and get AI response.
```json
Request:
{
  "message": "Hello, how are you?",
  "conversation_id": "conv_123"
}

Response:
{
  "success": true,
  "response": "Ahoy there! I be doing fine as a fiddle...",
  "conversation_id": "conv_123",
  "message_count": 2,
  "summary_created": false,
  "processing_time_ms": 1250.5,
  "conversation_state": {
    "current_phase": "greeting"
  },
  "cache_stats": {
    "hits": 0,
    "misses": 1,
    "hit_rate_percent": 0.0
  }
}
```

#### 2. **POST /chat/enhanced/stream**
Stream chat response (Server-Sent Events).
```json
Request:
{
  "message": "Tell me a story",
  "conversation_id": "conv_123"
}

Response: (SSE stream)
data: {"content": "Once upon"}
data: {"content": " a time..."}
```

### Conversation Management

#### 3. **POST /conversations**
Create a new conversation.
```json
Request:
{
  "conversation_id": "conv_123",
  "user_id": "user_456"
}

Response:
{
  "status": "success",
  "conversation_id": "conv_123"
}
```

#### 4. **GET /conversations/{conversation_id}/history**
Get full conversation history.
```json
Response:
[
  {
    "role": "user",
    "content": "Hello",
    "timestamp": "2024-01-01T12:00:00"
  },
  {
    "role": "assistant",
    "content": "Ahoy there!",
    "timestamp": "2024-01-01T12:00:01"
  }
]
```

#### 5. **GET /conversations/{conversation_id}/summaries**
Get conversation summaries.
```json
Response:
[
  {
    "summary_text": "User greeted the bot and asked about...",
    "created_at": "2024-01-01T12:30:00"
  }
]
```

#### 6. **DELETE /conversations/{conversation_id}**
Delete a conversation and all its data.
```json
Response:
{
  "status": "success",
  "message": "Conversation deleted"
}
```

### Persona Management

#### 7. **GET /persona**
Get current persona content.
```json
Response:
{
  "persona_content": "You are a pirate chatbot..."
}
```

#### 8. **PUT /persona**
Update persona.
```json
Request:
{
  "persona_content": "You are a helpful assistant..."
}

Response:
{
  "status": "success",
  "message": "Persona updated"
}
```

### System Monitoring

#### 9. **GET /health**
Health check endpoint.
```json
Response:
{
  "timestamp": "2024-01-01T12:00:00",
  "overall_status": "healthy",
  "components": {
    "llm_provider": {"status": "healthy"}
  },
  "metrics": {
    "performance": {
      "uptime_seconds": 3600,
      "total_requests": 150,
      "avg_response_time_ms": 1200
    }
  }
}
```

#### 10. **GET /system/status**
Get comprehensive system status.
```json
Response:
{
  "timestamp": "2024-01-01T12:00:00",
  "health": {...},
  "system_metrics": {
    "conversations": {
      "active_count": 10,
      "total_messages": 500
    }
  }
}
```

## Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `OPENAI_API_KEY` | Yes | OpenRouter API key | - |
| `DATABASE_URL` | No | Database connection string | `sqlite:///./chatbot.db` |
| `REDIS_URL` | No | Redis connection URL | - |
| `PERSONA_FILE_PATH` | No | Path to persona file | `persona.txt` |

## Technical Stack

- **Framework**: FastAPI
- **Database**: SQLite (PostgreSQL compatible)
- **Cache**: Redis (optional)
- **AI Provider**: OpenRouter (OpenAI compatible)
- **Deployment**: Vercel

## Notes for Your Friend

1. **All endpoints are CORS-enabled** - can be called from any frontend
2. **conversation_id** should be unique per conversation (use UUID or similar)
3. **user_id** should be provided by your authentication system
4. **Automatic summarization** happens every 20 messages
5. **Database is auto-created** on first run
6. **Health endpoint** can be used for monitoring
7. **Streaming endpoint** uses Server-Sent Events for real-time responses

## Support

For issues or questions about integration, check the health endpoint first to ensure the service is running properly.