# app/backend/src/core/modules/whatsapp/service.py - ATUALIZADO
import requests
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v17.0"
        self.access_token = "SEU_TOKEN_AQUI"  # Configurar via settings
        
    async def enviar_mensagem_texto(self, to: str, message: str, business_phone_id: str) -> Dict:
        """Envia mensagem de texto via WhatsApp Business API"""
        try:
            url = f"{self.base_url}/{business_phone_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "text": {"body": message},
                "context": {
                    "message_id": "context_info"  # Para replies
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            logger.info(f"✅ Mensagem enviada para {to}")
            return response.json()
            
        except Exception as e:
            logger.error(f"❌ Erro enviando mensagem WhatsApp: {str(e)}")
            raise
    
    async def enviar_template_mensagem(self, to: str, template_name: str, business_phone_id: str, parameters: Dict = None) -> Dict:
        """Envia mensagem de template"""
        try:
            url = f"{self.base_url}/{business_phone_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {"code": "pt_BR"}
                }
            }
            
            if parameters:
                payload["template"]["components"] = [
                    {
                        "type": "body",
                        "parameters": parameters
                    }
                ]
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"❌ Erro enviando template: {str(e)}")
            raise
    
    async def marcar_mensagem_como_lida(self, message_id: str, business_phone_id: str) -> Dict:
        """Marca mensagem como lida"""
        try:
            url = f"{self.base_url}/{business_phone_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id
            }
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"❌ Erro marcando como lida: {str(e)}")
            raise

# Instância global
whatsapp_service = WhatsAppService()