# Vercel entry point for FastAPI
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the FastAPI app
from app.main import app

# This is the correct way to export FastAPI for Vercel
# The app object itself is the handler
