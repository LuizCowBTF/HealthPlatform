# app/backend/src/core/modules/crm/service.py - ATUALIZADO
import aiosqlite
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from ...database import DATABASE_PATH

class CRMService:
    def __init__(self):
        self.db_path = DATABASE_PATH
    
    async def initialize(self):
        """Inicializa o serviço CRM"""
        print("🔄 Inicializando CRM Service...")
        # Testar conexão com banco
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("SELECT 1")
            print("✅ CRM Service: OK")
            return True
        except Exception as e:
            print(f"❌ CRM Service: {e}")
            return False
    
    async def get_leads(self, status: Optional[str] = None, corretor_id: Optional[int] = None) -> List[Dict]:
        """Obtém leads com filtros opcionais"""
        query = "SELECT * FROM leads WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if corretor_id:
            query += " AND corretor_id = ?"
            params.append(corretor_id)
        
        query += " ORDER BY data_criacao DESC"
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(query, params)
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Erro ao buscar leads: {e}")
            return []
    
    async def create_lead(self, lead_data: Dict) -> Dict:
        """Cria um novo lead"""
        required_fields = ['nome', 'email', 'telefone']
        for field in required_fields:
            if field not in lead_data:
                raise ValueError(f"Campo obrigatório faltando: {field}")
        
        fields = []
        values = []
        placeholders = []
        
        for field, value in lead_data.items():
            fields.append(field)
            values.append(value)
            placeholders.append("?")
        
        fields.append("data_criacao")
        values.append(datetime.now().isoformat())
        placeholders.append("?")
        
        query = f"""
        INSERT INTO leads ({', '.join(fields)})
        VALUES ({', '.join(placeholders)})
        """
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(query, values)
                await db.commit()
                
                # Retornar lead criado
                lead_id = cursor.lastrowid
                return await self.get_lead_by_id(lead_id)
        except Exception as e:
            raise Exception(f"Erro ao criar lead: {e}")
    
    async def get_lead_by_id(self, lead_id: int) -> Optional[Dict]:
        """Obtém um lead pelo ID"""
        query = "SELECT * FROM leads WHERE id = ?"
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(query, (lead_id,))
                row = await cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            print(f"Erro ao buscar lead {lead_id}: {e}")
            return None
    
    async def get_metricas_principais(self, corretor_id: Optional[int] = None) -> Dict:
        """Calcula métricas principais para dashboard"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Total de leads
                query_leads = "SELECT COUNT(*) FROM leads"
                params = []
                
                if corretor_id:
                    query_leads += " WHERE corretor_id = ?"
                    params.append(corretor_id)
                
                cursor = await db.execute(query_leads, params)
                total_leads = (await cursor.fetchone())[0]
                
                # Leads fechados (clientes)
                query_fechados = "SELECT COUNT(*) FROM leads WHERE status = 'fechado'"
                if corretor_id:
                    query_fechados += " AND corretor_id = ?"
                
                cursor = await db.execute(query_fechados, params)
                leads_fechados = (await cursor.fetchone())[0]
                
                # Taxa de conversão
                taxa_conversao = round((leads_fechados / max(total_leads, 1)) * 100, 2) if total_leads > 0 else 0
                
                # Vendas do mês atual
                mes_atual = datetime.now().strftime("%Y-%m")
                query_vendas = """
                SELECT COUNT(*) FROM vendas 
                WHERE strftime('%Y-%m', data_venda) = ?
                """
                if corretor_id:
                    query_vendas += " AND corretor_id = ?"
                    cursor = await db.execute(query_vendas, (mes_atual, corretor_id))
                else:
                    cursor = await db.execute(query_vendas, (mes_atual,))
                
                vendas_mes_atual = (await cursor.fetchone())[0]
                
                # Faturamento total (estimado)
                query_faturamento = """
                SELECT COALESCE(SUM(valor_total), 0) FROM vendas 
                WHERE status = 'pago'
                """
                if corretor_id:
                    query_faturamento += " AND corretor_id = ?"
                    cursor = await db.execute(query_faturamento, (corretor_id,))
                else:
                    cursor = await db.execute(query_faturamento)
                
                faturamento_total = (await cursor.fetchone())[0] or 0
                
                return {
                    "total_leads": total_leads,
                    "leads_fechados": leads_fechados,
                    "taxa_conversao": taxa_conversao,
                    "vendas_mes_atual": vendas_mes_atual,
                    "faturamento_total": float(faturamento_total),
                    "clientes_ativos": leads_fechados,
                    "meta_mensal": 50,  # Exemplo
                    "progresso_meta": min(100, int((vendas_mes_atual / 50) * 100)) if 50 > 0 else 0
                }
                
        except Exception as e:
            print(f"Erro ao calcular métricas: {e}")
            return {
                "total_leads": 0,
                "leads_fechados": 0,
                "taxa_conversao": 0,
                "vendas_mes_atual": 0,
                "faturamento_total": 0,
                "clientes_ativos": 0,
                "meta_mensal": 0,
                "progresso_meta": 0
            }
    
    async def get_leads_por_status(self, corretor_id: Optional[int] = None) -> List[Dict]:
        """Agrupa leads por status"""
        query = """
        SELECT status, COUNT(*) as quantidade 
        FROM leads 
        WHERE 1=1
        """
        params = []
        
        if corretor_id:
            query += " AND corretor_id = ?"
            params.append(corretor_id)
        
        query += " GROUP BY status ORDER BY quantidade DESC"
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(query, params)
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Erro ao buscar leads por status: {e}")
            return []
    
    async def get_top_corretores(self, limit: int = 5) -> List[Dict]:
        """Obtém top corretores por vendas"""
        query = """
        SELECT 
            u.id as corretor_id,
            u.nome as corretor_nome,
            COUNT(v.id) as total_vendas,
            COALESCE(SUM(v.valor_total), 0) as valor_vendas,
            COALESCE(SUM(c.valor_comissao), 0) as total_comissoes
        FROM usuarios u
        LEFT JOIN vendas v ON u.id = v.corretor_id
        LEFT JOIN comissoes c ON v.id = c.venda_id
        WHERE u.tipo = 'corretor'
        GROUP BY u.id, u.nome
        ORDER BY valor_vendas DESC
        LIMIT ?
        """
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(query, (limit,))
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Erro ao buscar top corretores: {e}")
            return []
    
    async def get_atividades_recentes(self, limit: int = 10) -> List[Dict]:
        """Obtém atividades recentes do sistema"""
        query = """
        SELECT 
            'lead' as tipo,
            l.id,
            l.nome,
            l.status,
            l.data_criacao as data,
            u.nome as corretor_nome
        FROM leads l
        LEFT JOIN usuarios u ON l.corretor_id = u.id
        
        UNION ALL
        
        SELECT 
            'venda' as tipo,
            v.id,
            c.nome,
            v.status,
            v.data_venda as data,
            u.nome as corretor_nome
        FROM vendas v
        JOIN clientes c ON v.cliente_id = c.id
        JOIN usuarios u ON v.corretor_id = u.id
        
        ORDER BY data DESC
        LIMIT ?
        """
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(query, (limit,))
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Erro ao buscar atividades recentes: {e}")
            return []