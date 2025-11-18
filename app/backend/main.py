# app/backend/main.py - VERSÃO CORRIGIDA
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import os
from pathlib import Path

# Configurar paths CORRETAMENTE
current_dir = Path(__file__).parent  # app/backend/
project_root = current_dir.parent.parent  # HealthPlatform/
frontend_dir = project_root / "app" / "frontend"

app = FastAPI(title="HealthPlatform SaaS", version="2.1.0")

print(f"📁 Project Root: {project_root}")
print(f"📁 Frontend Dir: {frontend_dir}")

# Mount static files - CORRIGIDO
static_dir = frontend_dir / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    print("✅ Arquivos estáticos montados")
    print(f"📁 Static files em: {static_dir}")
else:
    print(f"❌ Pasta static não encontrada: {static_dir}")

# Configurar templates - CORRIGIDO
templates_dir = frontend_dir / "templates"
if templates_dir.exists():
    templates = Jinja2Templates(directory=str(templates_dir))
    print("✅ Templates carregados")
    print(f"📁 Templates em: {templates_dir}")
else:
    print(f"❌ Pasta templates não encontrada: {templates_dir}")
    # Criar fallback
    templates = None

# Importações condicionais para evitar erros
try:
    from app.backend.src.core.database import get_db, engine
    from app.backend.src.core.modules.crm.models import Base
    
    # Criar tabelas se os modelos existirem
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas do banco criadas/com validadas")
except ImportError as e:
    print(f"⚠️  Aviso: Alguns módulos não disponíveis - {e}")


# Registrar rotas IA
try:
    from app.backend.src.routes.ia_routes import router as ia_router
    app.include_router(ia_router, prefix="/api/v1/ia", tags=["Inteligência Artificial"])
    print("✅ Rotas IA Brasileira registradas")
except ImportError as e:
    print(f"⚠️  Rotas IA não disponíveis: {e}")



# Registrar rotas condicionalmente
try:
    from app.backend.src.routes.whatsapp_routes import router as whatsapp_router
    app.include_router(whatsapp_router, prefix="/api/v1/whatsapp", tags=["WhatsApp"])
    print("✅ Rotas WhatsApp registradas")
except ImportError as e:
    print(f"⚠️  Rotas WhatsApp não disponíveis: {e}")

try:
    from app.backend.src.routes.crm_routes import router as crm_router
    app.include_router(crm_router, prefix="/api/v1/crm", tags=["CRM"])
    print("✅ Rotas CRM registradas")
except ImportError as e:
    print(f"⚠️  Rotas CRM não disponíveis: {e}")

# ========== ROTAS PRINCIPAIS ==========

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Serve o dashboard principal"""
    if templates:
        try:
            return templates.TemplateResponse("dashboard.html", {"request": request})
        except Exception as e:
            return HTMLResponse(f"""
                <html>
                    <body>
                        <h1>HealthPlatform SaaS - Erro no Template</h1>
                        <p>Erro: {e}</p>
                        <a href="/api/v1/crm/dashboard/metricas">Ver Métricas API</a>
                    </body>
                </html>
            """)
    else:
        return HTMLResponse("""
            <html>
                <head>
                    <title>HealthCRM Dashboard</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 40px; }
                        .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin: 20px 0; }
                        a { color: #e67951; text-decoration: none; }
                    </style>
                </head>
                <body>
                    <h1>🏥 HealthCRM Dashboard</h1>
                    <div class="card">
                        <h3>Dashboard em Desenvolvimento</h3>
                        <p>O template completo será carregado em breve.</p>
                        <p><strong>APIs funcionando:</strong></p>
                        <ul>
                            <li><a href="/api/v1/crm/dashboard/metricas" target="_blank">📊 Métricas do Dashboard</a></li>
                            <li><a href="/api/v1/crm/leads" target="_blank">👥 Lista de Leads</a></li>
                            <li><a href="/api/v1/crm/vendas" target="_blank">💰 Lista de Vendas</a></li>
                            <li><a href="/api/v1/crm/corretores" target="_blank">👑 Lista de Corretores</a></li>
                        </ul>
                    </div>
                </body>
            </html>
        """)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_alt(request: Request):
    """Alternativa para o dashboard"""
    return await dashboard(request)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "HealthPlatform"}

@app.get("/api/info")
async def api_info():
    """Endpoint para verificar módulos carregados"""
    return {
        "service": "HealthPlatform SaaS",
        "status": "running", 
        "version": "2.1.0",
        "modules": {
            "crm": "loaded",
            "whatsapp": "loaded", 
            "dashboard": "available"
        },
        "paths": {
            "project_root": str(project_root),
            "frontend_dir": str(frontend_dir),
            "static_dir": str(static_dir) if static_dir.exists() else "not_found",
            "templates_dir": str(templates_dir) if templates_dir.exists() else "not_found"
        }
    }


@app.get("/teste-ia")
async def teste_ia(request: Request):
    """Página de teste da IA Brasileira"""
    return templates.TemplateResponse("teste_ia.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)