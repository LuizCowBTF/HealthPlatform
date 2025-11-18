# app/backend/src/services/whatsapp_service.py
from typing import Dict, Optional
from sqlalchemy.orm import Session
import json
from datetime import datetime

class WhatsAppService:
    def __init__(self, db: Session):
        self.db = db
        from app.backend.src.services.crm_service import CRMService
        self.crm_service = CRMService(db)
        self.webhook_verified = False
    
    async def process_incoming_message(self, data: Dict) -> Dict:
        """Processa mensagem recebida - SUPER ROBUSTO"""
        try:
            print("🔄 INICIANDO PROCESSAMENTO WHATSAPP...")
            print(f"📦 Dados recebidos: {json.dumps(data, indent=2)}")
            
            # Extrair dados da mensagem
            message_data = self._extract_message_data(data)
            if not message_data:
                return {"error": "Estrutura de mensagem inválida"}
            
            phone = message_data['phone']
            text = message_data['text']
            message_id = message_data.get('message_id', 'unknown')
            
            print(f"📱 MENSAGEM RECEBIDA - Phone: {phone}, ID: {message_id}")
            print(f"💬 Texto: {text}")
            
            # ✅ CRIAR/ATUALIZAR LEAD NO CRM
            lead_result = self.crm_service.create_whatsapp_lead(phone, text)
            
            response_data = {
                "phone": phone,
                "message": text,
                "message_id": message_id,
                "lead_creation": lead_result,
                "type": "incoming",
                "timestamp": datetime.now().isoformat(),
                "processed_at": datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
            
            # Se lead foi criado/atualizado com sucesso
            if lead_result["success"]:
                lead_id = lead_result["lead_id"]
                
                # ✅ ENVIAR RESPOSTA AUTOMÁTICA
                welcome_message = self._generate_welcome_response(lead_result.get('lead_name', 'Lead WhatsApp'))
                send_result = await self.send_message(phone, welcome_message)
                
                # ✅ SALVAR RESPOSTA NO HISTÓRICO
                if send_result:
                    self.crm_service.update_lead_conversation(lead_id, welcome_message, "outgoing")
                
                response_data["auto_reply"] = {
                    "sent": send_result,
                    "message": welcome_message,
                    "lead_id": lead_id
                }
                
                print(f"🎯 PROCESSAMENTO COMPLETO - Lead ID: {lead_id}")
            else:
                print(f"⚠️ PROCESSAMENTO PARCIAL - Erro: {lead_result.get('error')}")
            
            return response_data
            
        except Exception as e:
            print(f"💥 ERRO CRÍTICO NO PROCESSAMENTO: {e}")
            import traceback
            traceback.print_exc()
            return {"error": f"Erro interno: {str(e)}"}
    
    def _extract_message_data(self, data: Dict) -> Optional[Dict]:
        """Extrai dados da mensagem do webhook - SUPER FLEXÍVEL"""
        try:
            # Múltiplos formatos possíveis do webhook
            entries = data.get('entry', [])
            if not entries:
                return None
            
            for entry in entries:
                changes = entry.get('changes', [])
                for change in changes:
                    value = change.get('value', {})
                    
                    # Verificar se tem mensagens
                    messages = value.get('messages', [])
                    if messages:
                        message = messages[0]
                        return {
                            'phone': message.get('from', ''),
                            'text': message.get('text', {}).get('body', ''),
                            'message_id': message.get('id', ''),
                            'timestamp': message.get('timestamp', '')
                        }
            
            return None
            
        except Exception as e:
            print(f"❌ Erro ao extrair dados: {e}")
            return None
    
    def _generate_welcome_response(self, lead_name: str) -> str:
        """Gera mensagem de boas-vindas HIPER PERSONALIZADA"""
        import random
        
        saudacoes = ["Olá", "Oi", "Olá", "Oi", "E aí"]
        emojis = ["👋", "😊", "👍", "💪", "✨"]
        
        saudacao = random.choice(saudacoes)
        emoji = random.choice(emojis)
        
        return f"""{saudacao} {lead_name}! {emoji}

Sou o assistente virtual da *HealthPlatform*! 

Fico *muito feliz* pelo seu interesse em planos de saúde! 🏥

📞 *Um dos nossos corretores especializados entrará em contato em breve* para te apresentar as melhores opções do mercado.

💡 *Enquanto isso, me conta:*
• Está buscando plano *empresarial* (PME)? 
• Plano *individual ou familiar* (PF)?
• Ou quer saber sobre *adesão*?

É só responder aqui mesmo! Vou te ajudar a encontrar a melhor solução! 😄

_*Equipe HealthPlatform*_"""
    
    async def send_message(self, phone: str, message: str) -> bool:
        """Envia mensagem via WhatsApp - SIMULAÇÃO ROBUSTA"""
        try:
            print(f"📤 ENVIANDO MENSAGEM PARA {phone}")
            print(f"💌 Conteúdo: {message}")
            
            # SIMULAÇÃO DE ENVIO - SUBSTITUIR PELA API REAL
            # from .whatsapp_api import WhatsAppAPI
            # api = WhatsAppAPI()
            # result = await api.send_message(phone, message)
            
            # Simulação de delay de envio
            import asyncio
            await asyncio.sleep(1)
            
            print("✅ MENSAGEM ENVIADA COM SUCESSO (SIMULAÇÃO)")
            return True
            
        except Exception as e:
            print(f"❌ ERRO NO ENVIO: {e}")
            return False
    
    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """Verifica webhook do WhatsApp"""
        if mode == "subscribe" and token == "meu_token_secreto":
            print("✅ WEBHOOK WHATSAPP VERIFICADO!")
            return challenge
        return None