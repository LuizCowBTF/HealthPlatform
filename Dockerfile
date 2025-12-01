# Dockerfile
# ============================================
# 🏥 HEALTHPLATFORM SaaS - DOCKER DEPLOY
# ============================================

# 🐍 FASE 1: BASE IMAGE
FROM python:3.11-slim AS builder

# 📦 Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# 📁 Criar diretório da aplicação
WORKDIR /app

# 📋 Copiar requirements primeiro (cache otimizado)
COPY requirements.txt .

# 🔧 Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 🐍 FASE 2: IMAGEM FINAL (mais leve)
FROM python:3.11-slim

# 🏷️ Metadados
LABEL maintainer="seu-email@exemplo.com"
LABEL version="1.0.0"
LABEL description="HealthPlatform SaaS - CRM + WhatsApp + IA + Financeiro"

# 👤 Criar usuário não-root (segurança)
RUN useradd -m -u 1000 healthuser && \
    mkdir -p /app && chown -R healthuser:healthuser /app

# 📦 Dependências de runtime
RUN apt-get update && apt-get install -y \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 📁 Configurar diretório de trabalho
WORKDIR /app

# 👥 Copiar dependências da fase anterior
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# 📋 Copiar código da aplicação
COPY --chown=healthuser:healthuser . .

# 🔧 Configurar ambiente
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV HOST=0.0.0.0

# 📁 Criar diretório para banco de dados
RUN mkdir -p /data && chown -R healthuser:healthuser /data
ENV DATABASE_PATH=/data/health_platform.db

# 👤 Mudar para usuário não-root
USER healthuser

# 🌐 Expor porta
EXPOSE 8000

# 🚀 Health check (verifica se app está saudável)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# ⚡ Comando de inicialização
CMD ["python", "app/backend/main.py"]