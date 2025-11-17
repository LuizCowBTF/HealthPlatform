# app/backend/src/modules/crm/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.backend.src.core.database import Base

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100))
    source = Column(String(50))  # Plantão, Instagram, etc.
    status = Column(String(50))  # Novo, Em contato, Convertido, etc.
    broker_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Sale(Base):
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer)
    broker_id = Column(Integer)
    plan_type = Column(String(50))  # PME, PF, Adesão
    operator = Column(String(50))   # Amil, Bradesco, etc.
    value = Column(Float)
    commission_value = Column(Float)
    status = Column(String(20))     # pending, completed, cancelled
    sale_date = Column(DateTime(timezone=True), server_default=func.now())

class Broker(Base):
    __tablename__ = "brokers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100))
    phone = Column(String(20))
    monthly_goal = Column(Float, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())