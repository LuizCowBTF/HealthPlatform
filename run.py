# run.py - CORRIGIDO
import subprocess
import sys
import os
from pathlib import Path

def main():
    print("🚀 INICIANDO HEALTHPLATFORM SAAS...")
    
    # Mudar para o diretório do projeto
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    print(f"📁 Diretório: {project_dir}")
    
    # Verificar se o main.py existe
    main_path = project_dir / "app" / "backend" / "src" / "main.py"
    if not main_path.exists():
        print(f"❌ Arquivo main.py não encontrado: {main_path}")
        return
    
    print("✅ Estrutura validada")
    print("🔥 Iniciando servidor FastAPI...")
    
    try:
        # Executar uvicorn com o caminho CORRETO
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.backend.src.main:app",  # ✅ CAMINHO CORRETO
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Servidor interrompido")

if __name__ == "__main__":
    main()