# app/backend/src/modules/crm/service.py
from sqlalchemy.orm import Session
from . import models

class CRMService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_dashboard_data(self, broker_id: int = None):
        # KPIs do CRM
        total_leads = self.db.query(models.Lead).count()
        total_sales = self.db.query(models.Sale).filter(models.Sale.status == "completed").count()
        
        # Cálculo de receita
        revenue_result = self.db.query(func.sum(models.Sale.value)).filter(
            models.Sale.status == "completed"
        ).first()
        total_revenue = revenue_result[0] or 0
        
        # Taxa de conversão
        conversion_rate = (total_sales / total_leads * 100) if total_leads > 0 else 0
        
        return {
            "total_leads": total_leads,
            "total_sales": total_sales,
            "total_revenue": total_revenue,
            "conversion_rate": round(conversion_rate, 2)
        }
    
    def create_lead(self, lead_data: dict):
        lead = models.Lead(**lead_data)
        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)
        return lead