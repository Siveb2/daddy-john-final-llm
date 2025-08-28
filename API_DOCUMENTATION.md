# AI Persona Chatbot API Documentation

## Base URL
```
https://your-app.vercel.app
```

## Authentication
Currently, the API doesn't require authentication. However, you should implement user authentication on your frontend and pass user IDs in the requests.

## API Endpoints

### 1. Health Check
**GET** `/health`

Check if the service is running and healthy.

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

### 2. Root Endpoint
**GET** `/`

Basic information about the API.

**Response:**
```json
{
  "message": "AI Persona Chatbot API is running",
  "version": "3.0.0",
  "status": "healthy",
  "endpoints": {
    "health": "/health",
    "chat": "/chat/enhanced",
    "docs": "/docs"
  }
}
```

### 3. Chat Endpoint
**POST** `/chat/enhanced`

Send a message to the chatbot and get a response.

**Request Body:**
```json
{
  "message": "Hello, how are you?",
  "conversation_id": "user_123_conversation_1"
}
```

**Response:**
```json
{
  "success": true,
  "response": "Ahoy matey! I be doin' well, thank ye for askin'!",
  "conversation_id": "user_123_conversation_1",
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

### 4. Streaming Chat Endpoint
**POST** `/chat/enhanced/stream`

Get real-time streaming responses using Server-Sent Events.

**Request Body:** Same as `/chat/enhanced`

**Response:** Server-Sent Events stream
```
data: {"content": "Ahoy matey!", "done": false}

data: {"content": " I be doin' well", "done": false}

data: {"content": "", "done": true}
```

### 5. Create Conversation
**POST** `/conversations`

Create a new conversation.

**Request Body:**
```json
{
  "conversation_id": "user_123_conversation_1",
  "user_id": "user_123"
}
```

**Response:**
```json
{
  "status": "success",
  "conversation_id": "user_123_conversation_1"
}
```

### 6. Get Conversation History
**GET** `/conversations/{conversation_id}/history`

Get all messages in a conversation.

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

### 7. Get Conversation Summaries
**GET** `/conversations/{conversation_id}/summaries`

Get conversation summaries (created every 20 messages).

**Response:**
```json
[
  {
    "summary_text": "User greeted the bot and asked about its well-being. The bot responded in pirate speak.",
    "created_at": "2024-01-15T10:35:00"
  }
]
```

### 8. Delete Conversation
**DELETE** `/conversations/{conversation_id}`

Delete a conversation and all its messages.

**Response:**
```json
{
  "status": "success",
  "message": "Conversation deleted"
}
```

### 9. Get Persona
**GET** `/persona`

Get the current AI persona configuration.

**Response:**
```json
{
  "persona_content": "You are a pirate chatbot. All responses must be in pirate speak."
}
```

### 10. Update Persona
**PUT** `/persona`

Update the AI persona.

**Request Body:**
```json
{
  "persona_content": "You are a helpful AI assistant."
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Persona updated"
}
```

### 11. System Status
**GET** `/system/status`

Get detailed system status and metrics.

**Response:**
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "status": "running",
  "features": {
    "advanced_features": true,
    "engine_initialized": true,
    "api_key_configured": true
  },
  "health": {
    "overall_status": "healthy",
    "components": {
      "llm_provider": {"status": "healthy"}
    }
  },
  "system_metrics": {
    "performance": {
      "uptime_seconds": 3600,
      "total_requests": 150,
      "avg_response_time_ms": 1200
    },
    "cache": {
      "hits": 50,
      "misses": 100,
      "hit_rate_percent": 33.33
    },
    "conversations": {
      "active_count": 10,
      "total_messages": 500
    }
  }
}
```

## Error Responses

All endpoints return standard HTTP status codes:

- **200**: Success
- **201**: Created (for conversation creation)
- **400**: Bad Request (invalid input)
- **404**: Not Found (conversation not found)
- **500**: Internal Server Error
- **503**: Service Unavailable (engine not available)

**Error Response Format:**
```json
{
  "detail": "Error message description"
}
```

## Integration Examples

### JavaScript/TypeScript

#### Basic Chat Integration
```javascript
async function sendMessage(message, conversationId) {
  try {
    const response = await fetch('https://your-app.vercel.app/chat/enhanced', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message,
        conversation_id: conversationId
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data.response;
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
}

// Usage
sendMessage('Hello!', 'user_123_conversation_1')
  .then(response => console.log('Bot response:', response))
  .catch(error => console.error('Error:', error));
```

