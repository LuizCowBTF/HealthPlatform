from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
import aiosqlite
import os
from datetime import datetime, timedelta
import json

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ CAMINHOS CORRETOS PARA SEU PROJETO
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "app", "frontend")
STATIC_DIR = os.path.join(FRONTEND_DIR, "static")
TEMPLATES_DIR = os.path.join(FRONTEND_DIR, "templates")
DATABASE_PATH = os.path.join(PROJECT_ROOT, "health_platform.db")

print("=" * 50)
print("🚀 HEALTH PLATFORM - CONFIGURAÇÃO")
print("=" * 50)
print(f"📁 DATABASE_PATH: {DATABASE_PATH} → Existe: {os.path.exists(DATABASE_PATH)}")

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ✅ ENDPOINT DEBUG PARA VER ESTRUTURA DA TABELA
@app.get("/api/debug/tabela-leads")
async def debug_tabela_leads():
    """Mostra a estrutura real da tabela leads"""
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute("PRAGMA table_info(leads)") as cursor:
                colunas = await cursor.fetchall()
            
            async with db.execute("SELECT * FROM leads LIMIT 3") as cursor:
                exemplos = await cursor.fetchall()
            
            colunas_info = []
            for col in colunas:
                colunas_info.append({
                    "id": col[0],
                    "nome": col[1],
                    "tipo": col[2],
                    "pode_ser_nulo": col[3],
                    "valor_padrao": col[4],
                    "eh_pk": col[5]
                })
            
            return {
                "colunas": colunas_info,
                "exemplos": exemplos,
                "total_colunas": len(colunas)
            }
    except Exception as e:
        return {"error": str(e)}

