# app/backend/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.backend.src.core.database import get_db, engine
from app.backend.src.core.config import settings
from app.backend.src.modules.crm.models import Base
from app.backend.src.api.v1 import crm_routes, finance_routes, whatsapp_routes

# Criar tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HealthPlatform SaaS", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="app/frontend/static"), name="static")
templates = Jinja2Templates(directory="app/frontend/templates")

# Registrar rotas
app.include_router(crm_routes.router, prefix="/api/v1/crm", tags=["CRM"])
app.include_router(finance_routes.router, prefix="/api/v1/finance", tags=["Finance"])
app.include_router(whatsapp_routes.router, prefix="/api/v1/whatsapp", tags=["WhatsApp"])

@app.get("/")
async def root():
    return {"message": "HealthPlatform SaaS - Sistema CRM + Financeiro"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "HealthPlatform"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)