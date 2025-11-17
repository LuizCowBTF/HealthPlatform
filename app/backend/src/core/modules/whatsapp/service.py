# app/backend/src/modules/whatsapp/service.py
import requests
from typing import Dict, Optional

class WhatsAppService:
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://graph.facebook.com/v17.0"
    
    async def send_message(self, phone: str, message: str, template: Optional[str] = None) -> bool:
        """Envia mensagem via WhatsApp Business API"""
        try:
            url = f"{self.base_url}/YOUR_PHONE_NUMBER_ID/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": phone,
                "type": "text",
                "text": {"body": message}
            }
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Erro ao enviar mensagem WhatsApp: {e}")
            return False
    
    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """Verifica webhook do WhatsApp"""
        if mode == "subscribe" and token == "meu_token_secreto":
            return challenge
        return None
    
    async def process_incoming_message(self, data: Dict) -> Dict:
        """Processa mensagem recebida"""
        message = data.get('entry', [{}])[0].get('changes', [{}])[0].get('value', {})
        
        if 'messages' in message:
            message_data = message['messages'][0]
            phone = message_data['from']
            text = message_data.get('text', {}).get('body', '')
            
            return {
                "phone": phone,
                "message": text,
                "type": "incoming",
                "timestamp": message_data['timestamp']
            }
        
        return {}