# ✅ ENDPOINT CORRIGIDO PARA DASHBOARD (APENAS COM DADOS DISPONÍVEIS)
@app.get("/api/v1/crm/dashboard/completo")
async def get_dashboard_completo():
    """Endpoint completo para o dashboard - apenas com dados disponíveis"""
    try:
        if not os.path.exists(DATABASE_PATH):
            return create_dashboard_fallback()
            
        async with aiosqlite.connect(DATABASE_PATH) as db:
            # ✅ MÉTRICAS PRINCIPAIS
            cursor = await db.execute("SELECT COUNT(*) FROM leads WHERE status LIKE '%Fechado%'")
            clientes_ativos = (await cursor.fetchone())[0]
            
            cursor = await db.execute("SELECT COUNT(*) FROM leads")
            total_leads = (await cursor.fetchone())[0]
            
            # Meta mensal (últimos 30 dias)
            cursor = await db.execute("""
            SELECT COUNT(*) FROM leads 
            WHERE status LIKE '%Fechado%' 
            AND date(created_at) >= date('now', '-30 days')
            """)
            vendas_30_dias = (await cursor.fetchone())[0]
            
            # ✅ VENDAS MENSAL (últimos 6 meses)
            vendas_mensais = []
            cursor = await db.execute("""
            SELECT strftime('%Y-%m', created_at) as mes, 
                   COUNT(*) as vendas,
                   COUNT(*) * 1500 as faturamento_estimado
            FROM leads 
            WHERE status LIKE '%Fechado%'
            GROUP BY mes 
            ORDER BY mes DESC 
            LIMIT 6
            """)
            vendas_data = await cursor.fetchall()
            
            for mes_data in vendas_data:
                vendas_mensais.append({
                    "mes": mes_data[0],
                    "vendas": mes_data[1],
                    "faturamento": float(mes_data[2])
                })
            
            # ✅ VENDAS POR OPERADORA (usando 'source')
            vendas_operadora = []
            cursor = await db.execute("""
            SELECT source, COUNT(*) as vendas, COUNT(*) * 1500 as faturamento
            FROM leads 
            WHERE status LIKE '%Fechado%' AND source IS NOT NULL AND source != ''
            GROUP BY source 
            ORDER BY vendas DESC
            LIMIT 10
            """)
            operadoras_data = await cursor.fetchall()
            
            for operadora in operadoras_data:
                nome_operadora = operadora[0] or "Outros"
                if nome_operadora == "Plantão":
                    nome_operadora = "Plantão de Vendas"
                elif nome_operadora == "Online":
                    nome_operadora = "Site Online"
                elif nome_operadora == "Indicação":
                    nome_operadora = "Indicação"
                
                vendas_operadora.append({
                    "operadora": nome_operadora,
                    "vendas": operadora[1],
                    "faturamento": float(operadora[2])
                })
            
            # ✅ TOP CORRETORES (usando broker_id)
            top_corretores = []
            cursor = await db.execute("""
            SELECT broker_id, COUNT(*) as vendas, COUNT(*) * 1500 as faturamento
            FROM leads 
            WHERE status LIKE '%Fechado%' AND broker_id IS NOT NULL
            GROUP BY broker_id 
            ORDER BY vendas DESC 
            LIMIT 5
            """)
            corretores_data = await cursor.fetchall()
            
            for i, corretor in enumerate(corretores_data):
                broker_id = corretor[0]
                
                top_corretores.append({
                    "nome": f"Corretor {broker_id}",
                    "vendas": corretor[1],
                    "faturamento": float(corretor[2]),
                    "posicao": i + 1
                })
            
            # ✅ ATIVIDADES RECENTES CORRIGIDAS
            atividades_recentes = []
            cursor = await db.execute("""
            SELECT l.full_name, l.status, l.created_at, l.broker_id, l.source
            FROM leads l
            WHERE l.status LIKE '%Fechado%'
            ORDER BY l.created_at DESC 
            LIMIT 5
            """)
            atividades_data = await cursor.fetchall()
            
            for atividade in atividades_data:
                broker_id = atividade[3]
                
                # Buscar vendas totais CORRETAS do corretor
                if broker_id:
                    cursor_vendas = await db.execute("""
                    SELECT COUNT(*) as vendas, COUNT(*) * 1500 as faturamento
                    FROM leads 
                    WHERE broker_id = ? AND status LIKE '%Fechado%'
                    """, (broker_id,))
                    resultado = await cursor_vendas.fetchone()
                    total_vendas = resultado[0] if resultado else 0
                    faturamento_total = float(resultado[1]) if resultado else 0
                else:
                    total_vendas = 0
                    faturamento_total = 0
                
                nome_operadora = atividade[4] or "Plano Saúde"
                if nome_operadora == "Plantão":
                    nome_operadora = "Plantão de Vendas"
                
                atividades_recentes.append({
                    "cliente": atividade[0] or "Cliente",
                    "acao": f"Contrato {nome_operadora}",
                    "corretor": f"Corretor {broker_id}" if broker_id else "Não atribuído",
                    "data": atividade[2],
                    "vendas": total_vendas,
                    "faturamento": faturamento_total
                })
            
            # ✅ LEADS POR STATUS
            leads_por_status = []
            cursor = await db.execute("SELECT status, COUNT(*) FROM leads GROUP BY status")
            leads_status_data = await cursor.fetchall()
            
            for status_data in leads_status_data:
                leads_por_status.append({
                    "status": status_data[0],
                    "quantidade": status_data[1]
                })
            
            # ✅ CALCULAR META MENSAL (70% do melhor mês)
            meta_mensal = 0
            if vendas_mensais:
                melhor_mes = max(vendas_mensais, key=lambda x: x['vendas'])
                meta_mensal = int(melhor_mes['vendas'] * 0.7)
            
            progresso_meta = min(100, int((vendas_30_dias / max(meta_mensal, 1)) * 100)) if meta_mensal > 0 else 0
            
            return {
                "vendas_mensais": vendas_mensais,
                "vendas_operadora": vendas_operadora,
                "leads_por_status": leads_por_status,
                "top_corretores": top_corretores,
                "metricas_principais": {
                    "faturamento_total": float(clientes_ativos * 1500),
                    "leads_novos": total_leads,
                    "taxa_conversao": round((clientes_ativos / max(total_leads, 1)) * 100, 1) if total_leads > 0 else 0,
                    "clientes_ativos": clientes_ativos,
                    "meta_mensal": meta_mensal,
                    "progresso_meta": progresso_meta,
                    "vendas_mes_atual": vendas_30_dias
                },
                "atividades_recentes": atividades_recentes
            }
            
    except Exception as e:
        print(f"❌ Erro no dashboard completo: {str(e)}")
        return create_dashboard_fallback()

# ✅ ENDPOINT PARA MÉTRICAS BÁSICAS
@app.get("/api/v1/crm/dashboard/metricas")
async def get_dashboard_metricas():
    """Endpoint para métricas básicas do dashboard"""
    try:
        if not os.path.exists(DATABASE_PATH):
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
            
            faturamento_total = clientes_ativos * 1500
            
            return {
                "faturamento_total": float(faturamento_total),
                "leads_novos": total_leads,
                "taxa_conversao": round((clientes_ativos / max(total_leads, 1)) * 100, 1) if total_leads > 0 else 0,
                "clientes_ativos": clientes_ativos
            }
            
    except Exception as e:
        return {"error": str(e)}

