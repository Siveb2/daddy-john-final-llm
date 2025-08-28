#!/bin/bash

# AI Persona Chatbot - Deployment Script
# This script helps deploy the chatbot to Vercel

echo "🚀 AI Persona Chatbot Deployment Script"
echo "======================================"

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating template..."
    cat > .env << EOF
# Required Environment Variables
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=your_postgresql_database_url_here

# Optional Environment Variables
PERSONA_FILE_PATH=persona.txt
REDIS_URL=your_redis_url_here
EOF
    echo "📝 Please edit .env file with your actual values before deploying"
    exit 1
fi

# Check if requirements.txt exists
if [ ! -f requirements.txt ]; then
    echo "❌ requirements.txt not found"
    exit 1
fi

# Check if main.py exists
if [ ! -f app/main.py ]; then
    echo "❌ app/main.py not found"
    exit 1
fi

# Check if vercel.json exists
if [ ! -f vercel.json ]; then
    echo "❌ vercel.json not found"
    exit 1
fi

echo "✅ All required files found"

# Test local installation
echo "🧪 Testing local installation..."
python -c "import fastapi, uvicorn, sqlalchemy, openai" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Dependencies not installed. Installing..."
    pip install -r requirements.txt
fi

echo "✅ Dependencies verified"

# Deploy to Vercel
echo "🚀 Deploying to Vercel..."
vercel --prod

echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Set environment variables in Vercel dashboard"
echo "2. Test the health endpoint: https://your-app.vercel.app/health"
echo "3. Test chat functionality"
echo "4. Monitor logs for any issues"
echo ""
echo "🔗 API Documentation: https://your-app.vercel.app/docs"
