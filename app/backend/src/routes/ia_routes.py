# app/backend/src/routes/ia_routes.py
from fastapi import APIRouter, HTTPException
from app.backend.src.core.modules.ai.health_ia import health_ia

router = APIRouter()

@router.post("/analisar-perfil")
async def analisar_perfil(dados_cliente: dict):
    """Analisa perfil do cliente e sugere plano ideal"""
    try:
        resultado = health_ia.analisar_perfil_cliente(dados_cliente)
        return {
            "status": "success",
            "data": resultado,
            "sistema": "HEALTH-IA BRASILEIRO"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")


@router.post("/gerar-script-venda")
async def gerar_script_venda(dados: dict):
    """Gera script de venda personalizado"""
    try:
        perfil = dados.get("perfil_cliente", {})
        plano = dados.get("plano_sugerido", "INDIVIDUAL")
        formato = dados.get("formato", "texto")  # Novo parâmetro
        
        script = health_ia.gerar_script_venda(perfil, plano, formato)
        return {
            "status": "success", 
            "data": {
                "script": script,
                "plano": plano,
                "cliente": perfil.get("nome", "Cliente"),
                "formato": formato
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro gerando script: {str(e)}")


@router.get("/perguntas-triagem")
async def perguntas_triagem():
    """Retorna perguntas para qualificação"""
    try:
        perguntas = health_ia.perguntas_triagem()
        return {
            "status": "success",
            "data": {
                "perguntas": perguntas,
                "total_perguntas": len(perguntas)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro nas perguntas: {str(e)}")

@router.get("/planos-disponiveis")
async def planos_disponiveis():
    """Lista todos os planos disponíveis"""
    try:
        return {
            "status": "success",
            "data": health_ia.planos_disponiveis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro nos planos: {str(e)}")