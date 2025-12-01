from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
import aiosqlite
import os
from datetime import datetime, timedelta
import json
from pathlib import Path

app = FastAPI(title="HealthPlatform SaaS", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ CAMINHOS CORRETOS - FOCANDO NO FRONTEND
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent  # HealthPlatform/
FRONTEND_DIR = PROJECT_ROOT / "app" / "frontend"
DATABASE_PATH = PROJECT_ROOT / "health_platform.db"

print("=" * 60)
print("🚀 HEALTH PLATFORM SaaS - CONFIGURAÇÃO")
print("=" * 60)
print(f"📁 PROJECT_ROOT: {PROJECT_ROOT}")
print(f"📁 FRONTEND_DIR: {FRONTEND_DIR} → Existe: {FRONTEND_DIR.exists()}")

# ✅ SERVIR ARQUIVOS ESTÁTICOS DO FRONTEND
if FRONTEND_DIR.exists():
    # MONTAR TODOS OS ARQUIVOS ESTÁTICOS
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
    print("✅ Static files montado em /static")
    
    # Montar diretório de dashboards separadamente
    DASHBOARDS_DIR = FRONTEND_DIR / "dashboards"
    if DASHBOARDS_DIR.exists():
        app.mount("/dashboards", StaticFiles(directory=DASHBOARDS_DIR), name="dashboards")
        print("✅ Dashboards montado em /dashboards")
    
    # Montar diretório de páginas
    PAGES_DIR = FRONTEND_DIR / "pages"
    if PAGES_DIR.exists():
        app.mount("/pages", StaticFiles(directory=PAGES_DIR), name="pages")
        print("✅ Pages montado em /pages")
    
    # Montar outros diretórios estáticos
    for static_dir in ["css", "js", "img"]:
        dir_path = FRONTEND_DIR / static_dir
        if dir_path.exists():
            app.mount(f"/{static_dir}", StaticFiles(directory=dir_path), name=static_dir)
            print(f"✅ {static_dir} montado em /{static_dir}")
else:
    print("❌ FRONTEND_DIR não encontrado!")

# ✅ ROTA DE HEALTH CHECK
@app.get("/api/health")
async def health_check():
    """Health check da aplicação"""
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "database": DATABASE_PATH.exists(),
        "frontend_dir": str(FRONTEND_DIR),
        "frontend_exists": FRONTEND_DIR.exists()
    }

# ✅ SUAS ROTAS DE API EXISTENTES (mantidas iguais)
@app.get("/api/v1/crm/dashboard/completo")
async def get_dashboard_completo():
    """Endpoint completo para o dashboard"""
    try:
        if not DATABASE_PATH.exists():
            return create_dashboard_fallback()
            
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM leads WHERE status LIKE '%Fechado%'")
            clientes_ativos = (await cursor.fetchone())[0]
            
            cursor = await db.execute("SELECT COUNT(*) FROM leads")
            total_leads = (await cursor.fetchone())[0]
            
            return {
                "vendas_mensais": [],
                "vendas_operadora": [],
                "leads_por_status": [],
                "top_corretores": [],
                "metricas_principais": {
                    "faturamento_total": float(clientes_ativos * 1500),
                    "leads_novos": total_leads,
                    "taxa_conversao": round((clientes_ativos / max(total_leads, 1)) * 100, 1) if total_leads > 0 else 0,
                    "clientes_ativos": clientes_ativos,
                    "meta_mensal": 0,
                    "progresso_meta": 0,
                    "vendas_mes_atual": 0
                },
                "atividades_recentes": []
            }
            
    except Exception as e:
        print(f"❌ Erro no dashboard completo: {str(e)}")
        return create_dashboard_fallback()

@app.get("/api/v1/crm/dashboard/metricas")
async def get_dashboard_metricas():
    """Endpoint para métricas básicas"""
    try:
        if not DATABASE_PATH.exists():
            return {
                "faturamento_total": 0,
                "leads_novos": 0,
                "taxa_conversao": 0,
                "clientes_ativos": 0
            }
            
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM leads WHERE status LIKE '%Fechado%'")
            clientes_ativos = (await cursor.fetchone())[0]
            
            cursor = await db.execute("SELECT COUNT(*) FROM leads")
            total_leads = (await cursor.fetchone())[0]
            
            return {
                "faturamento_total": float(clientes_ativos * 1500),
                "leads_novos": total_leads,
                "taxa_conversao": round((clientes_ativos / max(total_leads, 1)) * 100, 1) if total_leads > 0 else 0,
                "clientes_ativos": clientes_ativos
            }
            
    except Exception as e:
        return {"error": str(e)}

# ✅ ROTA PRINCIPAL - SERVE O INDEX.HTML (SINGLE PAGE APPLICATION)
@app.get("/")
async def serve_index():
    """Serve a página principal index.html"""
    index_path = FRONTEND_DIR / "index.html"
    
    if index_path.exists():
        return FileResponse(index_path)
    else:
        return HTMLResponse("Página principal não encontrada", status_code=404)

# ✅ ROTA ESPECÍFICA PARA DASHBOARD.HTML (para acesso direto)
@app.get("/dashboard.html")
async def serve_dashboard_direct():
    """Serve o dashboard.html diretamente (sem iframe)"""
    dashboard_path = FRONTEND_DIR / "dashboards" / "dashboard.html"
    
    if dashboard_path.exists():
        return FileResponse(dashboard_path)
    else:
        return RedirectResponse("/")

# ✅ BLOQUEAR ACESSO DIRETO ÀS PÁGINAS QUE DEVEM SER CARREGADAS NO IFRAME
@app.get("/dashboards/dashboard.html")
async def block_dashboard_redirect():
    """Redireciona para a página principal se tentar acessar dashboard diretamente"""
    return RedirectResponse("/")

@app.get("/pages/{path:path}")
async def block_pages_redirect(path: str):
    """Redireciona páginas internas para a página principal"""
    return RedirectResponse("/")

# ✅ ROTA PARA ARQUIVOS ESTÁTICOS (CSS, JS, IMG) - já coberto pelo mount
# ✅ ROTA FALLBACK PARA QUALQUER OUTRA REQUISIÇÃO
@app.get("/{full_path:path}")
async def catch_all_routes(full_path: str):
    """
    Captura todas as rotas e:
    1. Tenta servir como arquivo estático
    2. Se não encontrar, retorna o index.html (para SPA)
    """
    
    # Ignora rotas de API
    if full_path.startswith("api/"):
        return {"error": "Endpoint API não encontrado", "path": full_path}
    
    # Tenta encontrar como arquivo estático
    static_path = FRONTEND_DIR / full_path
    if static_path.exists() and static_path.is_file():
        return FileResponse(static_path)
    
    # Para SPA, sempre retorna index.html
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    
    return HTMLResponse(f"Página não encontrada: {full_path}", status_code=404)

def create_dashboard_fallback():
    """Dados fallback para quando o banco não está disponível"""
    return {
        "vendas_mensais": [
            {"mes": "2024-01", "vendas": 15, "faturamento": 22500},
            {"mes": "2024-02", "vendas": 22, "faturamento": 33000},
            {"mes": "2024-03", "vendas": 18, "faturamento": 27000}
        ],
        "metricas_principais": {
            "faturamento_total": 82500,
            "leads_novos": 55,
            "taxa_conversao": 32.7,
            "clientes_ativos": 18,
            "meta_mensal": 15,
            "progresso_meta": 86,
            "vendas_mes_atual": 13
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 INICIANDO SERVIDOR...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")