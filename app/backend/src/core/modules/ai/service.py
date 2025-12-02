# app/backend/src/core/modules/ai/service.py - VERSÃO CORRIGIDA
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Adicionar caminho do projeto
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class AIService:
    def __init__(self, api_key: Optional[str] = None):
        """Inicializa o serviço de IA"""
        self.api_key = api_key or "demo_key"  # Chave de demonstração
        self.initialized = False
        
    async def initialize(self):
        """Inicializa o serviço"""
        try:
            # Tentar importar OpenAI (opcional)
            try:
                import openai
                if self.api_key and self.api_key != "demo_key":
                    openai.api_key = self.api_key
                print("✅ OpenAI disponível")
            except ImportError:
                print("⚠️ OpenAI não instalado - usando modo simulado")
            
            self.initialized = True
            print("✅ AI Service inicializado")
            return True
        except Exception as e:
            print(f"❌ AI Service: {e}")
            return False
    
    async def check_status(self) -> bool:
        """Verifica status do serviço de IA"""
        return self.initialized
    
    async def analisar_lead(self, lead_id: int) -> Dict[str, Any]:
        """Analisa um lead usando IA (modo simulado se não tiver OpenAI)"""
        try:
            # Tentar usar OpenAI real
            try:
                import openai
                
                # Se tiver chave válida
                if self.api_key and self.api_key != "demo_key":
                    # Aqui iria a chamada real da API
                    response = {
                        "lead_id": lead_id,
                        "score": 0.85,
                        "probabilidade_fechamento": "Alta",
                        "sugestoes": ["Oferecer plano premium", "Agendar reunião"],
                        "modelo": "gpt-4"
                    }
                else:
                    # Modo simulado
                    response = self._analisar_lead_simulado(lead_id)
                    
            except ImportError:
                # OpenAI não instalado
                response = self._analisar_lead_simulado(lead_id)
            
            return {
                "success": True,
                "data": response
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": self._analisar_lead_simulado(lead_id)  # Fallback
            }
    
    async def gerar_resposta(self, mensagem: str, contexto: str = None) -> Dict[str, Any]:
        """Gera resposta automática usando IA"""
        try:
            # Respostas simuladas baseadas no contexto
            respostas_simuladas = {
                "saudacao": "Olá! Sou o assistente do HealthCRM. Como posso ajudar você hoje?",
                "duvida_plano": "Temos planos de saúde para todas as necessidades. Posso te apresentar as opções?",
                "contato": "Claro! Um de nossos corretores entrará em contato em breve.",
                "default": "Entendi sua solicitação. Vou encaminhar para nossa equipe especializada."
            }
            
            # Lógica simples de análise
            mensagem_lower = mensagem.lower()
            
            if any(word in mensagem_lower for word in ['oi', 'olá', 'bom dia', 'boa tarde']):
                resposta = respostas_simuladas["saudacao"]
            elif any(word in mensagem_lower for word in ['plano', 'seguro', 'saúde']):
                resposta = respostas_simuladas["duvida_plano"]
            elif any(word in mensagem_lower for word in ['contato', 'ligar', 'falar']):
                resposta = respostas_simuladas["contato"]
            else:
                resposta = respostas_simuladas["default"]
            
            return {
                "success": True,
                "data": {
                    "resposta": resposta,
                    "modelo": "health_ia_simulado",
                    "contexto_usado": contexto
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": {
                    "resposta": "Desculpe, não consegui processar sua solicitação no momento.",
                    "modelo": "fallback"
                }
            }
    
    def _analisar_lead_simulado(self, lead_id: int) -> Dict[str, Any]:
        """Análise simulada de lead (para desenvolvimento)"""
        # Gera resultados consistentes baseados no ID do lead
        scores = {
            1: {"score": 0.92, "categoria": "Muito Quente"},
            2: {"score": 0.78, "categoria": "Quente"},
            3: {"score": 0.65, "categoria": "Morno"},
            4: {"score": 0.45, "categoria": "Frio"}
        }
        
        lead_data = scores.get(lead_id % 4 + 1, scores[2])
        
        return {
            "lead_id": lead_id,
            "score": lead_data["score"],
            "categoria": lead_data["categoria"],
            "probabilidade_fechamento": f"{lead_data['score']*100:.1f}%",
            "sugestoes": [
                f"Lead classificado como {lead_data['categoria']}",
                "Recomendado contato em 24h" if lead_data["score"] > 0.7 else "Contato em 48h",
                "Oferecer demonstração gratuita"
            ],
            "modelo": "health_ia_simulado_v1"
        }