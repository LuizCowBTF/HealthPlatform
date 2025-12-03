"""
Configurações do HealthPlatform SaaS
"""

from pathlib import Path
import os

# ============================================
# CAMINHOS DO PROJETO
# ============================================

# Diretório raiz do projeto (4 níveis acima deste arquivo)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Frontend
FRONTEND_ROOT = PROJECT_ROOT / "app" / "frontend"

# Database
DATABASE_PATH = PROJECT_ROOT / "health_platform.db"

# ============================================
# CONFIGURAÇÕES DE PASTAS ESTÁTICAS
# ============================================

# Mapeamento: rota → pasta (ajuste conforme sua estrutura real)
STATIC_MAPPING = [
    ("/dashboards", "dashboards"),
    ("/pages", "pages"),      # ⚠️ Rota "/pages" aponta para pasta "pages"
    ("/css", "css"),
    ("/js", "js"),
    ("/img", "img"),
]

# ============================================
# CONFIGURAÇÕES DA API
# ============================================

API_PREFIX = "/api"
API_VERSION = "v1"
API_TITLE = "HealthPlatform SaaS"
API_DESCRIPTION = "CRM + WhatsApp + IA + Financeiro + Comissões"
API_VERSION_NUMBER = "2.0.0"

# ============================================
# VALIDAÇÃO DE ESTRUTURA
# ============================================

def validate_structure():
    """Valida se a estrutura de pastas existe"""
    print("\n🔍 Validando estrutura do projeto...")
    
    required = [
        ("Frontend", FRONTEND_ROOT),
        ("Dashboards", FRONTEND_ROOT / "dashboards"),
        ("Pages", FRONTEND_ROOT / "pages"),
        ("Index", FRONTEND_ROOT / "index.html"),
    ]
    
    all_ok = True
    for name, path in required:
        exists = path.exists()
        status = "✅" if exists else "❌"
        print(f"  {status} {name}: {path}")
        
        if not exists:
            all_ok = False
    
    return all_ok

# ============================================
# FUNÇÕES ÚTEIS
# ============================================

def get_static_paths():
    """Retorna lista de caminhos estáticos válidos"""
    valid_paths = []
    
    for route, folder_name in STATIC_MAPPING:
        folder_path = FRONTEND_ROOT / folder_name
        if folder_path.exists():
            valid_paths.append((route, folder_path))
    
    return valid_paths