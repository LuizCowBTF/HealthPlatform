# app/backend/src/routes/whatsapp_webhook.py
from fastapi import APIRouter, Request, HTTPException
from app.backend.src.core.services.orchestration_service import orchestration_service
import logging
import json

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/webhook")
async def verify_webhook(request: Request):
    """Verificação do webhook do Meta"""
    try:
        params = dict(request.query_params)
        
        # Verificação do token (Webhook Meta)
        if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == "healthplatform_brazil_2024":
            logger.info("✅ Webhook verificado com sucesso!")
            return int(params["hub.challenge"])
        else:
            logger.warning("❌ Token de verificação inválido")
            raise HTTPException(status_code=403, detail="Token inválido")
            
    except Exception as e:
        logger.error(f"Erro na verificação: {str(e)}")
        raise HTTPException(status_code=400, detail="Erro na verificação")

@router.post("/webhook")
async def process_webhook(request: Request):
    """Processa mensagens recebidas do WhatsApp"""
    try:
        body = await request.json()
        logger.info(f"📨 Webhook recebido: {json.dumps(body, indent=2)}")
        
        # Processar entrada do WhatsApp
        entry = body.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        
        # Verificar se é mensagem
        if "messages" in value:
            messages = value["messages"]
            
            for message in messages:
                if message["type"] == "text":
                    await processar_mensagem_texto(message, value)
                    
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"❌ Erro no webhook: {str(e)}")
        return {"status": "error", "message": str(e)}

async def processar_mensagem_texto(message: dict, value: dict):
    """Processa mensagem de texto recebida"""
    try:
        # Extrair dados da mensagem
        dados_mensagem = {
            "from": message["from"],
            "text": message.get("text", {}).get("body", ""),
            "message_id": message["id"],
            "timestamp": message["timestamp"],
            "profile_name": await obter_nome_perfil(message["from"], value),
            "whatsapp_business_id": value.get("metadata", {}).get("phone_number_id")
        }
        
        logger.info(f"💬 Mensagem de {dados_mensagem['profile_name']}: {dados_mensagem['text']}")
        
        # ORQUESTRAÇÃO - Processar com IA + CRM
        resultado = await orchestration_service.processar_mensagem_whatsapp(dados_mensagem)
        
        # Enviar resposta automática
        if resultado["success"] and resultado["resposta"]:
            await enviar_resposta_whatsapp(
                to=dados_mensagem["from"],
                message=resultado["resposta"],
                business_id=dados_mensagem["whatsapp_business_id"]
            )
            
            logger.info(f"✅ Resposta enviada para {dados_mensagem['profile_name']}")
            
    except Exception as e:
        logger.error(f"❌ Erro processando mensagem: {str(e)}")

async def obter_nome_perfil(telefone: str, value: dict) -> str:
    """Obtém nome do perfil do WhatsApp"""
    try:
        contacts = value.get("contacts", [])
        for contact in contacts:
            if contact["wa_id"] == telefone:
                return contact.get("profile", {}).get("name", "Cliente")
        return "Cliente"
    except:
        return "Cliente"

async def enviar_resposta_whatsapp(to: str, message: str, business_id: str):
    """Envia resposta via WhatsApp Business API"""
    try:
        from app.backend.src.modules.whatsapp.service import whatsapp_service
        
        await whatsapp_service.enviar_mensagem_texto(
            to=to,
            message=message,
            business_phone_id=business_id
        )
        
        logger.info(f"📤 Resposta enviada para {to}")
        
    except Exception as e:
        logger.error(f"❌ Erro enviando resposta WhatsApp: {str(e)}")