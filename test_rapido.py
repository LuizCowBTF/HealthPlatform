# test_rapido.py
import sys
import os

# Adicionar o diretório atual ao path
sys.path.append(os.getcwd())

print("🔍 Buscando módulos...")

try:
    # Tentativa 1: Import direto do health_ia
    from app.backend.src.core.modules.ai.health_ia import health_ia
    print("✅ HealthIA importado com sucesso!")
    
except ImportError as e:
    print(f"❌ ImportError: {e}")
    
    try:
        # Tentativa 2: Import manual
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "health_ia", 
            "app/backend/src/core/modules/ai/health_ia.py"
        )
        health_ia_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(health_ia_module)
        health_ia = health_ia_module.health_ia
        print("✅ HealthIA carregado manualmente!")
        
    except Exception as e2:
        print(f"❌ Falha no carregamento manual: {e2}")
        
        # Tentativa 3: Procurar o arquivo
        print("\n🔍 Procurando arquivo health_ia.py...")
        for root, dirs, files in os.walk("."):
            if "health_ia.py" in files:
                print(f"✅ Encontrado em: {os.path.join(root, 'health_ia.py')}")
                break
        else:
            print("❌ Arquivo health_ia.py não encontrado!")

# Teste básico se conseguiu importar
try:
    if 'health_ia' in locals():
        print("\n🎯 TESTANDO IA BRASILEIRA...")
        
        # Teste de análise de perfil
        perfil_teste = {
            "nome": "João Silva", 
            "idade": 35, 
            "renda": 8000, 
            "dependentes": 2, 
            "profissao": "empresario"
        }
        
        resultado = health_ia.analisar_perfil_cliente(perfil_teste)
        print(f"✅ Análise funcionando!")
        print(f"👤 Plano sugerido: {resultado['plano_sugerido']}")
        print(f"🏥 Operadora: {resultado['operadora_sugerida']}")
        print(f"💰 Preço: R$ {resultado['faixa_preco_estimada']}")
        
        # Teste de script de venda
        script = health_ia.gerar_script_venda(
            perfil_cliente={"nome": "Maria"},
            plano_sugerido=resultado['plano_sugerido']
        )
        print(f"📝 Script: {script[:100]}...")
        
        print("\n🎉 TUDO FUNCIONANDO PERFEITAMENTE!")
        
except NameError:
    print("\n❌ Não foi possível carregar a IA")
    print("💡 Preciso da estrutura exata das pastas!")