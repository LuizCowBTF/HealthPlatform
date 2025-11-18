# app/backend/src/core/services/orchestration_service.py
# 🎯 VERSÃO FINAL COM DATABASE INTEGRATION
import asyncio
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class OrchestrationService:
    def __init__(self, db_session=None):
        """
        Inicializa com sessão do banco de dados
        db_session: Sessão do SQLAlchemy (opcional)
        """
        self.db = db_session
        logger.info("🎯 ORQUESTRAÇÃO INICIADA" + (" COM DATABASE" if db_session else " SEM DATABASE"))
        
        # 🧠 IA Brasileira
        try:
            from app.backend.src.core.modules.ai.health_ia import health_ia
            self.ia = health_ia
            logger.info("✅ IA Brasileira carregada")
        except ImportError as e:
            logger.error(f"❌ Erro ao carregar IA: {e}")
            self.ia = None
        
        # 📊 CRM Service REAL com Database
        try:
            from app.backend.src.services.crm_service import CRMService
            if db_session:
                self.crm = CRMService(db_session)
                logger.info("✅ CRM Service REAL com database")
            else:
                self.crm = self._criar_crm_mock()
                logger.info("✅ CRM Service MOCK (sem database)")
        except ImportError as e:
            logger.error(f"❌ Erro ao carregar CRM Service: {e}")
            self.crm = self._criar_crm_mock()
        
        # 📱 WhatsApp Service REAL com Database
        try:
            from app.backend.src.services.whatsapp_service import WhatsAppService
            if db_session:
                self.whatsapp = WhatsAppService(db_session)
                logger.info("✅ WhatsApp Service REAL com database")
            else:
                self.whatsapp = self._criar_whatsapp_mock()
                logger.info("✅ WhatsApp Service MOCK (sem database)")
        except ImportError as e:
            logger.error(f"❌ Erro ao carregar WhatsApp Service: {e}")
            self.whatsapp = self._criar_whatsapp_mock()
    
    def _criar_crm_mock(self):
        """Mock do CRM para desenvolvimento"""
        class MockCRM:
            def __init__(self):
                self.leads = {}
                self.lead_id_counter = 1
                logger.info("📝 Mock CRM criado para testes")
            
            async def buscar_lead_por_telefone(self, telefone):
                lead = self.leads.get(telefone)
                if lead:
                    logger.info(f"🔍 Mock CRM: Lead encontrado {lead['id']}")
                return lead
            
            async def criar_lead(self, dados):
                lead_id = self.lead_id_counter
                self.lead_id_counter += 1
                lead = {
                    "id": lead_id,
                    **dados,
                    "data_criacao": "2024-01-01",
                    "ultima_atualizacao": "2024-01-01"
                }
                self.leads[dados["telefone"]] = lead
                logger.info(f"📝 Mock CRM: Lead criado ID {lead_id} - {dados['nome']}")
                return lead
            
            async def atualizar_lead(self, lead_id, ultima_mensagem):
                for lead in self.leads.values():
                    if lead["id"] == lead_id:
                        lead["ultima_mensagem"] = ultima_mensagem
                        lead["ultima_atualizacao"] = "2024-01-01"
                        logger.info(f"📝 Mock CRM: Lead {lead_id} atualizado")
                        return lead
                return None
            
            async def atualizar_estagio_lead(self, lead_id, novo_estagio, plano_sugerido):
                for lead in self.leads.values():
                    if lead["id"] == lead_id:
                        lead["estagio"] = novo_estagio
                        lead["plano_sugerido"] = plano_sugerido
                        logger.info(f"📊 Mock CRM: Lead {lead_id} -> {novo_estagio}")
                        return True
                return False
        
        return MockCRM()
    
    def _criar_whatsapp_mock(self):
        """Mock do WhatsApp para desenvolvimento"""
        class MockWhatsApp:
            def __init__(self):
                logger.info("📱 Mock WhatsApp criado para testes")
            
            async def enviar_mensagem_texto(self, to, message, business_phone_id):
                logger.info(f"📤 Mock WhatsApp: Mensagem para {to}")
                logger.info(f"💬 Conteúdo: {message[:100]}...")
                return {
                    "status": "sent", 
                    "message_id": f"mock_{to}",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
        
        return MockWhatsApp()
    
    async def processar_mensagem_whatsapp(self, dados_mensagem: Dict[str, Any]) -> Dict[str, Any]:
        """
        🎯 ORQUESTRAÇÃO FINAL: WhatsApp → IA → CRM → Resposta
        """
        try:
            logger.info("🔄 INICIANDO ORQUESTRAÇÃO...")
            
            telefone = dados_mensagem.get('from')
            mensagem_texto = dados_mensagem.get('text', '')
            nome_cliente = dados_mensagem.get('profile_name', 'Cliente')
            
            logger.info(f"📱 Mensagem de {nome_cliente} ({telefone}): {mensagem_texto[:50]}...")
            
            # 1. 📊 SINCRONIZAR CRM
            lead = await self._sincronizar_lead_crm(telefone, nome_cliente, mensagem_texto)
            
            # 2. 🧠 ANALISAR COM IA
            perfil_ia = await self._analisar_mensagem_ia(mensagem_texto, lead)
            
            # 3. 💬 GERAR RESPOSTA
            resposta = await self._gerar_resposta_automatica(mensagem_texto, perfil_ia, lead)
            
            # 4. 📈 ATUALIZAR FUNIL
            await self._atualizar_funil_crm(lead, perfil_ia)
            
            # 5. 📱 ENVIAR VIA WHATSAPP
            resultado_envio = await self.whatsapp.enviar_mensagem_texto(
                to=telefone,
                message=resposta,
                business_phone_id=dados_mensagem.get('whatsapp_business_id', 'default_business')
            )
            
            logger.info("✅ ORQUESTRAÇÃO CONCLUÍDA COM SUCESSO!")
            
            return {
                "success": True,
                "resposta": resposta,
                "lead_id": lead.get('id'),
                "estagio_funil": perfil_ia.get('estagio_sugerido'),
                "plano_sugerido": perfil_ia.get('plano_sugerido'),
                "whatsapp_status": resultado_envio.get('status'),
                "servico_crm": "REAL" if hasattr(self.crm, '__module__') and 'mock' not in str(self.crm.__class__).lower() else "MOCK",
                "servico_whatsapp": "REAL" if hasattr(self.whatsapp, '__module__') and 'mock' not in str(self.whatsapp.__class__).lower() else "MOCK"
            }
            
        except Exception as e:
            logger.error(f"❌ ERRO NA ORQUESTRAÇÃO: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "resposta": "Olá! Obrigado pelo contato. Em breve retornaremos. 📞"
            }
    
    async def _sincronizar_lead_crm(self, telefone: str, nome: str, mensagem: str) -> Dict[str, Any]:
        """Sincroniza lead com CRM (real ou mock)"""
        logger.info(f"🔍 Sincronizando lead: {nome}")
        
        lead_existente = await self.crm.buscar_lead_por_telefone(telefone)
        
        if lead_existente:
            logger.info(f"✅ Lead existente: {lead_existente.get('id')}")
            return await self.crm.atualizar_lead(lead_existente['id'], mensagem)
        else:
            logger.info(f"🆕 Criando novo lead: {nome}")
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
        
        if not self.ia:
            return {"estagio_sugerido": "contato_inicial", "plano_sugerido": None}
        
        mensagem_lower = mensagem.lower()
        
        # Análise de intenção
        if any(palavra in mensagem_lower for palavra in ['preço', 'custo', 'valor', 'quanto']):
            estagio = "interesse_preco"
            perfil_base = {
                "idade": lead_existente.get('idade', 30),
                "renda": lead_existente.get('renda', 5000),
                "dependentes": lead_existente.get('dependentes', 1),
                "profissao": lead_existente.get('profissao', 'cliente')
            }
            try:
                analise_ia = self.ia.analisar_perfil_cliente(perfil_base)
                plano_sugerido = analise_ia['plano_sugerido']
                logger.info(f"🎯 IA sugeriu: {plano_sugerido}")
            except Exception as e:
                logger.error(f"❌ Erro na IA: {e}")
                plano_sugerido = "FAMILIAR"
        
        elif any(palavra in mensagem_lower for palavra in ['plano', 'cobertura', 'consultas', 'exames']):
            estagio = "interesse_planos"
            plano_sugerido = "FAMILIAR"
        
        elif any(palavra in mensagem_lower for palavra in ['oi', 'olá', 'bom dia', 'boa tarde']):
            estagio = "contato_inicial"
            plano_sugerido = None
        else:
            estagio = "qualificacao"
            plano_sugerido = None
        
        return {
            "estagio_sugerido": estagio,
            "plano_sugerido": plano_sugerido
        }
    
    async def _gerar_resposta_automatica(self, mensagem_original: str, perfil_ia: Dict, lead: Dict) -> str:
        """Gera resposta automática contextual"""
        estagio = perfil_ia.get('estagio_sugerido')
        
        respostas = {
            "contato_inicial": f"""
👋 Olá {lead.get('nome', '')}! 

Sou seu assistente virtual da Health Platform! 

Como posso ajudar você hoje? 😊
            """,
            
            "interesse_preco": f"""
💡 Ótima pergunta sobre valores, {lead.get('nome', '')}!

Para te dar uma estimativa precisa, preciso conhecer melhor seu perfil.

Posso te explicar melhor as coberturas? 📞
            """,
            
            "interesse_planos": f"""
🎯 Excelente, {lead.get('nome', '')}! Vamos falar sobre planos!

Temos opções para todos os perfis. Qual se adequa mais a você? 😊
            """,
            
            "qualificacao": f"""
🤔 Entendi sua mensagem, {lead.get('nome', '')}!

Para te ajudar da melhor forma, poderia me contar mais sobre suas necessidades? 💎
            """
        }
        
        return respostas.get(estagio, respostas["contato_inicial"]).strip()
    
    async def _atualizar_funil_crm(self, lead: Dict, perfil_ia: Dict):
        """Atualiza estágio do lead no funil"""
        try:
            if hasattr(self.crm, 'atualizar_estagio_lead'):
                await self.crm.atualizar_estagio_lead(
                    lead_id=lead['id'],
                    novo_estagio=perfil_ia['estagio_sugerido'],
                    plano_sugerido=perfil_ia.get('plano_sugerido')
                )
                logger.info(f"📊 Funil atualizado: {perfil_ia['estagio_sugerido']}")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao atualizar funil: {str(e)}")

# 🎯 INSTÂNCIA GLOBAL PARA DESENVOLVIMENTO (SEM DATABASE)
orchestration_service = OrchestrationService()

# 🎯 PARA PRODUÇÃO: usar OrchestrationService(db_session) com database real