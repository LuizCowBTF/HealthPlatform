# app/backend/src/core/services/orchestration_service.py
from app.backend.src.modules.whatsapp.service import WhatsAppService
from app.backend.src.modules.crm.service import CRMService
from app.backend.src.core.modules.ai.health_ia import health_ia
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class OrchestrationService:
    def __init__(self):
        self.whatsapp = WhatsAppService()
        self.crm = CRMService()
        self.ia = health_ia
    
    async def processar_mensagem_whatsapp(self, dados_mensagem: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orquestra o fluxo completo:
        1. Identifica lead no CRM
        2. IA analisa e qualifica
        3. Gera resposta personalizada
        4. Atualiza estágio no funil
        """
        try:
            logger.info("🔄 INICIANDO ORQUESTRAÇÃO - Mensagem WhatsApp")
            
            # 1. EXTRAIR DADOS DA MENSAGEM
            telefone = dados_mensagem.get('from')
            mensagem_texto = dados_mensagem.get('text', '')
            nome_cliente = dados_mensagem.get('profile_name', 'Cliente')
            
            logger.info(f"📱 Mensagem de {telefone}: {mensagem_texto[:50]}...")
            
            # 2. IDENTIFICAR OU CRIAR LEAD NO CRM
            lead = await self._sincronizar_lead_crm(
                telefone=telefone,
                nome=nome_cliente,
                mensagem=mensagem_texto
            )
            
            # 3. IA ANALISAR MENSAGEM E QUALIFICAR
            perfil_ia = await self._analisar_mensagem_ia(
                mensagem=mensagem_texto,
                lead_existente=lead
            )
            
            # 4. GERAR RESPOSTA AUTOMÁTICA INTELIGENTE
            resposta = await self._gerar_resposta_automatica(
                mensagem_original=mensagem_texto,
                perfil_ia=perfil_ia,
                lead=lead
            )
            
            # 5. ATUALIZAR ESTÁGIO NO FUNIL
            await self._atualizar_funil_crm(lead, perfil_ia)
            
            logger.info("✅ ORQUESTRAÇÃO CONCLUÍDA")
            
            return {
                "success": True,
                "resposta": resposta,
                "lead_id": lead.get('id'),
                "estagio_funil": perfil_ia.get('estagio_sugerido'),
                "plano_sugerido": perfil_ia.get('plano_sugerido')
            }
            
        except Exception as e:
            logger.error(f"❌ ERRO NA ORQUESTRAÇÃO: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "resposta": "Olá! Obrigado pelo contato. Em breve nosso time retornará. 📞"
            }
    
    async def _sincronizar_lead_crm(self, telefone: str, nome: str, mensagem: str) -> Dict[str, Any]:
        """Identifica ou cria lead no CRM"""
        logger.info(f"🔍 Sincronizando lead: {nome} ({telefone})")
        
        # Verificar se lead já existe
        lead_existente = await self.crm.buscar_lead_por_telefone(telefone)
        
        if lead_existente:
            logger.info(f"✅ Lead encontrado: {lead_existente.get('id')}")
            # Atualizar última mensagem
            return await self.crm.atualizar_lead(
                lead_id=lead_existente['id'],
                ultima_mensagem=mensagem
            )
        else:
            # Criar novo lead
            logger.info(f"🆕 Criando novo lead para {nome}")
            return await self.crm.criar_lead({
                "nome": nome,
                "telefone": telefone,
                "ultima_mensagem": mensagem,
                "fonte": "whatsapp",
                "estagio": "contato_inicial"
            })
    
    async def _analisar_mensagem_ia(self, mensagem: str, lead_existente: Dict) -> Dict[str, Any]:
        """IA analisa mensagem e qualifica lead"""
        logger.info("🧠 IA analisando mensagem...")
        
        # Análise de intenção baseada em palavras-chave
        mensagem_lower = mensagem.lower()
        
        if any(palavra in mensagem_lower for palavra in ['preço', 'custo', 'valor', 'quanto']):
            estagio = "interesse_preco"
            plano_sugerido = self.ia.analisar_perfil_cliente(lead_existente)['plano_sugerido']
        
        elif any(palavra in mensagem_lower for palavra in ['plano', 'cobertura', 'consultas', 'exames']):
            estagio = "interesse_planos"
            plano_sugerido = self.ia.analisar_perfil_cliente(lead_existente)['plano_sugerido']
        
        elif any(palavra in mensagem_lower for palavra in ['oi', 'olá', 'bom dia', 'boa tarde']):
            estagio = "contato_inicial"
            plano_sugerido = None
        else:
            estagio = "qualificacao"
            plano_sugerido = None
        
        return {
            "estagio_sugerido": estagio,
            "plano_sugerido": plano_sugerido,
            "urgencia": "alta" if any(palavra in mensagem_lower for palavra in ['urgente', 'emergencia', 'imediat']) else "normal"
        }
    
    async def _gerar_resposta_automatica(self, mensagem_original: str, perfil_ia: Dict, lead: Dict) -> str:
        """Gera resposta automática contextual"""
        estagio = perfil_ia.get('estagio_sugerido')
        plano_sugerido = perfil_ia.get('plano_sugerido')
        
        logger.info(f"💬 Gerando resposta para estágio: {estagio}")
        
        respostas = {
            "contato_inicial": f"""
👋 Olá {lead.get('nome', '')}! 

Sou seu assistente virtual da Health Platform! 

Como posso ajudar você hoje? 

📋 Posso explicar nossos planos de saúde
💰 Dar uma estimativa de valores  
🎯 Indicar o plano ideal para seu perfil

Qual sua necessidade? 😊
            """,
            
            "interesse_preco": f"""
💡 Ótima pergunta sobre valores!

Para te dar uma estimativa precisa, preciso conhecer melhor seu perfil.

Nosso sistema indica que o plano *{plano_sugerido}* pode ser ideal para você, com preços entre R$ {self.ia.planos_disponiveis[plano_sugerido]['faixa_preco'][0]} e R$ {self.ia.planos_disponiveis[plano_sugerido]['faixa_preco'][1]} mensais.

Posso te explicar melhor as coberturas? 📞
            """,
            
            "interesse_planos": f"""
🎯 Excelente! Vamos falar sobre planos!

Recomendo o plano *{plano_sugerido}* para seu perfil, que inclui:

{chr(10).join(['• ' + item for item in self.ia.planos_disponiveis[plano_sugerido]['cobertura'][:3]])}

Quer que eu detalhe cada cobertura? 😊
            """,
            
            "qualificacao": """
🤔 Entendi sua mensagem!

Para te ajudar da melhor forma, poderia me contar:

• Quantas pessoas precisam de cobertura?
• Qual faixa de idade?
• Alguma necessidade específica de saúde?

Assim posso indicar o plano perfeito! 💎
            """
        }
        
        return respostas.get(estagio, respostas["contato_inicial"]).strip()
    
    async def _atualizar_funil_crm(self, lead: Dict, perfil_ia: Dict):
        """Atualiza estágio do lead no funil do CRM"""
        try:
            await self.crm.atualizar_estagio_lead(
                lead_id=lead['id'],
                novo_estagio=perfil_ia['estagio_sugerido'],
                plano_sugerido=perfil_ia.get('plano_sugerido')
            )
            logger.info(f"📊 Funil atualizado: {lead['id']} → {perfil_ia['estagio_sugerido']}")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao atualizar funil: {str(e)}")

# Instância global do serviço de orquestração
orchestration_service = OrchestrationService()