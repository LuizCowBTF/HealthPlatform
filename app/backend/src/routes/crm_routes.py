# app/backend/src/routes/crm_routes.py - VERSÃO COMPLETA CORRIGIDA
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
import traceback

from app.backend.src.core.database import get_db
from app.backend.src.core.modules.crm.models import Lead, Sale, Broker

router = APIRouter()

# ========== DASHBOARD & MÉTRICAS ==========
@router.get("/health")
async def crm_health():
    return {"status": "healthy", "module": "CRM"}

@router.get("/dashboard/metricas")
async def dashboard_metricas(db: Session = Depends(get_db)):
    """Métricas básicas do dashboard"""
    try:
        # Contagens básicas
        total_leads = db.query(Lead).count()
        total_vendas = db.query(Sale).count()
        corretores_ativos = db.query(Broker).filter(Broker.is_active == True).count()
        
        # Receitas
        sales_values = db.query(Sale.value).all()
        receita_total = sum([v[0] for v in sales_values if v[0] and isinstance(v[0], (int, float))])
        
        return {
            "status": "success",
            "data": {
                "total_leads": total_leads,
                "total_vendas": total_vendas,
                "receita_total": receita_total,
                "corretores_ativos": corretores_ativos,
                "taxa_conversao": round((total_vendas / total_leads * 100), 2) if total_leads > 0 else 0,
                "vendas_mes": total_vendas,  # Simplificado
                "receita_mensal": receita_total,  # Simplificado
                "leads_novos_hoje": 0,
                "vendas_hoje": 0
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "data": {}
        }

@router.get("/dashboard/completo")
async def dashboard_completo(db: Session = Depends(get_db)):
    """Dashboard completo com todos os dados"""
    try:
        # Métricas básicas
        total_leads = db.query(Lead).count()
        total_vendas = db.query(Sale).count()
        corretores_ativos = db.query(Broker).filter(Broker.is_active == True).count()
        
        # Receitas
        sales_values = db.query(Sale.value).all()
        receita_total = sum([v[0] for v in sales_values if v[0] and isinstance(v[0], (int, float))])
        
        # Vendas do mês atual
        inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        vendas_mes = db.query(Sale).filter(Sale.sale_date >= inicio_mes).count()
        
        # Receita do mês
        receita_mes_values = db.query(Sale.value).filter(Sale.sale_date >= inicio_mes).all()
        receita_mes = sum([v[0] for v in receita_mes_values if v[0] and isinstance(v[0], (int, float))])
        
        # Top corretores
        top_corretores = db.query(
            Broker.name, 
            func.count(Sale.id).label('total_vendas'),
            func.sum(Sale.value).label('receita_total')
        ).join(Sale, Broker.id == Sale.broker_id)\
         .group_by(Broker.id)\
         .order_by(func.sum(Sale.value).desc())\
         .limit(5)\
         .all()
        
        # Vendas por operadora
        vendas_operadora = db.query(
            Sale.operator,
            func.count(Sale.id).label('total'),
            func.sum(Sale.value).label('receita')
        ).filter(Sale.operator.isnot(None))\
         .group_by(Sale.operator)\
         .order_by(func.sum(Sale.value).desc())\
         .all()
        
        # Vendas por plano
        vendas_plano = db.query(
            Sale.plan_type,
            func.count(Sale.id).label('total')
        ).filter(Sale.plan_type.isnot(None))\
         .group_by(Sale.plan_type)\
         .order_by(func.count(Sale.id).desc())\
         .all()
        
        # Leads por origem
        leads_origem = db.query(
            Lead.source,
            func.count(Lead.id).label('total')
        ).filter(Lead.source.isnot(None))\
         .group_by(Lead.source)\
         .order_by(func.count(Lead.id).desc())\
         .all()
        
        # Leads por status
        leads_status = db.query(
            Lead.status,
            func.count(Lead.id).label('total')
        ).filter(Lead.status.isnot(None))\
         .group_by(Lead.status)\
         .order_by(func.count(Lead.id).desc())\
         .all()

        return {
            "status": "success",
            "data": {
                "metricas_principais": {
                    "total_leads": total_leads,
                    "total_vendas": total_vendas,
                    "receita_total": receita_total,
                    "receita_mensal": receita_mes,
                    "vendas_mensais": vendas_mes,
                    "corretores_ativos": corretores_ativos,
                    "taxa_conversao": round((total_vendas / total_leads * 100), 2) if total_leads > 0 else 0
                },
                "top_corretores": [
                    {
                        "nome": corretor.name,
                        "vendas": corretor.total_vendas,
                        "receita": corretor.receita_total or 0
                    } for corretor in top_corretores
                ],
                "vendas_por_operadora": [
                    {
                        "operadora": operadora.operator or "Não especificado",
                        "vendas": operadora.total,
                        "receita": operadora.receita or 0
                    } for operadora in vendas_operadora
                ],
                "vendas_por_plano": [
                    {
                        "plano": plano.plan_type or "Não especificado", 
                        "vendas": plano.total
                    } for plano in vendas_plano
                ],
                "leads_por_origem": [
                    {
                        "origem": origem.source or "Não especificado",
                        "total": origem.total
                    } for origem in leads_origem
                ],
                "leads_por_status": [
                    {
                        "status": status.status or "Não especificado",
                        "total": status.total
                    } for status in leads_status
                ]
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "data": {}
        }


@router.get("/corretores/performance")
async def corretores_performance(db: Session = Depends(get_db)):
    """Performance detalhada de todos os corretores - VERSÃO CORRIGIDA"""
    try:
        performance = db.query(
            Broker.id,
            Broker.name,
            Broker.email,
            Broker.phone,
            Broker.monthly_goal,
            func.count(Sale.id).label('total_vendas'),
            func.sum(Sale.value).label('receita_total'),
            func.sum(Sale.commission_value).label('comissao_total')
        ).outerjoin(Sale, Broker.id == Sale.broker_id)\
         .group_by(Broker.id)\
         .order_by(func.sum(Sale.value).desc())\
         .all()
        
        return {
            "status": "success",
            "data": [
                {
                    "id": p.id,
                    "nome": p.name,
                    "email": p.email,
                    "telefone": p.phone,
                    "meta_mensal": p.monthly_goal or 0,
                    "vendas_realizadas": p.total_vendas or 0,
                    "receita_gerada": p.receita_total or 0,
                    "comissao_gerada": p.comissao_total or 0,
                    "atingimento_meta": round((p.receita_total / (p.monthly_goal or 1)) * 100, 2) if p.monthly_goal and p.monthly_goal > 0 else 0
                } for p in performance
            ]
        }
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e),
            "data": []
        }


