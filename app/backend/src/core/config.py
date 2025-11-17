# app/backend/src/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./health_platform.db"
    
    # WhatsApp
    WHATSAPP_TOKEN: str
    WHATSAPP_WEBHOOK_TOKEN: str = "meu_token_secreto"
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    
    class Config:
        env_file = ".env"

settings = Settings()