#### Streaming Chat Integration
```javascript
function streamChat(message, conversationId, onChunk, onComplete, onError) {
  const eventSource = new EventSource(`https://your-app.vercel.app/chat/enhanced/stream`);
  
  eventSource.onmessage = function(event) {
    try {
      const data = JSON.parse(event.data);
      
      if (data.done) {
        eventSource.close();
        onComplete();
      } else if (data.error) {
        eventSource.close();
        onError(data.error);
      } else {
        onChunk(data.content);
      }
    } catch (error) {
      eventSource.close();
      onError(error);
    }
  };

  eventSource.onerror = function(error) {
    eventSource.close();
    onError(error);
  };

  // Send the message
  fetch('https://your-app.vercel.app/chat/enhanced/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: message,
      conversation_id: conversationId
    })
  });
}

// Usage
let fullResponse = '';
streamChat(
  'Tell me a story',
  'user_123_conversation_1',
  (chunk) => {
    fullResponse += chunk;
    console.log('Received chunk:', chunk);
  },
  () => {
    console.log('Complete response:', fullResponse);
  },
  (error) => {
    console.error('Stream error:', error);
  }
);
```

#### Conversation Management
```javascript
// Create a new conversation
async function createConversation(conversationId, userId) {
  const response = await fetch('https://your-app.vercel.app/conversations', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      conversation_id: conversationId,
      user_id: userId
    })
  });
  
  return response.json();
}

// Get conversation history
async function getConversationHistory(conversationId) {
  const response = await fetch(`https://your-app.vercel.app/conversations/${conversationId}/history`);
  return response.json();
}

// Delete conversation
async function deleteConversation(conversationId) {
  const response = await fetch(`https://your-app.vercel.app/conversations/${conversationId}`, {
    method: 'DELETE'
  });
  return response.json();
}
```

### Python

#### Basic Chat Integration
```python
import requests
import json

def send_message(message, conversation_id, base_url="https://your-app.vercel.app"):
    url = f"{base_url}/chat/enhanced"
    payload = {
        "message": message,
        "conversation_id": conversation_id
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data['response']
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")
        raise

# Usage
try:
    response = send_message("Hello!", "user_123_conversation_1")
    print(f"Bot response: {response}")
except Exception as e:
    print(f"Error: {e}")
```

#### Conversation Management
```python
import requests

def create_conversation(conversation_id, user_id, base_url="https://your-app.vercel.app"):
    url = f"{base_url}/conversations"
    payload = {
        "conversation_id": conversation_id,
        "user_id": user_id
    }
    
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()

def get_conversation_history(conversation_id, base_url="https://your-app.vercel.app"):
    url = f"{base_url}/conversations/{conversation_id}/history"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def delete_conversation(conversation_id, base_url="https://your-app.vercel.app"):
    url = f"{base_url}/conversations/{conversation_id}"
    response = requests.delete(url)
    response.raise_for_status()
    return response.json()
```

## Best Practices

### 1. Conversation ID Management
- Use unique conversation IDs for each chat session
- Include user ID in conversation ID for better organization
- Example: `user_123_conversation_1`, `user_123_conversation_2`

### 2. Error Handling
- Always check response status codes
- Implement retry logic for network errors
- Handle rate limiting gracefully

### 3. Performance
- Use streaming for real-time chat experiences
- Implement client-side caching for conversation history
- Monitor response times and error rates

### 4. Security
- Validate user input before sending to API
- Implement proper user authentication
- Sanitize conversation IDs and user IDs

### 5. Monitoring
- Use the `/health` endpoint for uptime monitoring
- Monitor `/system/status` for performance metrics
- Set up alerts for error rates and response times

## Rate Limits

Currently, there are no explicit rate limits, but consider:
- OpenAI API rate limits (depends on your plan)
- Vercel function execution limits
- Database connection limits

## Support

For issues or questions:
1. Check the `/health` endpoint first
2. Review the `/system/status` endpoint for detailed metrics
3. Check Vercel deployment logs
4. Ensure all environment variables are properly set

---

**API Version**: 3.0.0  
**Last Updated**: January 2024
