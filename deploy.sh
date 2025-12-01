#!/bin/bash
# deploy.sh - Script para build e deploy do HealthPlatform

echo "🚀 HEALTHPLATFORM - DEPLOY AUTOMATIZADO"
echo "========================================"

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função para imprimir com cor
print_color() {
    echo -e "${1}${2}${NC}"
}

# 1. VALIDAR DOCKER
print_color $YELLOW "1. Verificando Docker..."
if ! command -v docker &> /dev/null; then
    print_color $RED "❌ Docker não encontrado. Instale Docker primeiro."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_color $YELLOW "⚠️ Docker Compose não encontrado. Tentando docker compose..."
    DOCKER_COMPOSE_CMD="docker compose"
else
    DOCKER_COMPOSE_CMD="docker-compose"
fi

# 2. BUILD DA IMAGEM
print_color $YELLOW "2. Build da imagem Docker..."
$DOCKER_COMPOSE_CMD build --no-cache

if [ $? -eq 0 ]; then
    print_color $GREEN "✅ Build concluído com sucesso!"
else
    print_color $RED "❌ Falha no build."
    exit 1
fi

# 3. TESTAR IMAGEM
print_color $YELLOW "3. Testando a imagem..."
docker run --rm -p 8000:8000 --name healthplatform_test \
    -e DATABASE_PATH=/tmp/test.db \
    $(docker images healthplatform --format "{{.ID}}" | head -1) \
    python -c "print('✅ Python funciona!')"

# 4. SUBIR CONTAINERS
print_color $YELLOW "4. Iniciando containers..."
$DOCKER_COMPOSE_CMD up -d

# 5. VERIFICAR SAÚDE
print_color $YELLOW "5. Verificando saúde da aplicação..."
sleep 10  # Aguardar startup

HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/health)

if [ "$HEALTH_CHECK" = "200" ]; then
    print_color $GREEN "✅ Aplicação saudável!"
    echo ""
    echo "🎉 DEPLOY CONCLUÍDO COM SUCESSO!"
    echo "================================"
    echo ""
    echo "🌐 URLs disponíveis:"
    echo "   • Aplicação:      http://localhost:8000"
    echo "   • API Health:     http://localhost:8000/api/health"
    echo "   • Dashboard:      http://localhost:8000/dashboard.html"
    echo ""
    echo "🔧 Comandos úteis:"
    echo "   • Ver logs:       docker-compose logs -f"
    echo "   • Parar:          docker-compose down"
    echo "   • Reiniciar:      docker-compose restart"
    echo "   • Acessar shell:  docker exec -it healthplatform_app bash"
    echo ""
    print_color $GREEN "🚀 HealthPlatform está rodando!"
else
    print_color $RED "❌ Falha no health check. Status: $HEALTH_CHECK"
    echo "📋 Últimos logs:"
    $DOCKER_COMPOSE_CMD logs --tail=20
    exit 1
fi