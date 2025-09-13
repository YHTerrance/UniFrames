import os
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Frame Gen API"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "API for Frame Gen application"
    
    # Environment settings
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = ENV == "development"
    
    # API settings
    API_PREFIX: str = "/api/v1"
    
    # CORS settings
    CORS_ORIGINS: list = ["*"]
    
    # Database settings
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create settings instance
settings = Settings()