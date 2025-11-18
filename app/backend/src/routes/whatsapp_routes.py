# app/backend/src/routes/whatsapp_routes.py
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
import json
from app.backend.src.services.whatsapp_service import WhatsAppService
from app.backend.src.core.database import get_db

router = APIRouter()

@router.get("/webhook")
async def verify_webhook(
    request: Request,
    hub_mode: str = None,
    hub_verify_token: str = None,
    hub_challenge: str = None,
    db: Session = Depends(get_db)
):
    """Verificação do webhook do WhatsApp - FORTE"""
    print(f"🔐 VERIFICAÇÃO WEBHOOK - Mode: {hub_mode}, Token: {hub_verify_token}")
    
    whatsapp_service = WhatsAppService(db)
    result = whatsapp_service.verify_webhook(hub_mode, hub_verify_token, hub_challenge)
    
    if result:
        print("🎉 WEBHOOK VERIFICADO COM SUCESSO!")
        return int(result)
    
    print("❌ FALHA NA VERIFICAÇÃO DO WEBHOOK")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, 
        detail="Webhook verification failed"
    )

@router.post("/webhook")
async def webhook_handler(request: Request, db: Session = Depends(get_db)):
    """Recebe mensagens do WhatsApp - SUPER ROBUSTO"""
    try:
        print("🌐 WEBHOOK POST RECEBIDO - Iniciando processamento...")
        
        # Ler dados do request
        raw_body = await request.body()
        data = await request.json() if raw_body else {}
        
        print(f"📥 Dados brutos recebidos: {raw_body.decode() if raw_body else 'vazio'}")
        
        whatsapp_service = WhatsAppService(db)
        result = await whatsapp_service.process_incoming_message(data)
        
        print("✅ WEBHOOK PROCESSADO COM SUCESSO")
        return {
            "status": "success", 
            "data": result,
            "processed_at": "2024-12-19 14:30:00"
        }
        
    except Exception as e:
        print(f"💥 ERRO CRÍTICO NO WEBHOOK: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "status": "error", 
            "error": str(e),
            "message": "Erro interno no processamento do webhook"
        }, status.HTTP_500_INTERNAL_SERVER_ERROR

@router.get("/test-webhook")
async def test_webhook(db: Session = Depends(get_db)):
    """Rota de teste para simular mensagem WhatsApp"""
    try:
        print("🧪 TESTANDO WEBHOOK...")
        
        # Simular dados de mensagem WhatsApp
        test_data = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": "5511999999999",
                            "text": {"body": "Olá, me chamo João Silva e quero saber sobre planos de saúde"},
                            "id": "test_message_123"
                        }]
                    }
                }]
            }]
        }
        
        whatsapp_service = WhatsAppService(db)
        result = await whatsapp_service.process_incoming_message(test_data)
        
        return {
            "status": "test_completed",
            "result": result
        }
        
    except Exception as e:
        return {"status": "test_failed", "error": str(e)}