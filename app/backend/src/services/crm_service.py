# app/backend/src/services/crm_service.py
from sqlalchemy.orm import Session
from typing import Dict, Optional, List
import re
from datetime import datetime

class CRMService:
    def __init__(self, db: Session):
        self.db = db
    
    def extract_name_from_message(self, message: str) -> str:
        """Tenta extrair nome da mensagem usando regex - MELHORADO"""
        if not message or len(message.strip()) < 3:
            return "Lead WhatsApp"
            
        message_lower = message.lower().strip()
        
        # Padrões mais inteligentes para extrair nome
        patterns = [
            r"(?:meu nome é|sou o|sou a|me chamo|eu sou)\s+([a-zà-ÿ\s]{2,})",
            r"(?:oi|olá|ola|oie|opa),\s*([a-zà-ÿ\s]{2,})",
            r"^([a-zà-ÿ\s]{2,})\s+(?:aqui|falando|ao telefone|sou eu)",
            r"(?:aqu[ií]\s+)([a-zà-ÿ\s]{2,})",
            r"(?:é\s+)([a-zà-ÿ\s]{2,})",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message_lower, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Validar se é um nome plausível
                if len(name) >= 2 and not any(word in name for word in ['quero', 'gostaria', 'planos', 'saude']):
                    return name.title()
        
        # Se não encontrou nome, tenta pegar primeira palavra se for nome próprio
        first_word = message.split()[0] if message.split() else ""
        if first_word and first_word[0].isupper() and len(first_word) > 2:
            return first_word
        
        return "Lead WhatsApp"
    
    def phone_exists(self, phone: str) -> Optional[int]:
        """Verifica se phone já existe como lead e retorna ID"""
        from app.backend.src.models.lead import Lead
        
        existing_lead = self.db.query(Lead).filter(Lead.phone == phone).first()
        return existing_lead.id if existing_lead else None
    
    def create_whatsapp_lead(self, phone: str, message: str) -> Dict:
        """Cria lead automaticamente do WhatsApp - ROBUSTO"""
        from app.backend.src.models.lead import Lead
        from app.backend.src.models.lead_conversation import LeadConversation
        
        try:
            print(f"🔍 Criando lead para {phone}...")
            
            # Verificar se lead já existe
            existing_lead_id = self.phone_exists(phone)
            if existing_lead_id:
                print(f"⚠️ Lead já existe: ID {existing_lead_id}")
                
                # Atualizar conversa do lead existente
                conversation = LeadConversation(
                    lead_id=existing_lead_id,
                    message=message,
                    direction="incoming",
                    message_type="text"
                )
                self.db.add(conversation)
                self.db.commit()
                
                return {
                    "success": True, 
                    "lead_id": existing_lead_id,
                    "action": "updated",
                    "message": "Lead existente atualizado"
                }
            
            # Extrair nome da mensagem
            name = self.extract_name_from_message(message)
            print(f"📝 Nome extraído: {name}")
            
            # Criar novo lead
            new_lead = Lead(
                full_name=name,
                phone=phone,
                email=None,
                source="whatsapp",
                status="novo_contato",
                broker_id=None,
                notes=f"Lead criado automaticamente via WhatsApp em {datetime.now().strftime('%d/%m/%Y %H:%M')}. Mensagem: {message[:200]}...",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.db.add(new_lead)
            self.db.flush()  # Para obter o ID sem commit
            
            # Criar primeira conversa
            conversation = LeadConversation(
                lead_id=new_lead.id,
                message=message,
                direction="incoming",
                message_type="text",
                created_at=datetime.now()
            )
            self.db.add(conversation)
            
            self.db.commit()
            self.db.refresh(new_lead)
            
            print(f"✅ NOVO LEAD CRIADO: ID {new_lead.id} - {name}")
            
            return {
                "success": True, 
                "lead_id": new_lead.id,
                "lead_name": name,
                "action": "created",
                "message": "Novo lead criado com sucesso"
            }
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ ERRO AO CRIAR LEAD: {e}")
            return {"success": False, "error": str(e)}
    
    def update_lead_conversation(self, lead_id: int, message: str, direction: str = "outgoing") -> Dict:
        """Atualiza histórico de conversa do lead"""
        from app.backend.src.models.lead_conversation import LeadConversation
        
        try:
            conversation = LeadConversation(
                lead_id=lead_id,
                message=message,
                direction=direction,
                message_type="text",
                created_at=datetime.now()
            )
            
            self.db.add(conversation)
            self.db.commit()
            
            print(f"💬 Conversa salva: Lead {lead_id} - {direction}")
            
            return {"success": True}
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ ERRO AO SALVAR CONVERSA: {e}")
            return {"success": False, "error": str(e)}
    
    def get_lead_by_phone(self, phone: str):
        """Busca lead pelo telefone"""
        from app.backend.src.models.lead import Lead
        
        return self.db.query(Lead).filter(Lead.phone == phone).first()