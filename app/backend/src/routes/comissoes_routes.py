# app/backend/src/routes/comissoes_routes.py
from fastapi import APIRouter, HTTPException
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Service simulado - em produção injetaria o database
comissoes_service = None

@router.get("/corretores")
async def listar_corretores():
    """Lista todos os corretores"""
    try:
        corretores = await comissoes_service.listar_corretores()
        return {
            "status": "success",
            "data": corretores,
            "total": len(corretores)
        }
    except Exception as e:
        logger.error(f"❌ Erro ao listar corretores: {e}")
        raise HTTPException(status_code=500, detail="Erro interno")

@router.post("/vendas/registrar")
async def registrar_venda(venda_data: dict):
    """Registra uma nova venda e calcula comissão"""
    try:
        venda_registrada = await comissoes_service.registrar_venda(venda_data)
        return {
            "status": "success",
            "data": venda_registrada,
            "message": "Venda registrada com sucesso"
        }
    except Exception as e:
        logger.error(f"❌ Erro ao registrar venda: {e}")
        raise HTTPException(status_code=500, detail="Erro ao registrar venda")

@router.get("/corretores/{corretor_id}/comissoes")
async def obter_comissoes_corretor(corretor_id: int, mes: Optional[str] = None):
    """Obtém comissões de um corretor específico"""
    try:
        comissoes = await comissoes_service.calcular_comissoes_mes(corretor_id, mes)
        return {
            "status": "success", 
            "data": comissoes
        }
    except Exception as e:
        logger.error(f"❌ Erro ao obter comissões: {e}")
        raise HTTPException(status_code=500, detail="Erro ao calcular comissões")

@router.get("/relatorio/mensal")
async def relatorio_comissoes_mensal(mes: str):
    """Relatório completo de comissões do mês"""
    try:
        # Simulação - em produção geraria relatório completo
        relatorio = {
            "mes_referencia": mes,
            "total_vendas_mes": 85000.00,
            "total_comissoes_mes": 10200.00,
            "corretores_ativos": 12,
            "vendas_por_plano": {
                "FAMILIAR": 25,
                "EMPRESARIAL": 8, 
                "VIP": 12,
                "INDIVIDUAL": 15
            }
        }
        
        return {
            "status": "success",
            "data": relatorio
        }
    except Exception as e:
        logger.error(f"❌ Erro ao gerar relatório: {e}")
        raise HTTPException(status_code=500, detail="Erro ao gerar relatório")