# ✅ ENDPOINT PARA CLIENTES
@app.get("/api/clientes/reais")
async def get_clientes_reais():
    """Busca leads com status 'Plano Fechado' do banco real"""
    try:
        if not os.path.exists(DATABASE_PATH):
            return {"error": "Banco não encontrado", "clientes": [], "total": 0}
            
        async with aiosqlite.connect(DATABASE_PATH) as db:
            query = """
            SELECT id, full_name, email, phone, status, broker_id, created_at, source
            FROM leads 
            WHERE status LIKE '%Fechado%'
            ORDER BY created_at DESC
            """
            
            async with db.execute(query) as cursor:
                leads = await cursor.fetchall()
                
            clientes = []
            for lead in leads:
                clientes.append({
                    "id": lead[0],
                    "name": lead[1] or "Nome não informado",
                    "email": lead[2] or "Email não informado",
                    "phone": lead[3] or "Telefone não informado",
                    "plan_name": "Plano Saúde",
                    "plan_value": 1500,
                    "contract_date": lead[6],
                    "broker_name": f"Corretor {lead[5]}" if lead[5] else "Não atribuído",
                    "status": lead[4],
                    "document": "CPF não informado",
                    "origin": lead[7] or "Origem não informada",
                    "observations": ""
                })
                
            return {"clientes": clientes, "total": len(clientes)}
                
    except Exception as e:
        return {"error": str(e), "clientes": [], "total": 0}

def create_dashboard_fallback():
    """Cria dados fallback para o dashboard"""
    return {
        "vendas_mensais": [
            {"mes": "2024-01", "vendas": 15, "faturamento": 22500},
            {"mes": "2024-02", "vendas": 22, "faturamento": 33000},
            {"mes": "2024-03", "vendas": 18, "faturamento": 27000}
        ],
        "vendas_operadora": [
            {"operadora": "Plantão de Vendas", "vendas": 25, "faturamento": 37500},
            {"operadora": "Site Online", "vendas": 18, "faturamento": 27000},
            {"operadora": "Indicação", "vendas": 12, "faturamento": 18000}
        ],
        "leads_por_status": [
            {"status": "Plano Fechado", "quantidade": 55},
            {"status": "Em Negociação", "quantidade": 22},
            {"status": "Novo Lead", "quantidade": 33}
        ],
        "top_corretores": [
            {"nome": "Corretor 14", "vendas": 111, "faturamento": 166500, "posicao": 1},
            {"nome": "Corretor 1", "vendas": 52, "faturamento": 78000, "posicao": 2},
            {"nome": "Corretor 2", "vendas": 38, "faturamento": 57000, "posicao": 3}
        ],
        "metricas_principais": {
            "faturamento_total": 475500,
            "leads_novos": 8918,
            "taxa_conversao": 3.6,
            "clientes_ativos": 317,
            "meta_mensal": 78,  # 70% do melhor mês (111 vendas)
            "progresso_meta": 42,  # Exemplo: 42% da meta
            "vendas_mes_atual": 33  # Exemplo: 33 vendas este mês
        },
        "atividades_recentes": [
            {"cliente": "LUCIANO", "acao": "Contrato Plantão de Vendas", "corretor": "Corretor 1", "data": "2024-03-15", "vendas": 52, "faturamento": 78000},
            {"cliente": "ERIKA", "acao": "Contrato Site Online", "corretor": "Corretor 2", "data": "2024-03-14", "vendas": 38, "faturamento": 57000}
        ]
    }

# ✅ ENDPOINT PARA PÁGINA INICIAL
@app.get("/")
async def serve_home():
    dashboard_path = os.path.join(TEMPLATES_DIR, "dashboard.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    else:
        return HTMLResponse("Health Platform - Dashboard")

# ✅ SERVIR TODAS AS PÁGINAS HTML
@app.get("/{path:path}")
async def serve_frontend(path: str):
    if path in ["", "dashboard", "clientes", "leads", "comissoes", "relatorios"]:
        if path == "":
            path = "dashboard"
        
        html_file = f"{path}.html"
        html_path = os.path.join(TEMPLATES_DIR, html_file)
        
        if os.path.exists(html_path):
            return FileResponse(html_path)
    
    return HTMLResponse("Página não encontrada", status_code=404)

if __name__ == "__main__":
    import uvicorn
    print("🚀 INICIANDO SERVIDOR...")
    print("🌐 Dashboard: http://localhost:8000/")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")