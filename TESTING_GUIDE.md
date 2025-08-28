# API Testing Guide for Postman

Base URL: `https://daddy-john-final-llm.vercel.app`

## Prerequisites
1. Set your `OPENAI_API_KEY` in Vercel environment variables
2. Import this collection into Postman
3. Test endpoints in the order listed below

---

## 1. Health Check Endpoint

**GET** `/health`

```
URL: https://daddy-john-final-llm.vercel.app/health
Method: GET
Headers: None required
Body: None
```

**Expected Response:**
```json
{
  "timestamp": "2024-01-01T12:00:00",
  "overall_status": "healthy",
  "components": {
    "llm_provider": {"status": "healthy"}
  },
  "message": "Basic health check passed"
}
```

---

## 2. System Status Endpoint

**GET** `/system/status`

```
URL: https://daddy-john-final-llm.vercel.app/system/status
Method: GET
Headers: None required
Body: None
```

**Expected Response:**
```json
{
  "timestamp": "2024-01-01T12:00:00",
  "status": "basic_engine_active",
  "message": "System is running with basic features"
}
```

---

## 3. Get Persona

**GET** `/persona`

```
URL: https://daddy-john-final-llm.vercel.app/persona
Method: GET
Headers: None required
Body: None
```

**Expected Response:**
```json
{
  "persona_content": "You are a pirate chatbot. All responses must be in pirate speak."
}
```

---

## 4. Update Persona

**PUT** `/persona`

```
URL: https://daddy-john-final-llm.vercel.app/persona
Method: PUT
Headers: 
  Content-Type: application/json
Body (JSON):
{
  "persona_content": "You are a helpful AI assistant that speaks like a friendly robot."
}
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Persona updated"
}
```

---

## 5. Create Conversation

**POST** `/conversations`

```
URL: https://daddy-john-final-llm.vercel.app/conversations
Method: POST
Headers: 
  Content-Type: application/json
Body (JSON):
{
  "conversation_id": "test_conv_123",
  "user_id": "test_user_456"
}
```

**Expected Response:**
```json
{
  "status": "success",
  "conversation_id": "test_conv_123"
}
```

---

## 6. Send Chat Message

**POST** `/chat/enhanced`

```
URL: https://daddy-john-final-llm.vercel.app/chat/enhanced
Method: POST
Headers: 
  Content-Type: application/json
Body (JSON):
{
  "message": "Hello! How are you today?",
  "conversation_id": "test_conv_123"
}
```

**Expected Response:**
```json
{
  "success": true,
  "response": "Hello there! I'm doing well, thank you for asking...",
  "conversation_id": "test_conv_123",
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

---

## 7. Stream Chat Response

**POST** `/chat/enhanced/stream`

```
URL: https://daddy-john-final-llm.vercel.app/chat/enhanced/stream
Method: POST
Headers: 
  Content-Type: application/json
Body (JSON):
{
  "message": "Tell me a short story",
  "conversation_id": "test_conv_123"
}
```

**Expected Response:** (Server-Sent Events)
```
data: {"content": "Once upon"}
data: {"content": " a time..."}
data: {"content": " there was"}
...
```

---

## 8. Get Conversation History

**GET** `/conversations/{conversation_id}/history`

```
URL: https://daddy-john-final-llm.vercel.app/conversations/test_conv_123/history
Method: GET
Headers: None required
Body: None
```

**Expected Response:**
```json
[
  {
    "role": "user",
    "content": "Hello! How are you today?",
    "timestamp": "2024-01-01T12:00:00"
  },
  {
    "role": "assistant",
    "content": "Hello there! I'm doing well...",
    "timestamp": "2024-01-01T12:00:01"
  }
]
```

---

## 9. Get Conversation Summaries

**GET** `/conversations/{conversation_id}/summaries`

```
URL: https://daddy-john-final-llm.vercel.app/conversations/test_conv_123/summaries
Method: GET
Headers: None required
Body: None
```

**Expected Response:**
```json
[
  {
    "summary_text": "User greeted the assistant and asked about well-being...",
    "created_at": "2024-01-01T12:30:00"
  }
]
```

---

## 10. Delete Conversation

**DELETE** `/conversations/{conversation_id}`

```
URL: https://daddy-john-final-llm.vercel.app/conversations/test_conv_123
Method: DELETE
Headers: None required
Body: None
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Conversation deleted"
}
```

---

## Testing Sequence

### Step 1: Basic Health Checks
1. Test `/health` endpoint
2. Test `/system/status` endpoint
3. Test `/persona` endpoint (GET)

### Step 2: Persona Management
1. Test `/persona` endpoint (PUT) to update persona
2. Test `/persona` endpoint (GET) again to verify update

### Step 3: Conversation Flow
1. Test `/conversations` endpoint (POST) to create conversation
2. Test `/chat/enhanced` endpoint multiple times with different messages
3. Test `/conversations/{id}/history` to verify message storage
4. Test `/chat/enhanced/stream` for streaming response

### Step 4: Data Retrieval
1. Test `/conversations/{id}/summaries` endpoint
2. Test conversation history again

### Step 5: Cleanup
1. Test `/conversations/{id}` endpoint (DELETE)
2. Verify conversation is deleted by trying to get history

---

## Sample Test Messages

Use these messages to test different conversation phases:

**Greeting Phase:**
```json
{"message": "Hello there!", "conversation_id": "test_conv_123"}
```

**Information Gathering:**
```json
{"message": "What can you help me with?", "conversation_id": "test_conv_123"}
```

**Problem Solving:**
```json
{"message": "I need help with a coding problem", "conversation_id": "test_conv_123"}
```

**Casual Chat:**
```json
{"message": "What's your favorite color?", "conversation_id": "test_conv_123"}
```

---

## Error Testing

Test these scenarios to ensure proper error handling:

**Invalid Conversation ID:**
```json
{"message": "Test message", "conversation_id": "nonexistent_conv"}
```

**Empty Message:**
```json
{"message": "", "conversation_id": "test_conv_123"}
```

**Missing Required Fields:**
```json
{"message": "Test without conversation_id"}
```

---

## Expected Status Codes

- **200**: Successful GET requests
- **201**: Successful conversation creation
- **404**: Conversation not found
- **422**: Validation errors (missing/invalid fields)
- **500**: Server errors
- **503**: Service unavailable (health check failures)

---

## Notes for Your Friend

1. **All endpoints support CORS** - can be called from any frontend
2. **conversation_id** should be unique (recommend UUID format)
3. **user_id** should come from your authentication system
4. **Automatic summarization** occurs every 20 messages
5. **Database persists** between requests
6. **Health endpoint** should be used for monitoring
7. **Streaming endpoint** uses Server-Sent Events format
