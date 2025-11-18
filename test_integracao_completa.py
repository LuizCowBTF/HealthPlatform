# test_integracao_completa.py
import asyncio
import requests
import json
from app.backend.src.core.services.orchestration_service import orchestration_service

class TesteIntegracaoCompleta:
    def __init__(self):
        self.base_url = "http://localhost:8000"
    
    async def testar_fluxo_completo(self):
        """Testa todo o fluxo: WhatsApp → IA → CRM → Resposta"""
        print("🧪 INICIANDO TESTE DO FLUXO COMPLETO")
        print("=" * 60)
        
        # Simular diferentes cenários de mensagens
        cenarios = [
            {
                "nome": "Cliente Novo - Saudação",
                "mensagem": "Oi, gostaria de saber sobre planos de saúde",
                "telefone": "5511999999999"
            },
            {
                "nome": "Interesse em Preços", 
                "mensagem": "Quanto custa um plano de saúde?",
                "telefone": "5511988888888"
            },
            {
                "nome": "Plano Familiar",
                "mensagem": "Preciso de plano para minha família com 4 pessoas",
                "telefone": "5511977777777"
            },
            {
                "nome": "Urgência",
                "mensagem": "Preciso urgente de um plano de saúde!",
                "telefone": "5511966666666"
            }
        ]
        
        for cenario in cenarios:
            print(f"\n🎯 TESTANDO: {cenario['nome']}")
            print(f"📱 Mensagem: '{cenario['mensagem']}'")
            
            resultado = await self.executar_cenario(cenario)
            
            if resultado["success"]:
                print("✅ SUCESSO!")
                print(f"💬 Resposta: {resultado['resposta'][:100]}...")
                print(f"👤 Lead ID: {resultado['lead_id']}")
                print(f"📊 Estágio: {resultado['estagio_funil']}")
                print(f"🎯 Plano Sugerido: {resultado['plano_sugerido']}")
            else:
                print("❌ FALHA!")
                print(f"Erro: {resultado['error']}")
            
            print("-" * 50)
            await asyncio.sleep(1)  # Delay entre testes
    
    async def executar_cenario(self, cenario):
        """Executa um cenário de teste específico"""
        
        # Simular payload do webhook do WhatsApp
        payload_webhook = {
            "from": cenario["telefone"],
            "text": cenario["mensagem"],
            "profile_name": cenario["nome"].split(" - ")[0],
            "message_id": f"test_{cenario['telefone']}",
            "timestamp": 1234567890,
            "whatsapp_business_id": "test_business_123"
        }
        
        try:
            # Chamar diretamente a orquestração (simulando webhook)
            resultado = await orchestration_service.processar_mensagem_whatsapp(payload_webhook)
            return resultado
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def testar_endpoints_api(self):
        """Testa endpoints individuais da API"""
        print("\n🔍 TESTANDO ENDPOINTS DA API")
        print("=" * 40)
        
        endpoints = [
            "/api/v1/ia/analisar-perfil",
            "/api/v1/ia/gerar-script-venda", 
            "/api/v1/crm/leads",
            "/api/v1/whatsapp/webhook"
        ]
        
        for endpoint in endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                
                if "analisar-perfil" in endpoint:
                    payload = {
                        "nome": "João Silva",
                        "idade": 35,
                        "renda": 8000,
                        "dependentes": 2,
                        "profissao": "empresario"
                    }
                    response = requests.post(url, json=payload)
                
                elif "gerar-script-venda" in endpoint:
                    payload = {
                        "perfil_cliente": {"nome": "Maria Santos"},
                        "plano_sugerido": "FAMILIAR"
                    }
                    response = requests.post(url, json=payload)
                
                elif "leads" in endpoint:
                    response = requests.get(url)
                
                elif "webhook" in endpoint:
                    response = requests.get(url)
                
                status = "✅" if response.status_code in [200, 201] else "❌"
                print(f"{status} {endpoint}: {response.status_code}")
                
            except Exception as e:
                print(f"❌ {endpoint}: ERRO - {str(e)}")

async def main():
    """Função principal de teste"""
    tester = TesteIntegracaoCompleta()
    
    print("🚀 HEALTH PLATFORM - TESTE DE INTEGRAÇÃO COMPLETA")
    print("📍 Ambiente: Localhost")
    print("⏰ Iniciando testes...\n")
    
    # 1. Testar endpoints da API
    tester.testar_endpoints_api()
    
    # 2. Testar fluxo completo de orquestração
    await tester.testar_fluxo_completo()
    
    print("\n🎉 TESTES CONCLUÍDOS!")
    print("📊 Verifique os logs do servidor para detalhes completos")

if __name__ == "__main__":
    # Executar testes
    asyncio.run(main())