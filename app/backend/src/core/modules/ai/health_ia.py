# app/backend/src/core/modules/ai/health_ia.py
# SISTEMA DE IA 100% BRASILEIRO - HEALTHPLATFORM

class HealthIA:
    def __init__(self):
        self.planos_disponiveis = self._carregar_planos()
        self.operadoras = self._carregar_operadoras()
        
    def _carregar_planos(self):
        """Carrega todos os planos disponíveis no sistema"""
        return {
            "INDIVIDUAL": {
                "faixa_preco": (150, 500),
                "cobertura": ["consultas", "exames basicos", "urgencia"],
                "indicado": ["jovens", "solteiros", "estudantes"],
                "operadoras": ["Amil", "Bradesco", "SulAmérica"]
            },
            "FAMILIAR": {
                "faixa_preco": (800, 2000), 
                "cobertura": ["consultas", "exames", "internacao", "odontologico"],
                "indicado": ["familias", "casais", "com filhos"],
                "operadoras": ["Amil", "Unimed", "Bradesco"]
            },
            "EMPRESARIAL": {
                "faixa_preco": (2000, 10000),
                "cobertura": ["consultas", "exames", "internacao", "alta complexidade"],
                "indicado": ["empresas", "MEI", "profissionais"],
                "operadoras": ["Amil", "SulAmérica", "Unimed"]
            },
            "VIP": {
                "faixa_preco": (1500, 3000),
                "cobertura": ["consultas VIP", "exames completos", "internacao apartamento"],
                "indicado": ["executivos", "alta renda"],
                "operadoras": ["Amil", "Unimed", "NotreDame"]
            }
        }
    
    def _carregar_operadoras(self):
        """Carrega informações das operadoras"""
        return {
            "Amil": {"reputacao": 4.5, "rede": "nacional", "tempo_contratacao": "24h"},
            "Bradesco": {"reputacao": 4.3, "rede": "nacional", "tempo_contratacao": "48h"},
            "SulAmérica": {"reputacao": 4.2, "rede": "nacional", "tempo_contratacao": "72h"},
            "Unimed": {"reputacao": 4.6, "rede": "nacional", "tempo_contratacao": "24h"},
            "NotreDame": {"reputacao": 4.1, "rede": "regional", "tempo_contratacao": "48h"}
        }
    
    def analisar_perfil_cliente(self, dados_cliente):
        """
        Analisa perfil do cliente e recomenda plano ideal
        """
        print(f"🧠 HEALTH-IA: Analisando perfil do cliente...")
        
        idade = dados_cliente.get('idade', 0)
        renda = dados_cliente.get('renda', 0)
        dependentes = dados_cliente.get('dependentes', 0)
        profissao = dados_cliente.get('profissao', '').lower()
        
        # Lógica de recomendação 100% brasileira
        if dependentes >= 2 or (idade > 30 and renda > 5000):
            plano_sugerido = "FAMILIAR"
            justificativa = f"Recomendado para famílias com {dependentes} dependentes e renda familiar adequada"
        
        elif profissao in ['empresario', 'empresária', 'diretor', 'gerente'] and renda > 10000:
            plano_sugerido = "EMPRESARIAL" 
            justificativa = "Perfil executivo - ideal para cobertura empresarial completa"
        
        elif idade < 35 and renda < 3000:
            plano_sugerido = "INDIVIDUAL"
            justificativa = "Plano econômico perfeito para jovens profissionais"
        
        else:
            plano_sugerido = "VIP"
            justificativa = "Plano premium para quem busca conforto e cobertura ampla"
        
        # Sugerir operadora baseada na reputação
        operadora_sugerida = self._sugerir_operadora(plano_sugerido)
        
        return {
            "plano_sugerido": plano_sugerido,
            "operadora_sugerida": operadora_sugerida,
            "justificativa": justificativa,
            "faixa_preco_estimada": self.planos_disponiveis[plano_sugerido]["faixa_preco"],
            "cobertura_principal": self.planos_disponiveis[plano_sugerido]["cobertura"][:3]
        }
    
    def _sugerir_operadora(self, plano):
        """Sugere a melhor operadora para o plano"""
        operadoras_plano = self.planos_disponiveis[plano]["operadoras"]
        
        # Ordena por reputação (lógica brasileira: melhor custo-benefício)
        operadoras_ordenadas = sorted(
            operadoras_plano, 
            key=lambda op: self.operadoras[op]["reputacao"], 
            reverse=True
        )
        
        return operadoras_ordenadas[0] if operadoras_ordenadas else "Amil"
    
    def gerar_script_venda(self, perfil_cliente, plano_sugerido, formato='texto'):
        """
        Gera script de vendas personalizado
        formato: 'texto' ou 'html'
        """
        nome_cliente = perfil_cliente.get('nome', 'Cliente')
        
        scripts = {
            "INDIVIDUAL": {
                "titulo": "PLANO INDIVIDUAL - SEU FUTURO PROTEGIDO",
                "saudacao": f"👋 OLÁ {nome_cliente.upper()}!",
                "introducao": "Que bom que você está pensando no seu futuro!",
                "destaques": [
                    "Cobertura completa por apenas R$ 150-500/mês",
                    "Consultas, exames e urgência 24h", 
                    "Sem carência para emergências",
                    "Rede nacional de hospitais"
                ],
                "vantagens": [
                    "Flexibilidade total",
                    "Preço acessível",
                    "Qualidade Amil/Bradesco"
                ],
                "call_to_action": "Vamos garantir sua tranquilidade? 📞"
            },
            
            "FAMILIAR": {
                "titulo": "PLANO FAMILIAR - QUEM AMA, CUIDA!",
                "saudacao": f"👋 OLÁ {nome_cliente.upper()}!",
                "introducao": "Protegendo quem você mais ama! 💝",
                "destaques": [
                    "Toda sua família protegida (R$ 800-2000/mês)",
                    "Consultas, exames, internação e odontológico",
                    "Até 6 dependentes sem custo adicional", 
                    "Assistência 24h para todos"
                ],
                "vantagens": [
                    "Pediatria e obstetrícia",
                    "Especialistas completos",
                    "Hospitais de excelência"
                ],
                "call_to_action": "Sua família merece o melhor! 👨‍👩‍👧‍👦"
            },
            
            "EMPRESARIAL": {
                "titulo": "PLANO EMPRESARIAL - INVESTIMENTO INTELIGENTE",
                "saudacao": f"👋 OLÁ {nome_cliente.upper()}!",
                "introducao": "Investindo no seu maior patrimônio: SEUS COLABORADORES! 💼",
                "destaques": [
                    "Cobertura completa para sua equipe (R$ 2.000-10.000/mês)",
                    "Atendimento corporativo prioritário",  
                    "Redução de absenteísmo em até 40%",
                    "Imposto reduzido (despesa operacional)"
                ],
                "vantagens": [
                    "Atendimento VIP para funcionários",
                    "Customização total de rede",
                    "Relatórios de utilização",
                    "Consultoria em saúde ocupacional"
                ],
                "call_to_action": "Funcionários saudáveis = Empresa forte! 💪"
            },
            
            "VIP": {
                "titulo": "PLANO VIP - EXCLUSIVIDADE E CONFORTO",
                "saudacao": f"👋 OLÁ {nome_cliente.upper()}!",
                "introducao": "Exclusividade e conforto para quem merece o melhor! 🌟",
                "destaques": [
                    "Atendimento personalizado (R$ 1.500-3.000/mês)",  
                    "Consultas em horários flexíveis",
                    "Acomodação em apartamento",
                    "Acesso a melhores hospitais"
                ],
                "vantagens": [
                    "Concierge médico 24h",
                    "Segunda opinião médica", 
                    "Desconto em hospitais internacionais",
                    "Programas de wellness"
                ],
                "call_to_action": "Sua saúde é seu maior luxo! 💎"
            }
        }
        
        script_data = scripts.get(plano_sugerido, scripts["INDIVIDUAL"])
        
        if formato == 'html':
            return self._formatar_html(script_data)
        else:
            return self._formatar_texto(script_data)
    
    def _formatar_texto(self, script_data):
        """Formata script em texto puro com quebras"""
        texto = f"{script_data['saudacao']}\n\n"
        texto += f"{script_data['introducao']}\n\n"
        texto += f"🎯 **{script_data['titulo']}:**\n\n"
        
        for destaque in script_data['destaques']:
            texto += f"• {destaque}\n"
        
        texto += f"\n💡 **VANTAGENS EXCLUSIVAS:**\n\n"
        for vantagem in script_data['vantagens']:
            texto += f"✓ {vantagem}\n"
        
        texto += f"\n{script_data['call_to_action']}"
        
        return texto
    
    def _formatar_html(self, script_data):
        """Formata script em HTML"""
        html = f"<div class='script-venda'><h3>{script_data['saudacao']}</h3>"
        html += f"<p><strong>{script_data['introducao']}</strong></p>"
        html += f"<h4>🎯 {script_data['titulo']}:</h4><ul>"
        
        for destaque in script_data['destaques']:
            html += f"<li>{destaque}</li>"
        
        html += "</ul><h4>💡 VANTAGENS EXCLUSIVAS:</h4><ul>"
        for vantagem in script_data['vantagens']:
            html += f"<li>✓ {vantagem}</li>"
        
        html += f"</ul><p><strong>{script_data['call_to_action']}</strong></p></div>"
        return html

    def perguntas_triagem(self):
        """Retorna perguntas para qualificação de leads"""
        return [
            "Qual sua faixa etária?",
            "Quantas pessoas precisam de cobertura?",
            "Qual sua renda familiar aproximada?",
            "Alguma condição de saúde pré-existente?",
            "Prefere rede nacional ou regional?",
            "Já teve plano de saúde antes?",
            "Qual sua principal necessidade? (consultas, exames, internação)"
        ]

# Instância global do nosso sistema de IA
health_ia = HealthIA()