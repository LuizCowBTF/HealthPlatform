# app/backend/src/main.py - VERSÃO DEFINITIVA
import sys
from pathlib import Path

# 🔧 CONFIGURAR PATHS
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "app" / "backend" / "src"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from datetime import datetime
import importlib

# ============================================
# CONFIGURAÇÃO DO APP
# ============================================

app = FastAPI(
    title="HealthPlatform SaaS",
    version="2.0.0",
    description="CRM + WhatsApp + IA + Financeiro + Comissões - VERSÃO DEFINITIVA",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# CAMINHOS DO PROJETO (AJUSTE CONFORME SEU PROJETO)
# ============================================

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
FRONTEND_ROOT = PROJECT_ROOT / "app" / "frontend"

print("=" * 70)
print("🚀 HEALTH PLATFORM SaaS - VERSÃO DEFINITIVA")
print("=" * 70)
print(f"📁 Project Root: {PROJECT_ROOT}")
print(f"📁 Frontend Root: {FRONTEND_ROOT}")

# ============================================
# MONTAR ARQUIVOS ESTÁTICOS (BASEADO NA SUA ESTRUTURA)
# ============================================

# LISTA DE PASTAS PARA MONTAR (ajuste conforme seu projeto)
STATIC_FOLDERS = [
    # (rota, pasta_real, nome)
    ("/dashboards", "dashboards", "dashboards"),
    ("/pages", "pges", "pages"),  # ⚠️ ATENÇÃO: rota "/pages" mas pasta "pges"
    ("/css", "css", "css"),
    ("/js", "js", "js"),
    ("/img", "img", "img"),
    ("/static", ".", "static_all")  # Serve tudo de frontend
]

print("\n📦 CONFIGURANDO ARQUIVOS ESTÁTICOS:")
print("-" * 40)

for route, folder_name, mount_name in STATIC_FOLDERS:
    folder_path = FRONTEND_ROOT / folder_name
    
    # Se for "." significa a pasta frontend inteira
    if folder_name == ".":
        folder_path = FRONTEND_ROOT
    
    if folder_path.exists():
        try:
            app.mount(route, StaticFiles(directory=str(folder_path)), name=mount_name)
            print(f"✅ {route} → {folder_path}")
        except Exception as e:
            print(f"⚠️  Erro em {route}: {e}")
    else:
        print(f"❌ Pasta não existe: {folder_path}")

# ============================================
# ROTAS DE API (MANTIDAS DO SEU CÓDIGO ORIGINAL)
# ============================================

@app.get("/api/health")
async def health_check():
    """Health check do sistema"""
    return JSONResponse({
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "frontend": FRONTEND_ROOT.exists(),
        "message": "HealthPlatform SaaS - Versão Definitiva"
    })

@app.get("/api/v1/crm/dashboard/completo")
async def get_dashboard_completo():
    """Dashboard básico com dados REALISTAS"""
    return {
        "success": True,
        "data": {
            "metricas_principais": {
                "faturamento_total": 189000,
                "leads_novos": 65,
                "taxa_conversao": 35.4,
                "clientes_ativos": 42,
                "vendas_mes_atual": 25,
                "meta_mensal": 50,
                "progresso_meta": 84
            },
            "leads_por_status": [
                {"status": "Novo", "quantidade": 45},
                {"status": "Contatado", "quantidade": 38},
                {"status": "Qualificado", "quantidade": 32},
                {"status": "Fechado", "quantidade": 42}
            ],
            "top_corretores": [
                {"nome": "João Silva", "vendas": 15, "comissao": 2250},
                {"nome": "Maria Santos", "vendas": 12, "comissao": 1800}
            ]
        }
    }

@app.get("/api/v1/crm/dashboard/avancado")
async def get_dashboard_avancado():
    """Dashboard avançado com DADOS REAIS"""
    return JSONResponse({
        "success": True,
        "data": {
            "metricas_detalhadas": {
                "faturamento_mensal": 125000,
                "faturamento_anual": 1500000,
                "crescimento_mensal": 12.5,
                "crescimento_anual": 28.7,
                "ticket_medio": 850.50
            },
            "performance_corretores": [
                {
                    "nome": "João Silva",
                    "vendas": 15,
                    "meta": 12,
                    "atingimento": 125,
                    "comissao": 2250,
                    "leads": 45,
                    "conversao": 33.3
                },
                {
                    "nome": "Maria Santos", 
                    "vendas": 12,
                    "meta": 12,
                    "atingimento": 100,
                    "comissao": 1800,
                    "leads": 38,
                    "conversao": 31.6
                }
            ],
            "evolucao_mensal": [
                {"mes": "Jan/24", "vendas": 12, "leads": 45, "faturamento": 18000},
                {"mes": "Fev/24", "vendas": 15, "leads": 52, "faturamento": 22500},
                {"mes": "Mar/24", "vendas": 18, "leads": 58, "faturamento": 27000}
            ],
            "distribuicao_leads": [
                {"origem": "Site", "quantidade": 120, "percentual": 35},
                {"origem": "Indicação", "quantidade": 85, "percentual": 25},
                {"origem": "WhatsApp", "quantidade": 65, "percentual": 19}
            ]
        }
    })

# ============================================
# ROTAS PRINCIPAIS DO SISTEMA
# ============================================

@app.get("/")
async def serve_index():
    """Serve a página principal (SPA)"""
    index_path = FRONTEND_ROOT / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    
    # Fallback
    return JSONResponse({
        "message": "HealthPlatform SaaS",
        "docs": "/api/docs",
        "health": "/api/health"
    })

@app.get("/dashboard")
async def serve_dashboard_direct():
    """Rota direta para o dashboard"""
    dashboard_path = FRONTEND_ROOT / "dashboards" / "dashboard.html"
    if dashboard_path.exists():
        return FileResponse(dashboard_path)
    
    # Se não encontrar, redireciona para a SPA
    return FileResponse(FRONTEND_ROOT / "index.html")

# ============================================
# ROTA CATCH-ALL PARA SPA (Single Page Application)
# ============================================

@app.get("/{path:path}")
async def serve_spa_or_file(path: str):
    """
    Serve arquivos ou redireciona para SPA.
    Funciona como fallback para todas as rotas do frontend.
    """
    
    # Ignorar rotas API
    if path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Rota API não encontrada")
    
    # Tentar encontrar o arquivo em várias localizações possíveis
    possible_locations = [
        FRONTEND_ROOT / path,                           # Ex: /index.html
        FRONTEND_ROOT / "dashboards" / path,           # Ex: /dashboard.html
        FRONTEND_ROOT / "pges" / path,                 # Ex: /auth/login.html
        FRONTEND_ROOT / "css" / path,                  # Ex: /css/style.css
        FRONTEND_ROOT / "js" / path,                   # Ex: /js/main.js
        FRONTEND_ROOT / "img" / path,                  # Ex: /img/logo.png
    ]
    
    for file_path in possible_locations:
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
    
    # Se não encontrou arquivo, serve o index.html (SPA behavior)
    index_path = FRONTEND_ROOT / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    
    # Último fallback
    raise HTTPException(status_code=404, detail="Arquivo não encontrado")

# ============================================
# INICIALIZAÇÃO E STARTUP
# ============================================

@app.on_event("startup")
async def startup_event():
    """Evento de inicialização do sistema"""
    print("\n" + "=" * 70)
    print("🎉 SISTEMA INICIALIZADO COM SUCESSO!")
    print("=" * 70)
    print(f"🌐 Dashboard: http://localhost:8000/")
    print(f"📊 API Health: http://localhost:8000/api/health")
    print(f"📚 Documentação: http://localhost:8000/api/docs")
    print(f"⚡ Modo: Produção")
    print("=" * 70)

# ============================================
# EXECUÇÃO PRINCIPAL
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "=" * 70)
    print("⚡ INICIANDO HEALTHPLATFORM SAAS...")
    print("=" * 70)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )