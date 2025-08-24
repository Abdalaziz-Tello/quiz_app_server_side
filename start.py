#!/usr/bin/env python3
"""
Production startup script for Quiz App Backend
"""

import uvicorn
import os

if __name__ == "__main__":
    # Configuration for production
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "10000"))
    
    print("🚀 Starting Quiz App Backend (Production Mode)")
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"📖 API Docs: http://{host}:{port}/docs")
    print(f"📚 ReDoc: http://{host}:{port}/redoc")
    print("=" * 50)
    
    # Start the server in production mode
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )
