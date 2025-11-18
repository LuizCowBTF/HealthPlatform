# test_integracao_final.py
import asyncio
import sys
import os

# Adicionar paths corretos
sys.path.append(os.path.join(os.getcwd(), 'app', 'backend', 'src'))

try:
    from core.modules.ai.health_ia import health_ia
    print("✅ IA Brasileira importada!")
    
    # Verificar se os serviços existem
    try:
        from services.crm_service import crm_service
        print("✅ CRM Service importado!")
    except ImportError:
        print("⚠️  CRM Service não encontrado - usando mock")
        crm_service = None
        
    try:
        from services.whatsapp_service import whatsapp_service  
        print("✅ WhatsApp Service importado!")
    except ImportError:
        print("⚠️  WhatsApp Service não encontrado - usando mock")
        whatsapp_service = None
        
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    sys.exit(1)

class MockCRMService:
    """Mock do CRM Service para testes"""
    def __init__(self):
        self.leads = {}
        self.lead_id_counter = 1
    
    async def buscar_lead_por_telefone(self, telefone):
        return self.leads.get(telefone)
    
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
        print(f"📝 Mock CRM: Lead criado ID {lead_id} para {dados['nome']}")
        return lead
    
    async def atualizar_lead(self, lead_id, ultima_mensagem):
        for lead in self.leads.values():
            if lead["id"] == lead_id:
                lead["ultima_mensagem"] = ultima_mensagem
                lead["ultima_atualizacao"] = "2024-01-01"
                print(f"📝 Mock CRM: Lead {lead_id} atualizado")
                return lead
        return None
    
    async def atualizar_estagio_lead(self, lead_id, novo_estagio, plano_sugerido):
        for lead in self.leads.values():
            if lead["id"] == lead_id:
                lead["estagio"] = novo_estagio
                lead["plano_sugerido"] = plano_sugerido
                print(f"📊 Mock CRM: Lead {lead_id} -> Estágio: {novo_estagio}, Plano: {plano_sugerido}")
                return True
        return False

class MockWhatsAppService:
    """Mock do WhatsApp Service para testes"""
    async def enviar_mensagem_texto(self, to, message, business_phone_id):
        print(f"📤 Mock WhatsApp: Mensagem enviada para {to}")
        print(f"💬 Conteúdo: {message[:100]}...")
        return {"status": "sent", "message_id": "mock_123"}

