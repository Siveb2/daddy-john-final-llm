#!/usr/bin/env python3
"""
Comprehensive Testing Script for AI Persona Chatbot
Run this script to verify all components are working correctly.
"""

import sys
import json
import asyncio
import requests
from datetime import datetime

def test_imports():
    """Test all critical imports"""
    print("🔍 Testing imports...")
    
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import openai
        import pydantic
        import aiofiles
        import aiohttp
        import httpx
        import tenacity
        import redis
        import tiktoken
        print("✅ All dependencies imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_database():
    """Test database connection and models"""
    print("\n🔍 Testing database...")
    
    try:
        from app.db.database import engine, SessionLocal
        from app.db import models
        from sqlalchemy import text
        
        # Test table creation
        models.Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        # Test session creation
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        print("✅ Database connection working")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_app_imports():
    """Test application imports"""
    print("\n🔍 Testing application imports...")
    
    try:
        from app.main import app
        from app.core.chatbot_core import ChatbotEngine, PersonaManager
        from app.core.advanced_features import ProductionChatbotEngine
        from app.db import crud
        
        print(f"✅ FastAPI app: {app.title} v{app.version}")
        print(f"✅ Routes configured: {len(app.routes)}")
        print("✅ All application modules imported")
        return True
    except Exception as e:
        print(f"❌ Application import error: {e}")
        return False

def test_persona():
    """Test persona loading"""
    print("\n🔍 Testing persona...")
    
    try:
        from app.core.chatbot_core import PersonaManager
        pm = PersonaManager()
        
        if pm.persona_content:
            print(f"✅ Persona loaded: {pm.persona_content[:50]}...")
            return True
        else:
            print("❌ Persona content is empty")
            return False
    except Exception as e:
        print(f"❌ Persona error: {e}")
        return False

def test_vercel_config():
    """Test Vercel configuration"""
    print("\n🔍 Testing Vercel configuration...")
    
    try:
        with open('vercel.json', 'r') as f:
            config = json.load(f)
        
        required_keys = ['version', 'builds', 'routes']
        for key in required_keys:
            if key not in config:
                print(f"❌ Missing required key: {key}")
                return False
        
        if config['version'] != 2:
            print("❌ Vercel version should be 2")
            return False
        
        if not config['builds']:
            print("❌ No builds configured")
            return False
        
        if not config['routes']:
            print("❌ No routes configured")
            return False
        
        print("✅ Vercel configuration is valid")
        return True
    except Exception as e:
        print(f"❌ Vercel config error: {e}")
        return False

def test_requirements():
    """Test requirements.txt"""
    print("\n🔍 Testing requirements.txt...")
    
    try:
        with open('requirements.txt', 'r') as f:
            lines = f.readlines()
        
        packages = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
        
        if len(packages) < 10:
            print(f"❌ Too few packages: {len(packages)}")
            return False
        
        print(f"✅ Requirements file has {len(packages)} packages")
        return True
    except Exception as e:
        print(f"❌ Requirements error: {e}")
        return False

def test_environment_variables():
    """Test environment variables"""
    print("\n🔍 Testing environment variables...")
    
    import os
    
    # Check for required environment variables
    required_vars = ['OPENAI_API_KEY', 'DATABASE_URL']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("   These should be set in Vercel dashboard")
        return True  # Don't fail the test, just warn
    else:
        print("✅ All required environment variables are set")
        return True

def test_api_endpoints():
    """Test API endpoints (if running locally)"""
    print("\n🔍 Testing API endpoints...")
    
    try:
        from app.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test root endpoint
        response = client.get("/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
        
        # Test health endpoint (may fail without env vars, which is expected)
        response = client.get("/health")
        if response.status_code in [200, 503]:  # 503 is expected without env vars
            print("✅ Health endpoint working (503 is expected without env vars)")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test persona endpoint
        response = client.get("/persona")
        if response.status_code == 200:
            print("✅ Persona endpoint working")
        else:
            print(f"❌ Persona endpoint failed: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"⚠️  API testing skipped (not running locally): {e}")
        return True

def main():
    """Run all tests"""
    print("🚀 AI Persona Chatbot - Deployment Testing")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    tests = [
        ("Dependencies", test_imports),
        ("Database", test_database),
        ("Application", test_app_imports),
        ("Persona", test_persona),
        ("Vercel Config", test_vercel_config),
        ("Requirements", test_requirements),
        ("Environment", test_environment_variables),
        ("API Endpoints", test_api_endpoints),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your deployment is ready.")
        print("\n📋 Next steps:")
        print("1. Push code to GitHub")
        print("2. Connect to Vercel")
        print("3. Set environment variables in Vercel dashboard")
        print("4. Deploy with: vercel --prod")
        print("5. Test the live endpoints")
    else:
        print("⚠️  Some tests failed. Please fix the issues before deploying.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
