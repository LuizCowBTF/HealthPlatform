import os
import sys
import subprocess
import time
from pathlib import Path

def check_server_running(port=8000):
    """Verifica se o servidor já está rodando"""
    try:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    except:
        return False

def start_server():
    """Inicia o servidor FastAPI"""
    print("🚀 INICIANDO HEALTHPLATFORM SAAS...")
    
    current_dir = Path(__file__).parent
    print(f"📁 Diretório: {current_dir}")
    
    # Verificar dependências
    try:
        import fastapi
        import uvicorn
        print("✅ Dependências encontradas")
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("📦 Instalando dependências...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    
    # Verificar se servidor já está rodando
    if check_server_running():
        print("✅ Servidor já está rodando na porta 8000")
        print("🌐 Acesse: http://localhost:8000")
        return True
    
    # Iniciar servidor - CAMINHO CORRETO!
    print("🔥 Iniciando servidor FastAPI...")
    try:
        # Usar o arquivo principal correto
        subprocess.Popen([
            sys.executable, 
            "-m", "uvicorn", 
            "app.backend.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
        
        # Aguardar inicialização
        print("⏳ Aguardando servidor iniciar...")
        time.sleep(5)
        
        if check_server_running():
            print("🎉 SERVIDOR INICIADO COM SUCESSO!")
            print("🌐 Dashboard: http://localhost:8000")
            print("🔧 API Health: http://localhost:8000/health")
            return True
        else:
            print("❌ Falha ao iniciar servidor - tempo esgotado")
            return False
            
    except Exception as e:
        print(f"💥 Erro ao iniciar servidor: {e}")
        return False

if __name__ == "__main__":
    start_server()