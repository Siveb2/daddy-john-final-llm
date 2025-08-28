# AI Persona Chatbot API - Production Ready

A production-ready, persona-based AI chatbot system built with FastAPI, designed for deployment on Vercel with PostgreSQL database integration.

## 🚀 Features

- **Persona-Based Chat**: Customizable AI personalities with system prompting
- **Conversation Management**: Persistent conversation history and summaries
- **Streaming Responses**: Real-time chat responses with Server-Sent Events
- **Database Integration**: PostgreSQL/Supabase support with SQLAlchemy ORM
- **Production Ready**: Health checks, monitoring, and error handling
- **Vercel Deployment**: Optimized for serverless deployment
- **CORS Support**: Cross-origin resource sharing enabled
- **Comprehensive API**: RESTful endpoints for all chatbot operations

## 📋 Prerequisites

- Python 3.12+
- PostgreSQL database (Supabase recommended)
- OpenAI API key
- Vercel account (for deployment)

## 🛠️ Installation & Setup

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd chatbot_ai_server
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   DATABASE_URL=your_postgresql_database_url
   PERSONA_FILE_PATH=persona.txt
   REDIS_URL=your_redis_url_optional
   ```

5. **Run the application**
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Vercel Deployment

1. **Connect to Vercel**
   ```bash
   vercel login
   vercel
   ```

2. **Set environment variables in Vercel dashboard**
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `PERSONA_FILE_PATH`: persona.txt (default)
   - `REDIS_URL`: Optional Redis URL for caching

3. **Deploy**
   ```bash
   vercel --prod
   ```

## 📚 API Endpoints

### Core Chat Endpoints

#### `POST /chat/enhanced`
Send a message to the chatbot.

**Request Body:**
```json
{
  "message": "Hello, how are you?",
  "conversation_id": "user_123"
}
```

**Response:**
```json
{
  "success": true,
  "response": "Ahoy matey! I be doin' well, thank ye for askin'!",
  "conversation_id": "user_123",
  "message_count": 2,
  "summary_created": false,
  "processing_time_ms": 1250.5,
  "conversation_state": {
    "current_phase": "greeting"
  },
  "cache_stats": {
    "hits": 5,
    "misses": 10,
    "hit_rate_percent": 33.33,
    "memory_cache_size": 15
  }
}
```

#### `POST /chat/enhanced/stream`
Streaming chat endpoint for real-time responses.

**Request Body:** Same as `/chat/enhanced`

**Response:** Server-Sent Events stream
```
data: {"content": "Ahoy matey!", "done": false}

data: {"content": " I be doin' well", "done": false}

data: {"content": "", "done": true}
```

### Conversation Management

#### `POST /conversations`
Create a new conversation.

**Request Body:**
```json
{
  "conversation_id": "user_123",
  "user_id": "user_123"
}
```

#### `GET /conversations/{conversation_id}/history`
Get conversation history.

**Response:**
```json
[
  {
    "role": "user",
    "content": "Hello",
    "timestamp": "2024-01-15T10:30:00"
  },
  {
    "role": "assistant", 
    "content": "Ahoy matey!",
    "timestamp": "2024-01-15T10:30:05"
  }
]
```

#### `GET /conversations/{conversation_id}/summaries`
Get conversation summaries.

#### `DELETE /conversations/{conversation_id}`
Delete a conversation.

### System Management

#### `GET /persona`
Get current persona content.

#### `PUT /persona`
Update persona content.

**Request Body:**
```json
{
  "persona_content": "You are a helpful AI assistant."
}
```

#### `GET /health`
Comprehensive health check.

**Response:**
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "overall_status": "healthy",
  "components": {
    "database": {"status": "healthy"},
    "engine": {"status": "healthy", "type": "enhanced"},
    "openai_api": {"status": "configured"}
  },
  "message": "Service is running"
}
```

#### `GET /system/status`
Get detailed system status and metrics.

#### `GET /`
Root endpoint with basic information.

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Yes | - |
| `DATABASE_URL` | PostgreSQL connection string | Yes | SQLite fallback |
| `PERSONA_FILE_PATH` | Path to persona file | No | `persona.txt` |
| `REDIS_URL` | Redis connection string | No | - |

### Database Setup

The application supports both PostgreSQL and SQLite:

- **PostgreSQL (Recommended)**: Set `DATABASE_URL` environment variable
- **SQLite (Development)**: Automatically used if no `DATABASE_URL` is provided

### Persona Configuration

Edit `persona.txt` to customize the AI's personality:

```
You are a pirate chatbot. All responses must be in pirate speak.
```

## 🏗️ Architecture

### Core Components

1. **ChatbotEngine**: Main orchestrator for chat operations
2. **PersonaManager**: Handles persona loading and system prompts
3. **ContextManager**: Manages conversation history and summaries
4. **MessageProcessor**: Processes messages and generates responses
5. **Database Layer**: SQLAlchemy ORM with PostgreSQL support

### Advanced Features

- **Caching**: Memory-based response caching
- **Performance Monitoring**: Request metrics and response times
- **Health Checks**: Comprehensive system health monitoring
- **Error Handling**: Graceful error handling and logging
- **Streaming**: Real-time response streaming

## 🚀 Deployment Checklist

### Before Deployment

- [ ] Set all required environment variables
- [ ] Configure database connection
- [ ] Test API endpoints locally
- [ ] Verify persona configuration
- [ ] Check health endpoint functionality

### Vercel-Specific

- [ ] Ensure `vercel.json` is properly configured
- [ ] Set function timeout to 30 seconds
- [ ] Configure CORS origins if needed
- [ ] Test deployment with `vercel --prod`

### Post-Deployment

- [ ] Verify health endpoint: `https://your-app.vercel.app/health`
- [ ] Test chat functionality
- [ ] Monitor logs for errors
- [ ] Check database connectivity

## 🔍 Troubleshooting

### Common Issues

1. **500 Internal Server Error**
   - Check environment variables
   - Verify database connection
   - Check OpenAI API key validity

2. **Database Connection Issues**
   - Verify `DATABASE_URL` format
   - Check database accessibility
   - Ensure proper SSL configuration

3. **Import Errors**
   - Verify all dependencies in `requirements.txt`
   - Check Python version compatibility
   - Ensure proper file structure

### Debug Mode

Enable debug logging by setting log level to DEBUG in the application.

## 📊 Monitoring

### Health Checks

- **Endpoint**: `GET /health`
- **Frequency**: Every 30 seconds recommended
- **Alerts**: Monitor for non-200 responses

### Metrics

- Response times
- Error rates
- Cache hit rates
- Database connection status

## 🤝 Integration

### Frontend Integration

```javascript
// Example chat integration
const response = await fetch('/chat/enhanced', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: 'Hello',
    conversation_id: 'user_123'
  })
});

const data = await response.json();
console.log(data.response);
```

### Streaming Integration

```javascript
// Example streaming integration
const eventSource = new EventSource('/chat/enhanced/stream');
eventSource.onmessage = function(event) {
  const data = JSON.parse(event.data);
  if (data.done) {
    eventSource.close();
  } else {
    console.log(data.content);
  }
};
```

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Test with the health endpoint
4. Check Vercel deployment logs

---

**Version**: 3.0.0  
**Last Updated**: January 2024