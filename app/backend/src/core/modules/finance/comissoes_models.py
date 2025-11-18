# app/backend/src/core/modules/finance/comissoes_models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Corretor(Base):
    __tablename__ = "brokers"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True)
    telefone = Column(String(20))
    cpf = Column(String(14), unique=True)
    percentual_comissao = Column(Float, default=10.0)  # % padrão
    ativo = Column(Boolean, default=True)
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Corretor {self.nome}>"

class Venda(Base):
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    corretor_id = Column(Integer, nullable=False)
    lead_id = Column(Integer, nullable=False)
    plano_vendido = Column(String(50), nullable=False)  # INDIVIDUAL, FAMILIAR, etc
    valor_venda = Column(Float, nullable=False)
    valor_comissao = Column(Float, nullable=False)
    percentual_comissao = Column(Float, nullable=False)
    data_venda = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="pendente")  # pendente, paga, cancelada
    
    def __repr__(self):
        return f"<Venda {self.id} - {self.plano_vendido}>"

class Comissao(Base):
    __tablename__ = "comissoes"
    
    id = Column(Integer, primary_key=True, index=True)
    corretor_id = Column(Integer, nullable=False)
    mes_referencia = Column(String(7), nullable=False)  # YYYY-MM
    total_vendas = Column(Float, default=0.0)
    total_comissao = Column(Float, default=0.0)
    status_pagamento = Column(String(20), default="pendente")  # pendente, paga, atrasada
    data_calculo = Column(DateTime, default=datetime.utcnow)
    data_pagamento = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Comissao {self.mes_referencia} - R$ {self.total_comissao}>"