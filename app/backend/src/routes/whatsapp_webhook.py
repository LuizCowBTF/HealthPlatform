# app/backend/src/routes/whatsapp_webhook.py
from fastapi import APIRouter, Request, HTTPException
from app.backend.src.core.services.orchestration_service import orchestration_service
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/webhook")
async def verify_webhook(request: Request):
    """Verificação do webhook do Meta WhatsApp"""
    try:
        params = dict(request.query_params)
        
        # Webhook verification (Meta requirements)
        if (params.get("hub.mode") == "subscribe" and 
            params.get("hub.verify_token") == "healthplatform_brazil_2024"):
            logger.info("✅ Webhook do WhatsApp verificado!")
            return int(params["hub.challenge"])
        else:
            logger.warning("❌ Token de verificação inválido")
            raise HTTPException(status_code=403, detail="Token inválido")
            
    except Exception as e:
        logger.error(f"Erro na verificação: {str(e)}")
        raise HTTPException(status_code=400, detail="Erro na verificação")

@router.post("/webhook")
async def process_webhook(request: Request):
    """Processa mensagens reais do WhatsApp usando nossa ORQUESTRAÇÃO"""
    try:
        body = await request.json()
        logger.info("📨 Webhook REAL recebido do WhatsApp")
        
        # Log para debug (remover em produção)
        logger.debug(f"Payload completo: {json.dumps(body, indent=2)}")
        
        # Processar estrutura do webhook do WhatsApp Business API
        entry = body.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        
        # Verificar se é mensagem
        if "messages" in value:
            messages = value["messages"]
            
            for message in messages:
                await processar_mensagem_real(message, value)
                    
        return {"status": "success", "message": "Processado pela orquestração"}
        
    except Exception as e:
        logger.error(f"❌ Erro no webhook real: {str(e)}")
        return {"status": "error", "message": str(e)}

async def processar_mensagem_real(message: dict, value: dict):
    """Processa mensagem REAL do WhatsApp usando nossa orquestração"""
    try:
        # Extrair dados da mensagem real do WhatsApp
        dados_mensagem = {
            "from": message["from"],
            "text": message.get("text", {}).get("body", ""),
            "message_id": message["id"],
            "timestamp": message["timestamp"],
            "profile_name": await obter_nome_perfil_real(message["from"], value),
            "whatsapp_business_id": value.get("metadata", {}).get("phone_number_id")
        }
        
        logger.info(f"💬 Mensagem REAL de {dados_mensagem['profile_name']}: {dados_mensagem['text'][:50]}...")
        
        # 🎯 USAR NOSSA ORQUESTRAÇÃO PARA PROCESSAR MENSAGEM REAL
        resultado = await orchestration_service.processar_mensagem_whatsapp(dados_mensagem)
        
        if resultado["success"]:
            logger.info(f"✅ Mensagem REAL processada com sucesso - Estágio: {resultado['estagio_funil']}")
        else:
            logger.error(f"❌ Erro ao processar mensagem REAL: {resultado.get('error')}")
            
    except Exception as e:
        logger.error(f"💥 Erro processando mensagem REAL: {str(e)}")

async def obter_nome_perfil_real(telefone: str, value: dict) -> str:
    """Obtém nome do perfil REAL do WhatsApp"""
    try:
        contacts = value.get("contacts", [])
        for contact in contacts:
            if contact["wa_id"] == telefone:
                return contact.get("profile", {}).get("name", "Cliente")
        return "Cliente"
    except:
        return "Cliente"

# 🎯 ROTAS ADICIONAIS PARA O DASHBOARD
@router.get("/estatisticas")
async def obter_estatisticas():
    """Retorna estatísticas para o dashboard"""
    # Em produção, isso viria do database
    return {
        "total_leads": 150,
        "leads_hoje": 12,
        "taxa_conversao": "23%",
        "estagios_funil": {
            "contato_inicial": 45,
            "interesse_preco": 35,
            "interesse_planos": 28,
            "qualificacao": 22,
            "proposta_enviada": 15,
            "fechado": 8
        },
        "planos_mais_procurados": [
            {"plano": "FAMILIAR", "quantidade": 65},
            {"plano": "INDIVIDUAL", "quantidade": 45},
            {"plano": "EMPRESARIAL", "quantidade": 25},
            {"plano": "VIP", "quantidade": 15}
        ]
    }

@router.get("/leads-recentes")
async def obter_leads_recentes():
    """Retorna leads recentes para o dashboard"""
    # Em produção, isso viria do database
    return {
        "leads": [
            {
                "id": 1,
                "nome": "João Silva",
                "telefone": "5511912345678",
                "estagio": "interesse_preco",
                "plano_sugerido": "FAMILIAR",
                "ultima_mensagem": "Quanto custa o plano familiar?",
                "data_criacao": "2024-01-15 10:30:00"
            },
            {
                "id": 2,
                "nome": "Maria Santos",
                "telefone": "5511987654321", 
                "estagio": "contato_inicial",
                "plano_sugerido": None,
                "ultima_mensagem": "Oi, gostaria de informações",
                "data_criacao": "2024-01-15 09:15:00"
            }
        ]
    }