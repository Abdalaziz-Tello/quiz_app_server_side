"""
Configuration file for Quiz App Backend
"""

import os
from typing import Optional

class Settings:
    # JWT Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    RELOAD: bool = os.getenv("RELOAD", "true").lower() == "true"
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./quiz_app.db")
    
    # CORS Configuration
    CORS_ORIGINS: list = ["*"]  # Change this in production
    
    # Security Configuration
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

# Global settings instance
settings = Settings()

# Print configuration on import (for debugging)
if __name__ == "__main__":
    print("🔧 Quiz App Configuration:")
    print(f"  SECRET_KEY: {'*' * len(settings.SECRET_KEY)}")
    print(f"  ACCESS_TOKEN_EXPIRE_MINUTES: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}")
    print(f"  HOST: {settings.HOST}")
    print(f"  PORT: {settings.PORT}")
    print(f"  RELOAD: {settings.RELOAD}")
    print(f"  DATABASE_URL: {settings.DATABASE_URL}")
    print(f"  DEBUG: {settings.DEBUG}")
