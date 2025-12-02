# app/backend/src/core/modules/finance/service.py - VERSÃO SIMPLIFICADA
import aiosqlite
from datetime import datetime
from typing import List, Dict, Optional
from ...database import DATABASE_PATH

class FinanceService:
    def __init__(self, db_path=None):
        self.db_path = db_path or DATABASE_PATH
    
    async def initialize(self):
        """Inicializa o serviço financeiro"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("SELECT 1")
            print("✅ Finance Service inicializado")
            return True
        except Exception as e:
            print(f"❌ Finance Service: {e}")
            return False
    
    async def get_vendas_mensais(self) -> List[Dict]:
        """Obtém vendas mensais para gráficos"""
        query = """
        SELECT 
            strftime('%Y-%m', data_venda) as mes,
            COUNT(*) as vendas,
            COALESCE(SUM(valor_total), 0) as faturamento
        FROM vendas
        WHERE status = 'pago'
        GROUP BY strftime('%Y-%m', data_venda)
        ORDER BY mes DESC
        LIMIT 12
        """
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(query)
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Erro ao buscar vendas mensais: {e}")
            # Dados de exemplo
            return [
                {"mes": "2024-01", "vendas": 15, "faturamento": 22500},
                {"mes": "2024-02", "vendas": 22, "faturamento": 33000},
                {"mes": "2024-03", "vendas": 18, "faturamento": 27000}
            ]
    
    async def get_vendas(self, mes: str = None, corretor_id: int = None) -> List[Dict]:
        """Lista vendas com filtros"""
        query = """
        SELECT 
            v.*,
            c.nome as cliente_nome,
            u.nome as corretor_nome
        FROM vendas v
        LEFT JOIN clientes c ON v.cliente_id = c.id
        LEFT JOIN usuarios u ON v.corretor_id = u.id
        WHERE 1=1
        """
        params = []
        
        if mes:
            query += " AND strftime('%Y-%m', v.data_venda) = ?"
            params.append(mes)
        
        if corretor_id:
            query += " AND v.corretor_id = ?"
            params.append(corretor_id)
        
        query += " ORDER BY v.data_venda DESC"
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(query, params)
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Erro ao buscar vendas: {e}")
            return []