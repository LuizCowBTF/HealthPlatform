#!/usr/bin/env python3
"""
HealthPlatform SaaS - Runner Principal
Execute este arquivo para iniciar o sistema completo.
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório do projeto ao path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def main():
    """Função principal para iniciar o sistema"""
    
    print("=" * 60)
    print("🚀 HEALTHPLATFORM SAAS - SISTEMA COMPLETO")
    print("=" * 60)
    
    # Verificar se o main.py existe
    main_py = PROJECT_ROOT / "app" / "backend" / "src" / "main.py"
    main_fixed = PROJECT_ROOT / "app" / "backend" / "src" / "main_fixed.py"
    
    if main_py.exists():
        print(f"✅ Usando versão principal: {main_py.name}")
        target = "app.backend.src.main"
    elif main_fixed.exists():
        print(f"⚠️  Usando versão alternativa: {main_fixed.name}")
        target = "app.backend.src.main_fixed"
    else:
        print("❌ Nenhum arquivo principal encontrado!")
        return 1
    
    # Iniciar servidor
    print("\n" + "=" * 60)
    print("🔥 INICIANDO SERVIDOR...")
    print("=" * 60)
    
    try:
        import uvicorn
        uvicorn.run(
            f"{target}:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            reload_dirs=[str(PROJECT_ROOT / "app" / "backend" / "src")]
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar servidor: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())