#!/bin/bash

echo "🚀 Iniciando deploy do HealthPlatform..."

# 1. Atualizar código
git pull origin main

# 2. Instalar/atualizar dependências
pip install -r requirements.txt --upgrade

# 3. Rodar migrações do banco (se houver)
python -m app.backend.src.core.database init

# 4. Coletar arquivos estáticos (se necessário)
# (Para produção)

# 5. Iniciar servidor
echo "✅ Deploy concluído!"
echo "🌐 Acesse: http://localhost:8000"
python run.py