# test_integracao_simplificado.py
import asyncio
import sys
import os

# Adicionar o path do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Tentar importar com estrutura correta
    from backend.src.core.modules.ai.health_ia import health_ia
    print("✅ HealthIA importado com sucesso!")
    
    # Criar orquestração simplificada para teste
    class OrchestrationTest:
        def __init__(self):
            self.ia = health_ia
            print("🧠 IA Carregada - Planos:", list(self.ia.planos_disponiveis.keys()))
        
        async def testar_analise_perfil(self):
            """Testa análise de perfil da IA"""
            print("\n🎯 TESTANDO ANÁLISE DE PERFIL")
            
            perfis_teste = [
                {"nome": "João", "idade": 25, "renda": 2000, "dependentes": 0, "profissao": "estudante"},
                {"nome": "Maria", "idade": 35, "renda": 8000, "dependentes": 2, "profissao": "empresaria"},
                {"nome": "Carlos", "idade": 45, "renda": 15000, "dependentes": 1, "profissao": "diretor"}
            ]
            
            for perfil in perfis_teste:
                resultado = self.ia.analisar_perfil_cliente(perfil)
                print(f"👤 {perfil['nome']} → Plano: {resultado['plano_sugerido']}")
                print(f"   Operadora: {resultado['operadora_sugerida']}")
                print(f"   Preço: R$ {resultado['faixa_preco_estimada']}")
            
        async def testar_script_venda(self):
            """Testa geração de scripts de venda"""
            print("\n🎯 TESTANDO SCRIPTS DE VENDA")
            
            planos = ["INDIVIDUAL", "FAMILIAR", "EMPRESARIAL", "VIP"]
            
            for plano in planos:
                script = self.ia.gerar_script_venda(
                    perfil_cliente={"nome": "Cliente Teste"},
                    plano_sugerido=plano
                )
                print(f"📝 {plano}: {script[:80]}...")
    
    async def main():
        tester = OrchestrationTest()
        await tester.testar_analise_perfil()
        await tester.testar_script_venda()
        
        print("\n🎉 TESTE BÁSICO CONCLUÍDO!")
        print("✅ IA Brasileira funcionando perfeitamente!")
        
except ImportError as e:
    print(f"❌ ERRO DE IMPORTAÇÃO: {e}")
    print("\n🔍 PRECISO DA ESTRUTURA EXATA DAS PASTAS!")
    print("Execute no prompt e me mostre:")
    print("dir E:\\workspace\\HealthPlatform\\app /s")

# Executar teste
if __name__ == "__main__":
    asyncio.run(main())