# app/backend/src/core/modules/finance/comissoes_service.py - VERSÃO SIMPLIFICADA
import aiosqlite
from datetime import datetime
from typing import List, Dict, Optional
from ...database import DATABASE_PATH

class ComissoesService:
    def __init__(self, db_path=None):
        self.db_path = db_path or DATABASE_PATH
    
    async def initialize(self):
        """Inicializa o serviço de comissões"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("SELECT 1")
            print("✅ Comissões Service inicializado")
            return True
        except Exception as e:
            print(f"❌ Comissões Service: {e}")
            return False
    
    async def get_comissoes(self, corretor_id: int = None, status: str = None) -> List[Dict]:
        """Lista comissões com filtros"""
        query = """
        SELECT 
            c.*,
            v.valor_total,
            v.produto,
            u.nome as corretor_nome
        FROM comissoes c
        LEFT JOIN vendas v ON c.venda_id = v.id
        LEFT JOIN usuarios u ON c.corretor_id = u.id
        WHERE 1=1
        """
        params = []
        
        if corretor_id:
            query += " AND c.corretor_id = ?"
            params.append(corretor_id)
        
        if status:
            query += " AND c.status = ?"
            params.append(status)
        
        query += " ORDER BY c.data_calculo DESC"
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(query, params)
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Erro ao buscar comissões: {e}")
            return []
    
    async def calcular_comissoes_mes(self, mes_ano: str) -> Dict:
        """Calcula comissões para um mês específico"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Buscar vendas do mês
                query_vendas = """
                SELECT 
                    v.id as venda_id,
                    v.corretor_id,
                    v.valor_total,
                    v.comissao_percentual,
                    u.nome as corretor_nome
                FROM vendas v
                LEFT JOIN usuarios u ON v.corretor_id = u.id
                WHERE strftime('%Y-%m', v.data_venda) = ?
                AND v.status = 'pago'
                """
                
                cursor = await db.execute(query_vendas, (mes_ano,))
                vendas = await cursor.fetchall()
                
                resultados = []
                total_comissoes = 0
                
                for venda in vendas:
                    venda_id = venda[0]
                    corretor_id = venda[1]
                    valor_total = venda[2]
                    percentual = venda[3] or 10.0  # Default 10%
                    corretor_nome = venda[4]
                    
                    valor_comissao = valor_total * (percentual / 100)
                    total_comissoes += valor_comissao
                    
                    # Verificar se comissão já existe
                    query_existe = "SELECT id FROM comissoes WHERE venda_id = ?"
                    cursor_existe = await db.execute(query_existe, (venda_id,))
                    existe = await cursor_existe.fetchone()
                    
                    if not existe:
                        # Inserir nova comissão
                        query_inserir = """
                        INSERT INTO comissoes (venda_id, corretor_id, valor_comissao, status)
                        VALUES (?, ?, ?, 'pendente')
                        """
                        await db.execute(query_inserir, (venda_id, corretor_id, valor_comissao))
                    
                    resultados.append({
                        "venda_id": venda_id,
                        "corretor_nome": corretor_nome,
                        "valor_venda": valor_total,
                        "percentual": percentual,
                        "valor_comissao": valor_comissao
                    })
                
                await db.commit()
                
                return {
                    "mes": mes_ano,
                    "vendas_processadas": len(vendas),
                    "total_comissoes": total_comissoes,
                    "detalhes": resultados
                }
                
        except Exception as e:
            print(f"Erro ao calcular comissões: {e}")
            return {"error": str(e)}