# app/backend/src/modules/finance/service.py
from sqlalchemy.orm import Session
from app.backend.src.modules.crm import models

class FinanceService:
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_commissions(self, broker_id: int = None):
        """Calcula comissões para todos os corretores ou um específico"""
        query = self.db.query(
            models.Broker.id,
            models.Broker.name,
            func.sum(models.Sale.commission_value).label('total_commission')
        ).join(
            models.Sale, models.Sale.broker_id == models.Broker.id
        ).filter(
            models.Sale.status == "completed"
        )
        
        if broker_id:
            query = query.filter(models.Broker.id == broker_id)
        
        results = query.group_by(models.Broker.id, models.Broker.name).all()
        
        commissions = []
        for broker_id, broker_name, total_commission in results:
            commissions.append({
                "broker_id": broker_id,
                "broker_name": broker_name,
                "total_commission": total_commission or 0,
                "commission_rate": 0.10,  # 10% padrão
                "payable_amount": (total_commission or 0) * 0.10
            })
        
        return commissions
    
    def get_financial_report(self, start_date, end_date):
        """Relatório financeiro completo"""
        sales_in_period = self.db.query(models.Sale).filter(
            models.Sale.status == "completed",
            models.Sale.sale_date >= start_date,
            models.Sale.sale_date <= end_date
        ).all()
        
        total_revenue = sum(sale.value for sale in sales_in_period)
        total_commissions = sum(sale.commission_value for sale in sales_in_period)
        
        return {
            "period": f"{start_date} to {end_date}",
            "total_revenue": total_revenue,
            "total_commissions": total_commissions,
            "net_profit": total_revenue - total_commissions,
            "sales_count": len(sales_in_period),
            "average_ticket": total_revenue / len(sales_in_period) if sales_in_period else 0
        }