# app/backend/src/core/modules/finance/comissoes_service.py
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

class ComissoesService:
    def __init__(self, db: Session):
        self.db = db
    
    async def calcular_comissao_venda(self, venda_data: Dict) -> Dict:
        """Calcula comissão para uma venda específica"""
        try:
            # Regras de comissão por tipo de plano
            regras_comissao = {
                "INDIVIDUAL": 15.0,  # 15%
                "FAMILIAR": 12.0,    # 12%  
                "EMPRESARIAL": 10.0, # 10%
                "VIP": 8.0           # 8%
            }
            
            plano = venda_data.get("plano_vendido", "INDIVIDUAL")
            valor_venda = venda_data.get("valor_venda", 0)
            percentual_corretor = venda_data.get("percentual_corretor", regras_comissao.get(plano, 10.0))
            
            # Calcular comissão
            valor_comissao = (valor_venda * percentual_corretor) / 100
            
            logger.info(f"💰 Comissão calculada: {plano} - R$ {valor_venda} -> R$ {valor_comissao} ({percentual_corretor}%)")
            
            return {
                "valor_comissao": round(valor_comissao, 2),
                "percentual_comissao": percentual_corretor,
                "plano": plano,
                "valor_venda": valor_venda
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular comissão: {e}")
            return {"valor_comissao": 0, "percentual_comissao": 0}
    
    async def registrar_venda(self, venda_data: Dict) -> Dict:
        """Registra uma nova venda e calcula comissão"""
        try:
            # Calcular comissão
            comissao_calculada = await self.calcular_comissao_venda(venda_data)
            
            # Aqui você registraria no database
            venda_registrada = {
                "id": 1,  # Simulado - em produção viria do DB
                **venda_data,
                **comissao_calculada,
                "data_venda": datetime.utcnow().isoformat(),
                "status": "pendente"
            }
            
            logger.info(f"✅ Venda registrada: Corretor {venda_data.get('corretor_id')} - R$ {comissao_calculada['valor_comissao']}")
            
            return venda_registrada
            
        except Exception as e:
            logger.error(f"❌ Erro ao registrar venda: {e}")
            return {}
    
    async def calcular_comissoes_mes(self, corretor_id: int, mes_referencia: str = None) -> Dict:
        """Calcula comissões totais do mês para um corretor"""
        if not mes_referencia:
            mes_referencia = datetime.utcnow().strftime("%Y-%m")
        
        # Simulação - em produção buscaria do database
        comissoes_mes = {
            "corretor_id": corretor_id,
            "mes_referencia": mes_referencia,
            "total_vendas": 15000.00,
            "total_comissao": 1800.00,
            "quantidade_vendas": 8,
            "vendas": [
                {"plano": "FAMILIAR", "valor": 2000.00, "comissao": 240.00},
                {"plano": "EMPRESARIAL", "valor": 5000.00, "comissao": 500.00},
                {"plano": "VIP", "valor": 3000.00, "comissao": 240.00},
            ]
        }
        
        logger.info(f"📊 Comissões do mês {mes_referencia}: R$ {comissoes_mes['total_comissao']}")
        
        return comissoes_mes
    
    async def listar_corretores(self) -> List[Dict]:
        """Lista todos os corretores ativos"""
        # Simulação - em produção buscaria da tabela brokers
        corretores = [
            {"id": 1, "nome": "Bruna Mamedes", "percentual_comissao": 12.0, "ativo": True},
            {"id": 2, "nome": "Maiara Andrade", "percentual_comissao": 10.0, "ativo": True},
            {"id": 3, "nome": "Fernando Diamantino", "percentual_comissao": 15.0, "ativo": True},
        ]
        
        return corretores