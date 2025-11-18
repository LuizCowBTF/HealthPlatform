# app/backend/src/main.py - VERSÃO SIMPLIFICADA E FUNCIONAL
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
import os
from pathlib import Path

# Configurar paths CORRETAMENTE
current_dir = Path(__file__).parent  # app/backend/src/
project_root = current_dir.parent.parent.parent  # HealthPlatform/
frontend_dir = project_root / "app" / "frontend"

app = FastAPI(title="Health Platform", version="1.0.0")

print(f"📁 Project Root: {project_root}")
print(f"📁 Frontend Dir: {frontend_dir}")

# Servir arquivos estáticos - CORRIGIDO
static_dir = frontend_dir / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    print("✅ Arquivos estáticos montados")
else:
    print(f"❌ Pasta static não encontrada: {static_dir}")

# Configurar templates - CORRIGIDO
templates_dir = frontend_dir / "templates"
if templates_dir.exists():
    templates = Jinja2Templates(directory=str(templates_dir))
    print("✅ Templates carregados")
else:
    print(f"❌ Pasta templates não encontrada: {templates_dir}")
    templates = None

# ========== ROTAS PRINCIPAIS (SIMPLIFICADAS) ==========

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Página inicial - Dashboard"""
    return await serve_template("dashboard.html", request)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard principal"""
    return await serve_template("dashboard.html", request)

@app.get("/comissoes", response_class=HTMLResponse)
async def comissoes(request: Request):
    """Página de comissões"""
    return await serve_template("comissoes.html", request)

@app.get("/clientes", response_class=HTMLResponse)
async def clientes(request: Request):
    """Página de clientes (placeholder)"""
    return await serve_template("dashboard.html", request)  # Usar dashboard como fallback

@app.get("/leads", response_class=HTMLResponse)
async def leads(request: Request):
    """Página de leads (placeholder)"""
    return await serve_template("dashboard.html", request)  # Usar dashboard como fallback

@app.get("/relatorios", response_class=HTMLResponse)
async def relatorios(request: Request):
    """Página de relatórios (placeholder)"""
    return await serve_template("dashboard.html", request)  # Usar dashboard como fallback

async def serve_template(template_name: str, request: Request):
    """Serve templates com fallback"""
    if templates:
        try:
            return templates.TemplateResponse(template_name, {"request": request})
        except Exception as e:
            return HTMLResponse(f"""
                <html>
                    <body>
                        <h1>HealthPlatform - Template Error</h1>
                        <p>Erro ao carregar {template_name}: {e}</p>
                        <a href="/">Voltar ao Dashboard</a>
                    </body>
                </html>
            """)
    else:
        return HTMLResponse(f"""
            <html>
                <body>
                    <h1>HealthPlatform</h1>
                    <p>Template {template_name} não disponível.</p>
                    <a href="/">Dashboard</a> | 
                    <a href="/comissoes">Comissões</a>
                </body>
            </html>
        """)

# ========== ROTAS API (CARREGAMENTO CONDICIONAL) ==========

# Tentar carregar rotas de forma segura
try:
    from app.backend.src.routes.ia_routes import router as ia_router
    app.include_router(ia_router, prefix="/api/v1/ia", tags=["IA"])
    print("✅ Rotas IA carregadas")
except ImportError as e:
    print(f"⚠️  Rotas IA não disponíveis: {e}")

try:
    from app.backend.src.routes.crm_routes import router as crm_router
    app.include_router(crm_router, prefix="/api/v1/crm", tags=["CRM"])
    print("✅ Rotas CRM carregadas")
except ImportError as e:
    print(f"⚠️  Rotas CRM não disponíveis: {e}")

try:
    from app.backend.src.routes.whatsapp_webhook import router as whatsapp_router
    app.include_router(whatsapp_router, prefix="/api/v1/whatsapp", tags=["WhatsApp"])
    print("✅ Rotas WhatsApp carregadas")
except ImportError as e:
    print(f"⚠️  Rotas WhatsApp não disponíveis: {e}")

# Rotas opcionais - com fallback
try:
    from app.backend.src.routes.comissoes_routes import router as comissoes_router
    app.include_router(comissoes_router, prefix="/api/v1/comissoes", tags=["Comissões"])
    print("✅ Rotas Comissões carregadas")
except ImportError as e:
    print(f"⚠️  Rotas Comissões não disponíveis: {e}")

# ========== ENDPOINTS BÁSICOS ==========

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "HealthPlatform"}

@app.get("/api/info")
async def api_info():
    return {
        "service": "HealthPlatform",
        "status": "running", 
        "version": "2.1.0",
        "endpoints": {
            "dashboard": "/",
            "comissoes": "/comissoes", 
            "clientes": "/clientes",
            "leads": "/leads",
            "relatorios": "/relatorios",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)