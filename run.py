# run.py
import subprocess
import sys
import os
from pathlib import Path

def main():
    print("🚀 INICIANDO HEALTHPLATFORM SAAS...")
    
    # Mudar para o diretório do projeto
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    print(f"📁 Diretório do projeto: {project_dir}")
    
    # Verificar se o main.py existe
    main_path = project_dir / "app" / "backend" / "src" / "main.py"
    print(f"🔍 Procurando main.py em: {main_path}")
    
    if not main_path.exists():
        print(f"❌ ERRO: Arquivo main.py não encontrado!")
        print("📋 Estrutura esperada:")
        print("   HealthPlatform/")
        print("   └── app/")
        print("       └── backend/")
        print("           └── src/")
        print("               └── main.py")
        return
    
    print("✅ Estrutura validada com sucesso!")
    print("🔥 Iniciando servidor FastAPI...")
    print("🌐 Dashboard disponível em: http://localhost:8000/")
    print("📊 API disponível em: http://localhost:8000/api/v1/crm/dashboard/completo")
    print("⏹️  Para parar o servidor: CTRL + C")
    print("-" * 50)
    
    try:
        # Executar uvicorn com o caminho CORRETO
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.backend.src.main:app",
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload",
            "--log-level", "info"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()