# test_integracao_corrigido.py
import asyncio
import sys
import os

# Adicionar paths corretos
sys.path.append(os.path.join(os.getcwd(), 'app', 'backend', 'src'))

try:
    from core.modules.ai.health_ia import health_ia
    from core.services.orchestration_service import orchestration_service
    print("✅ TODOS OS MÓDULOS IMPORTADOS COM SUCESSO!")
    
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    sys.exit(1)

class TesteIntegracaoCompleta:
    def __init__(self):
        self.orchestration = orchestration_service
        print("🚀 SISTEMA DE ORQUESTRAÇÃO INICIADO")
    
    async def testar_fluxo_whatsapp_ia_crm(self):
        """Testa o fluxo completo: WhatsApp → IA → CRM"""
        print("\n" + "="*60)
        print("🧪 TESTE DO FLUXO COMPLETO WHATSAPP + IA + CRM")
        print("="*60)
        
        # Cenários de teste realistas
        cenarios = [
            {
                "nome": "Cliente Novo - Saudação",
                "telefone": "5511999999999",
                "mensagem": "Oi, gostaria de saber sobre planos de saúde",
                "perfil_nome": "João Silva"
            },
            {
                "nome": "Interesse em Preços - Familiar", 
                "telefone": "5511988888888",
                "mensagem": "Quanto custa um plano para família de 4 pessoas?",
                "perfil_nome": "Maria Santos"
            },
            {
                "nome": "Executivo - Urgente",
                "telefone": "5511977777777", 
                "mensagem": "Preciso URGENTE de um plano empresarial para minha empresa!",
                "perfil_nome": "Carlos Oliveira"
            },
            {
                "nome": "Jovem - Orçamento Baixo",
                "telefone": "5511966666666",
                "mensagem": "Tenho 25 anos e quero um plano básico, quanto custa?",
                "perfil_nome": "Ana Souza"
            }
        ]
        
        resultados = []
        
        for i, cenario in enumerate(cenarios, 1):
            print(f"\n🎯 CENÁRIO {i}: {cenario['nome']}")
            print(f"📱 Telefone: {cenario['telefone']}")
            print(f"💬 Mensagem: '{cenario['mensagem']}'")
            
            # Simular payload do webhook do WhatsApp
            payload_webhook = {
                "from": cenario["telefone"],
                "text": cenario["mensagem"],
                "profile_name": cenario["perfil_nome"],
                "message_id": f"test_msg_{i}",
                "timestamp": 1234567890,
                "whatsapp_business_id": "test_business_123"
            }
            
            try:
                # Processar via orquestração
                resultado = await self.orchestration.processar_mensagem_whatsapp(payload_webhook)
                
                if resultado["success"]:
                    print("✅ SUCESSO NO PROCESSAMENTO!")
                    print(f"💬 Resposta: {resultado['resposta'][:120]}...")
                    print(f"👤 Lead ID: {resultado.get('lead_id', 'N/A')}")
                    print(f"📊 Estágio: {resultado.get('estagio_funil', 'N/A')}")
                    print(f"🎯 Plano: {resultado.get('plano_sugerido', 'N/A')}")
                    
                    resultados.append({
                        "cenario": cenario["nome"],
                        "status": "success",
                        "detalhes": resultado
                    })
                else:
                    print("❌ FALHA NO PROCESSAMENTO")
                    print(f"Erro: {resultado.get('error', 'Desconhecido')}")
                    
                    resultados.append({
                        "cenario": cenario["nome"], 
                        "status": "error",
                        "erro": resultado.get('error')
                    })
                    
            except Exception as e:
                print(f"💥 ERRO EXCEÇÃO: {str(e)}")
                resultados.append({
                    "cenario": cenario["nome"],
                    "status": "exception", 
                    "erro": str(e)
                })
            
            print("-" * 50)
            await asyncio.sleep(1)  # Delay entre testes
        
        return resultados
    
    async def testar_ia_diretamente(self):
        """Testa a IA brasileira diretamente"""
        print("\n" + "="*50)
        print("🧠 TESTE DIRETO DA IA BRASILEIRA")
        print("="*50)
        
        perfis_teste = [
            {"nome": "Estudante", "idade": 22, "renda": 1500, "dependentes": 0, "profissao": "estudante"},
            {"nome": "Família", "idade": 35, "renda": 8000, "dependentes": 3, "profissao": "professor"},
            {"nome": "Executivo", "idade": 45, "renda": 20000, "dependentes": 1, "profissao": "diretor"},
            {"nome": "Aposentado", "idade": 68, "renda": 5000, "dependentes": 0, "profissao": "aposentado"}
        ]
        
        for perfil in perfis_teste:
            print(f"\n👤 Analisando: {perfil['nome']}")
            resultado = health_ia.analisar_perfil_cliente(perfil)
            print(f"   📋 Plano: {resultado['plano_sugerido']}")
            print(f"   🏥 Operadora: {resultado['operadora_sugerida']}") 
            print(f"   💰 Preço: R$ {resultado['faixa_preco_estimada'][0]} - R$ {resultado['faixa_preco_estimada'][1]}")
            print(f"   📝 Justificativa: {resultado['justificativa']}")
    
    async def testar_scripts_venda(self):
        """Testa geração de scripts de venda"""
        print("\n" + "="*50)
        print("📝 TESTE DE SCRIPTS DE VENDA")
        print("="*50)
        
        planos = ["INDIVIDUAL", "FAMILIAR", "EMPRESARIAL", "VIP"]
        
        for plano in planos:
            print(f"\n🎯 Plano: {plano}")
            script = health_ia.gerar_script_venda(
                perfil_cliente={"nome": "Cliente Teste"},
                plano_sugerido=plano
            )
            print(f"   📄 Script: {script[:100]}...")

async def main():
    """Executa todos os testes"""
    print("🚀 HEALTH PLATFORM - TESTE DE INTEGRAÇÃO COMPLETO")
    print("📍 Estrutura verificada e imports corrigidos!")
    print("⏰ Iniciando testes...\n")
    
    tester = TesteIntegracaoCompleta()
    
    # Executar testes em sequência
    await tester.testar_ia_diretamente()
    await tester.testar_scripts_venda()
    
    print("\n🔥 INICIANDO TESTE DE ORQUESTRAÇÃO COMPLETA...")
    resultados = await tester.testar_fluxo_whatsapp_ia_crm()
    
    # Resumo final
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    
    sucessos = sum(1 for r in resultados if r["status"] == "success")
    erros = sum(1 for r in resultados if r["status"] == "error")
    excecoes = sum(1 for r in resultados if r["status"] == "exception")
    
    print(f"✅ Sucessos: {sucessos}/{len(resultados)}")
    print(f"❌ Erros: {erros}/{len(resultados)}")
    print(f"💥 Exceções: {excecoes}/{len(resultados)}")
    
    if sucessos == len(resultados):
        print("\n🎉 TODOS OS TESTES PASSARAM! SISTEMA INTEGRADO COM SUCESSO! 🎉")
    else:
        print(f"\n⚠️  {erros + excecoes} teste(s) falharam. Verifique os logs.")
    
    print("\n✨ Health Platform - Integração WhatsApp + IA + CRM ✨")

if __name__ == "__main__":
    asyncio.run(main())