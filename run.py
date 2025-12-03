#!/usr/bin/env python3
"""
HealthPlatform SaaS v3.0 - Runner Principal
Sistema completo com todos os módulos integrados
"""

import sys
import os
from pathlib import Path

# Configurar paths
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def print_banner():
    """Imprime banner do sistema"""
    print("\n" + "=" * 70)
    print("🏥 HEALTHPLATFORM SAAS v3.0")
    print("=" * 70)
    print("Sistema Completo: CRM + WhatsApp + IA + Financeiro + Comissões")
    print("=" * 70)

def check_environment():
    """Verifica ambiente e dependências"""
    print("\n🔍 Verificando ambiente...")
    
    # Verificar se main.py existe
    main_py = PROJECT_ROOT / "app" / "backend" / "src" / "main.py"
    if not main_py.exists():
        print("❌ Arquivo principal não encontrado:", main_py)
        return False
    
    # Verificar frontend
    frontend = PROJECT_ROOT / "app" / "frontend"
    if not frontend.exists():
        print("❌ Frontend não encontrado:", frontend)
        return False
    
    print("✅ Ambiente verificado")
    return True

def main():
    """Função principal"""
    print_banner()
    
    if not check_environment():
        print("\n❌ Não foi possível iniciar o sistema")
        return 1
    
    # Iniciar servidor
    print("\n🚀 Iniciando servidor...")
    print("=" * 70)
    
    try:
        import uvicorn
        uvicorn.run(
            "app.backend.src.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            reload_dirs=[
                str(PROJECT_ROOT / "app" / "backend" / "src"),
                str(PROJECT_ROOT / "app" / "frontend")
            ]
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar servidor: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())