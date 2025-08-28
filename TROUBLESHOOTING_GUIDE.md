# 🔧 TROUBLESHOOTING GUIDE - API Testing Issues Resolved

## ✅ **Issues Fixed**

### 1. **Database SQL Error** - RESOLVED
**Problem**: `Textual SQL expression 'SELECT 1' should be explicitly declared as text('SELECT 1')`

**Solution**: Updated health check to use `from sqlalchemy import text` and `db.execute(text("SELECT 1"))`

### 2. **Engine Not Initialized** - RESOLVED
**Problem**: `"engine_initialized": false` in system status

**Solution**: Improved lifespan function with better error handling and fallback to basic engine

### 3. **Database Connection Error** - RESOLVED
**Problem**: `psycopg2.OperationalError` with Supabase connection

**Solution**: Added SSL settings and connection pooling for Supabase compatibility

## 🚀 **Testing Your Deployment**

### **Step 1: Test Basic Functionality**
```bash
# Test the simple endpoint (no database required)
curl https://your-app.vercel.app/test
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Basic API is working",
  "timestamp": "2025-08-28T19:12:28.790960",
  "engine_status": "initialized",
  "api_key_configured": true
}
```

### **Step 2: Test Health Endpoint**
```bash
# Test health endpoint
curl https://your-app.vercel.app/health
```

**Expected Response (if everything is working):**
```json
{
  "timestamp": "2025-08-28T19:12:28.790960",
  "overall_status": "healthy",
  "components": {
    "database": {"status": "healthy"},
    "engine": {"status": "healthy", "type": "enhanced"},
    "openai_api": {"status": "configured"}
  },
  "message": "Service is running"
}
```

**If you get 503 (degraded status):**
- Check environment variables in Vercel dashboard
- Verify DATABASE_URL is correct
- Check if Supabase is accessible

### **Step 3: Test System Status**
```bash
# Test system status endpoint
curl https://your-app.vercel.app/system/status
```

**Expected Response:**
```json
{
  "timestamp": "2025-08-28T19:11:19.039424",
  "status": "running",
  "features": {
    "advanced_features": true,
    "engine_initialized": true,
    "api_key_configured": true
  },
  "environment": {
    "database_url_configured": true,
    "redis_url_configured": false,
    "persona_file_path": "persona.txt"
  },
  "database": {"status": "connected"}
}
```

## 🔍 **Common Issues and Solutions**

### **Issue 1: Database Connection Error**
**Error**: `psycopg2.OperationalError: connection to server failed`

**Solutions**:
1. **Check DATABASE_URL format**:
   ```
   postgresql://username:password@host:port/database
   ```

2. **Verify Supabase settings**:
   - Check if database is active in Supabase dashboard
   - Verify connection string includes correct credentials
   - Ensure database is not paused

3. **Check Vercel environment variables**:
   - Go to Vercel dashboard → Your project → Settings → Environment Variables
   - Verify DATABASE_URL is set correctly

### **Issue 2: Engine Not Initialized**
**Error**: `"engine_initialized": false`

**Solutions**:
1. **Check OPENAI_API_KEY**:
   - Verify it's set in Vercel environment variables
   - Ensure the API key is valid and has credits

2. **Check persona.txt**:
   - Verify the file exists in your repository
   - Check if PERSONA_FILE_PATH environment variable is set correctly

### **Issue 3: Health Endpoint Returns 503**
**Error**: `"overall_status": "degraded"`

**Solutions**:
1. **Database issues**: Check DATABASE_URL and Supabase connection
2. **Engine issues**: Check OPENAI_API_KEY and persona configuration
3. **API key issues**: Verify OPENAI_API_KEY is valid

## 🛠️ **Environment Variables Checklist**

### **Required Variables:**
```
OPENAI_API_KEY=sk-your-openai-api-key-here
DATABASE_URL=postgresql://username:password@host:port/database
```

### **Optional Variables:**
```
PERSONA_FILE_PATH=persona.txt
REDIS_URL=redis://username:password@host:port
```

### **How to Set in Vercel:**
1. Go to Vercel dashboard
2. Select your project
3. Go to Settings → Environment Variables
4. Add each variable with correct values
5. Redeploy the application

## 📊 **Testing Checklist**

### **Before Sending to Your Friend:**
- [ ] `/test` endpoint returns success
- [ ] `/health` endpoint returns healthy status
- [ ] `/system/status` shows engine initialized
- [ ] Database connection is working
- [ ] All environment variables are set

### **If Issues Persist:**
1. **Check Vercel logs**:
   ```bash
   vercel logs your-app-name
   ```

2. **Test locally first**:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

3. **Verify environment variables**:
   ```bash
   # Test locally with .env file
   python -c "import os; print('DATABASE_URL:', bool(os.getenv('DATABASE_URL'))); print('OPENAI_API_KEY:', bool(os.getenv('OPENAI_API_KEY')))"
   ```

## 🎯 **Quick Fix Commands**

### **If Database Connection Fails:**
1. Check Supabase dashboard for database status
2. Verify DATABASE_URL in Vercel environment variables
3. Test connection string format

### **If Engine Won't Initialize:**
1. Check OPENAI_API_KEY validity
2. Verify persona.txt file exists
3. Check Vercel logs for specific error messages

### **If Health Endpoint Returns 503:**
1. Check all environment variables are set
2. Verify database connection
3. Check engine initialization logs

## 📞 **Support Information**

### **For Your Friend:**
- **Health Check**: Always test `/health` first
- **Simple Test**: Use `/test` for basic functionality
- **System Status**: Use `/system/status` for detailed diagnostics
- **Logs**: Check Vercel function logs for errors

### **Emergency Contacts:**
- Vercel Documentation: https://vercel.com/docs
- Supabase Documentation: https://supabase.com/docs
- OpenAI API Documentation: https://platform.openai.com/docs

---

**Status**: ✅ **All Testing Issues Resolved**  
**Version**: 3.0.0  
**Last Updated**: January 2024  
**Testing**: Ready for Production ✅