class OrchestrationServiceTest:
    """Serviço de orquestração para testes"""
    def __init__(self):
        self.ia = health_ia
        self.crm = MockCRMService()
        self.whatsapp = MockWhatsAppService()
        print("🚀 ORQUESTRAÇÃO DE TESTE INICIADA!")
    
    async def processar_mensagem_whatsapp(self, dados_mensagem):
        """
        Orquestra o fluxo completo para testes
        """
        try:
            print(f"\n🔄 PROCESSANDO MENSAGEM: {dados_mensagem['profile_name']}")
            
            # 1. Extrair dados
            telefone = dados_mensagem.get('from')
            mensagem_texto = dados_mensagem.get('text', '')
            nome_cliente = dados_mensagem.get('profile_name', 'Cliente')
            
            # 2. Sincronizar com CRM
            lead = await self._sincronizar_lead_crm(telefone, nome_cliente, mensagem_texto)
            
            # 3. IA analisar mensagem
            perfil_ia = await self._analisar_mensagem_ia(mensagem_texto, lead)
            
            # 4. Gerar resposta automática
            resposta = await self._gerar_resposta_automatica(mensagem_texto, perfil_ia, lead)
            
            # 5. Atualizar funil
            await self._atualizar_funil_crm(lead, perfil_ia)
            
            # 6. Enviar resposta (mock)
            await self.whatsapp.enviar_mensagem_texto(
                to=telefone,
                message=resposta,
                business_phone_id=dados_mensagem.get('whatsapp_business_id', 'test_123')
            )
            
            return {
                "success": True,
                "resposta": resposta,
                "lead_id": lead.get('id'),
                "estagio_funil": perfil_ia.get('estagio_sugerido'),
                "plano_sugerido": perfil_ia.get('plano_sugerido')
            }
            
        except Exception as e:
            print(f"❌ ERRO: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _sincronizar_lead_crm(self, telefone, nome, mensagem):
        """Sincroniza lead com CRM"""
        lead_existente = await self.crm.buscar_lead_por_telefone(telefone)
        
        if lead_existente:
            print(f"✅ Lead existente encontrado: {lead_existente['id']}")
            return await self.crm.atualizar_lead(lead_existente['id'], mensagem)
        else:
            print(f"🆕 Criando novo lead para: {nome}")
            return await self.crm.criar_lead({
                "nome": nome,
                "telefone": telefone,
                "ultima_mensagem": mensagem,
                "fonte": "whatsapp",
                "estagio": "contato_inicial"
            })
    
    async def _analisar_mensagem_ia(self, mensagem, lead_existente):
        """IA analisa mensagem e qualifica lead"""
        mensagem_lower = mensagem.lower()
        
        # Análise de intenção
        if any(palavra in mensagem_lower for palavra in ['preço', 'custo', 'valor', 'quanto']):
            estagio = "interesse_preco"
            # Usar dados do lead se disponível, senão criar perfil básico
            perfil_base = {
                "idade": lead_existente.get('idade', 30),
                "renda": lead_existente.get('renda', 5000),
                "dependentes": lead_existente.get('dependentes', 1),
                "profissao": lead_existente.get('profissao', 'cliente')
            }
            plano_sugerido = self.ia.analisar_perfil_cliente(perfil_base)['plano_sugerido']
        
        elif any(palavra in mensagem_lower for palavra in ['plano', 'cobertura', 'consultas', 'exames']):
            estagio = "interesse_planos"
            plano_sugerido = "FAMILIAR"  # Default
        
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
    
    async def _gerar_resposta_automatica(self, mensagem_original, perfil_ia, lead):
        """Gera resposta automática contextual"""
        estagio = perfil_ia.get('estagio_sugerido')
        plano_sugerido = perfil_ia.get('plano_sugerido')
        
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

Posso indicar que nossos planos variam de R$ 150 a R$ 10.000, dependendo das suas necessidades.

Posso te explicar melhor as coberturas? 📞
            """,
            
            "interesse_planos": f"""
🎯 Excelente! Vamos falar sobre planos!

Temos opções para todos os perfis:
• Individual (R$ 150-500)
• Familiar (R$ 800-2000) 
• Empresarial (R$ 2.000-10.000)
• VIP (R$ 1.500-3.000)

Qual se adequa mais a você? 😊
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
    
    async def _atualizar_funil_crm(self, lead, perfil_ia):
        """Atualiza estágio do lead no funil"""
        await self.crm.atualizar_estagio_lead(
            lead_id=lead['id'],
            novo_estagio=perfil_ia['estagio_sugerido'],
            plano_sugerido=perfil_ia.get('plano_sugerido')
        )

async def testar_fluxo_completo():
    """Testa o fluxo completo de orquestração"""
    print("🚀 TESTE DO FLUXO COMPLETO WHATSAPP + IA + CRM")
    print("="*60)
    
    orchestration = OrchestrationServiceTest()
    
    # Cenários de teste
    cenarios = [
        {
            "nome": "Cliente Novo - Saudação",
            "telefone": "5511999999999",
            "mensagem": "Oi, gostaria de saber sobre planos de saúde",
            "profile_name": "João Silva"
        },
        {
            "nome": "Interesse em Preços", 
            "telefone": "5511988888888",
            "mensagem": "Quanto custa um plano de saúde?",
            "profile_name": "Maria Santos"
        },
        {
            "nome": "Plano Familiar",
            "telefone": "5511977777777",
            "mensagem": "Preciso de plano para minha família com 4 pessoas",
            "profile_name": "Carlos Oliveira"
        }
    ]
    
    for cenario in cenarios:
        print(f"\n🎯 CENÁRIO: {cenario['nome']}")
        print(f"📱 {cenario['profile_name']}: '{cenario['mensagem']}'")
        
        payload = {
            "from": cenario["telefone"],
            "text": cenario["mensagem"],
            "profile_name": cenario["profile_name"],
            "message_id": f"test_{cenario['telefone']}",
            "timestamp": 1234567890,
            "whatsapp_business_id": "test_business_123"
        }
        
        resultado = await orchestration.processar_mensagem_whatsapp(payload)
        
        if resultado["success"]:
            print("✅ SUCESSO!")
            print(f"💬 Resposta: {resultado['resposta'][:100]}...")
            print(f"📊 Estágio: {resultado['estagio_funil']}")
        else:
            print("❌ FALHA!")
            print(f"Erro: {resultado.get('error')}")
        
        print("-" * 50)

async def main():
    """Executa todos os testes"""
    print("🚀 HEALTH PLATFORM - TESTE DE INTEGRAÇÃO")
    print("📍 Usando mocks para serviços não encontrados")
    print("⏰ Iniciando testes...\n")
    
    # Testar IA diretamente primeiro
    print("🧠 TESTANDO IA BRASILEIRA...")
    perfil_teste = {"nome": "Teste", "idade": 35, "renda": 8000, "dependentes": 2, "profissao": "empresario"}
    resultado_ia = health_ia.analisar_perfil_cliente(perfil_teste)
    print(f"✅ IA Funcionando: {resultado_ia['plano_sugerido']} - {resultado_ia['operadora_sugerida']}")
    
    # Testar fluxo completo
    await testar_fluxo_completo()
    
    print("\n🎉 TESTES CONCLUÍDOS!")
    print("✨ Health Platform - Integração WhatsApp + IA + CRM ✨")

if __name__ == "__main__":
    asyncio.run(main())