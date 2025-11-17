# app/backend/src/modules/ai/service.py
import openai
from typing import Dict, Optional
from app.backend.src.core.config import settings

class AIService:
    def __init__(self):
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
        self.client = openai
    
    async def analyze_lead_sentiment(self, message: str) -> Dict:
        """Analisa sentimento do lead baseado na mensagem"""
        try:
            if not self.client.api_key:
                return {"score": 0.5, "sentiment": "neutral"}
            
            prompt = f"""
            Analise o sentimento desta mensagem de um lead e retorne um JSON:
            Mensagem: "{message}"
            
            Retorne: {{"score": 0.0 a 1.0, "sentiment": "positive|neutral|negative", "urgency": "low|medium|high"}}
            """
            
            response = self.client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100
            )
            
            return eval(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Erro na análise de IA: {e}")
            return {"score": 0.5, "sentiment": "neutral", "urgency": "low"}
    
    async def generate_response(self, user_message: str, context: Dict) -> str:
        """Gera resposta inteligente para o lead"""
        try:
            if not self.client.api_key:
                return "Obrigado pelo seu interesse! Em breve um corretor entrará em contato."
            
            prompt = f"""
            Você é um assistente de vendas de planos de saúde. 
            Contexto: {context}
            Mensagem do lead: "{user_message}"
            
            Responda de forma amigável e profissional, oferecendo ajuda.
            """
            
            response = self.client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Erro ao gerar resposta IA: {e}")
            return "Obrigado pelo contato! Em breve retornaremos."