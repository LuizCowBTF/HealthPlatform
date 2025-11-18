# app/backend/src/core/config.py - VERSÃO TOLERANTE
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./health_platform.db"
    
    # App
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # WhatsApp (opcionais para desenvolvimento)
    WHATSAPP_TOKEN: Optional[str] = None
    WHATSAPP_ACCESS_TOKEN: Optional[str] = None
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = None
    WHATSAPP_BUSINESS_ID: Optional[str] = None
    WHATSAPP_APP_SECRET: Optional[str] = None
    WHATSAPP_VERIFY_TOKEN: Optional[str] = "health_platform_test"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

# Configurações padrão para desenvolvimento
if settings.ENVIRONMENT == "development":
    if not settings.WHATSAPP_TOKEN:
        settings.WHATSAPP_TOKEN = "dev_temp_token"
    if not settings.WHATSAPP_ACCESS_TOKEN:
        settings.WHATSAPP_ACCESS_TOKEN = "dev_temp_access_token"
    print("⚠️  Modo desenvolvimento - usando tokens temporários")