@router.get("/leads")
async def listar_leads(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    """Listar leads"""
    try:
        leads = db.query(Lead).offset(skip).limit(limit).all()
        
        leads_data = []
        for lead in leads:
            leads_data.append({
                "id": lead.id,
                "nome": lead.full_name,
                "telefone": lead.phone,
                "email": lead.email,
                "origem": lead.source,
                "status": lead.status
            })
        
        return {
            "status": "success",
            "data": leads_data,
            "pagination": {"skip": skip, "limit": limit, "total": len(leads)}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar leads: {str(e)}")

@router.get("/vendas")
async def listar_vendas(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    """Listar vendas"""
    try:
        vendas = db.query(Sale).offset(skip).limit(limit).all()
        
        vendas_data = []
        for venda in vendas:
            vendas_data.append({
                "id": venda.id,
                "plano": venda.plan_type,
                "operadora": venda.operator,
                "valor": venda.value,
                "comissao": venda.commission_value,
                "status": venda.status
            })
        
        return {
            "status": "success",
            "data": vendas_data,
            "pagination": {"skip": skip, "limit": limit, "total": len(vendas)}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar vendas: {str(e)}")

@router.get("/corretores")
async def listar_corretores(db: Session = Depends(get_db)):
    """Listar corretores"""
    try:
        corretores = db.query(Broker).filter(Broker.is_active == True).all()
        
        corretores_data = []
        for corretor in corretores:
            corretores_data.append({
                "id": corretor.id,
                "nome": corretor.name,
                "email": corretor.email,
                "telefone": corretor.phone,
                "meta_mensal": corretor.monthly_goal,
                "ativo": corretor.is_active
            })
        
        return {
            "status": "success",
            "data": corretores_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar corretores: {str(e)}")