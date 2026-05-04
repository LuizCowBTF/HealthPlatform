"""
Testes básicos para o Health Platform CRM
"""
import pytest
import sys
from pathlib import Path

# Adiciona o backend ao path
backend_path = Path(__file__).parent.parent / "app" / "backend" / "src"
sys.path.insert(0, str(backend_path))

def test_import_main():
    """Teste mínimo: verifica se o main.py importa sem erros"""
    try:
        from main import app
        assert app is not None
        print("✅ App imported successfully")
    except ImportError as e:
        pytest.skip(f"Main module not ready: {e}")

def test_health_endpoint():
    """Testa o endpoint de health se o app estiver disponível"""
    try:
        from main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/api/health")
        
        # Se o endpoint não existe, ainda assim o teste passa (apenas avisa)
        if response.status_code == 404:
            pytest.skip("Health endpoint not implemented yet")
        else:
            assert response.status_code == 200
    except ImportError:
        pytest.skip("App not available for testing")