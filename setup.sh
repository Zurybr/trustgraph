#!/bin/bash
# TrustGraph - Setup Script
# Configura el entorno para TrustGraph

set -e

BLUE='\033[36m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
RESET='\033[0m'

echo -e "${BLUE}🔧 TrustGraph Setup${RESET}"
echo "===================="
echo ""

# Verificar Docker
echo -e "${BLUE}📦 Verificando Docker...${RESET}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker no está instalado${RESET}"
    echo "   Instala Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose no está instalado${RESET}"
    echo "   Instala Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✅ Docker OK${RESET}"

# Verificar Python
echo -e "${BLUE}🐍 Verificando Python...${RESET}"
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python no está instalado${RESET}"
    exit 1
fi

PYTHON_CMD=$(command -v python3 || command -v python)
echo -e "${GREEN}✅ Python: $PYTHON_CMD${RESET}"

# Crear .env si no existe
echo ""
echo -e "${BLUE}⚙️  Configurando entorno...${RESET}"

if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ Archivo .env creado${RESET}"
    echo -e "${YELLOW}⚠️  IMPORTANTE: Edita .env con tus API keys${RESET}"
else
    echo -e "${YELLOW}ℹ️  .env ya existe${RESET}"
fi

# Crear directorios de datos
echo ""
echo -e "${BLUE}📁 Creando directorios...${RESET}"
mkdir -p data/{cassandra,qdrant,garage,pulsar,prometheus,grafana,loki}
echo -e "${GREEN}✅ Directorios creados${RESET}"

# Instalar dependencias Python
echo ""
echo -e "${BLUE}📚 Verificando dependencias Python...${RESET}"

# Verificar si httpx o requests están instalados
if ! $PYTHON_CMD -c "import httpx" 2>/dev/null && ! $PYTHON_CMD -c "import requests" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  httpx no está instalado${RESET}"
    echo "   Instalando httpx..."
    pip install httpx || pip3 install httpx
fi

echo -e "${GREEN}✅ Dependencias OK${RESET}"

# Verificar MCP SDK (opcional)
echo ""
echo -e "${BLUE}🔌 Verificando MCP SDK (opcional)...${RESET}"
if ! $PYTHON_CMD -c "import mcp" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  MCP SDK no instalado (opcional para integración con Claude)${RESET}"
    echo "   Instala con: pip install mcp"
else
    echo -e "${GREEN}✅ MCP SDK OK${RESET}"
fi

echo ""
echo "===================="
echo -e "${GREEN}✅ Setup completo!${RESET}"
echo ""
echo -e "${YELLOW}📝 Próximos pasos:${RESET}"
echo ""
echo "1. Configura tus API keys en .env:"
echo "   nano .env"
echo ""
echo "2. Inicia TrustGraph:"
echo "   docker compose up -d"
echo "   # o: make up"
echo ""
echo "3. Espera 1-2 minutos y verifica:"
echo "   docker compose ps"
echo ""
echo "4. Carga la documentación:"
echo "   python scripts/load_docs.py"
echo "   # o: make load"
echo ""
echo "5. Accede al Workbench:"
echo "   http://localhost:8888"
echo ""
echo "📖 Comandos útiles:"
echo "   make help     - Ver todos los comandos"
echo "   make status   - Estado de servicios"
echo "   make query    - Modo interactivo"
echo ""
