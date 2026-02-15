#!/bin/bash
# TrustGraph Local Server Setup
# Configura y levanta TrustGraph en modo local

set -e

BLUE='\033[36m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
CYAN='\033[35m'
BOLD='\033[1m'
RESET='\033[0m'

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

print_header() {
    echo ""
    echo -e "${BOLD}${BLUE}╔══════════════════════════════════════════════════════════════╗${RESET}"
    echo -e "${BOLD}${BLUE}║${RESET}     🖥️  ${BOLD}TrustGraph Local Server Setup${RESET}                       ${BLUE}║${RESET}"
    echo -e "${BOLD}${BLUE}╚══════════════════════════════════════════════════════════════╝${RESET}"
    echo ""
}

check_prerequisites() {
    echo -e "${BLUE}📋 Verificando prerrequisitos...${RESET}"
    echo ""

    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker no está instalado${RESET}"
        echo "   Instala Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    echo -e "${GREEN}✅ Docker instalado${RESET}"

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo -e "${RED}❌ Docker Compose no está instalado${RESET}"
        exit 1
    fi
    echo -e "${GREEN}✅ Docker Compose instalado${RESET}"

    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 no está instalado${RESET}"
        exit 1
    fi
    echo -e "${GREEN}✅ Python 3 instalado${RESET}"

    echo ""
}

setup_environment() {
    echo -e "${BLUE}⚙️  Configurando entorno...${RESET}"
    echo ""

    cd "$REPO_DIR"

    # Crear .env si no existe
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            echo -e "${GREEN}✅ Archivo .env creado desde .env.example${RESET}"
        else
            echo -e "${RED}❌ No se encontró .env.example${RESET}"
            exit 1
        fi
    else
        echo -e "${YELLOW}ℹ️  .env ya existe, se conservará${RESET}"
    fi

    # Crear directorios de datos
    echo -e "${CYAN}📁 Creando directorios de datos...${RESET}"
    mkdir -p data/{cassandra,qdrant,garage,pulsar,prometheus,grafana,loki}
    echo -e "${GREEN}✅ Directorios creados${RESET}"

    # Instalar dependencias Python
    echo -e "${CYAN}📚 Verificando dependencias Python...${RESET}"
    pip3 install -q httpx requests click pyyaml 2>/dev/null || pip install -q httpx requests click pyyaml
    echo -e "${GREEN}✅ Dependencias instaladas${RESET}"

    echo ""
}

configure_provider() {
    echo -e "${BLUE}🤖 Configuración del Proveedor LLM${RESET}"
    echo ""

    read -p "¿Deseas configurar el proveedor LLM ahora? [Y/n] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        if [ -f "$REPO_DIR/scripts/setup_env.py" ]; then
            python3 "$REPO_DIR/scripts/setup_env.py"
        else
            echo -e "${YELLOW}⚠️  Wizard no encontrado, configura manualmente:${RESET}"
            echo -e "   nano .env"
        fi
    fi

    echo ""
}

start_services() {
    echo -e "${BLUE}🚀 Iniciando TrustGraph...${RESET}"
    echo ""

    cd "$REPO_DIR"

    # Pull latest images
    echo -e "${CYAN}📥 Descargando imágenes...${RESET}"
    docker compose pull

    # Start services
    echo -e "${CYAN}🚀 Iniciando servicios...${RESET}"
    docker compose up -d

    echo ""
    echo -e "${GREEN}✅ Servicios iniciados${RESET}"
    echo ""
    echo -e "${YELLOW}⏳ Esperando a que estén listos (esto puede tomar 1-2 minutos)...${RESET}"
    echo ""

    sleep 10

    # Check health
    echo -e "${CYAN}🏥 Verificando salud...${RESET}"
    MAX_RETRIES=30
    RETRY=0

    while [ $RETRY -lt $MAX_RETRIES ]; do
        if curl -s http://localhost:8080/api/v1/health > /dev/null 2>&1; then
            echo ""
            echo -e "${GREEN}✅ TrustGraph está listo!${RESET}"
            return 0
        fi

        echo -n "."
        sleep 2
        RETRY=$((RETRY + 1))
    done

    echo ""
    echo -e "${YELLOW}⚠️  TrustGraph está iniciando pero puede no estar listo aún${RESET}"
    return 1
}

show_summary() {
    echo ""
    echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════════════════════════╗${RESET}"
    echo -e "${BOLD}${GREEN}║${RESET}              ✅ Setup Local Completado!                      ${GREEN}${BOLD}║${RESET}"
    echo -e "${BOLD}${GREEN}╚══════════════════════════════════════════════════════════════╝${RESET}"
    echo ""
    echo -e "${BOLD}📊 Servicios disponibles:${RESET}"
    echo ""
    echo -e "  ${CYAN}Workbench UI:${RESET}  http://localhost:8888"
    echo -e "  ${CYAN}API Gateway:${RESET}   http://localhost:8080"
    echo -e "  ${CYAN}Grafana:${RESET}       http://localhost:3000  (admin/admin)"
    echo -e "  ${CYAN}Prometheus:${RESET}    http://localhost:9090"
    echo -e "  ${CYAN}Qdrant:${RESET}        http://localhost:6333"
    echo ""
    echo -e "${BOLD}📝 Próximos pasos:${RESET}"
    echo ""
    echo -e "  1. ${BOLD}Instalar CLI (opcional pero recomendado):${RESET}"
    echo -e "     ./install/install-cli.sh"
    echo ""
    echo -e "  2. ${BOLD}Configurar CLI:${RESET}"
    echo -e "     trus login"
    echo ""
    echo -e "  3. ${BOLD}Cargar documentación:${RESET}"
    echo -e "     make load"
    echo -e "     # o con CLI: trus recordar directorio/"
    echo ""
    echo -e "  4. ${BOLD}Ver estado:${RESET}"
    echo -e "     make status"
    echo -e "     # o: trus status"
    echo ""
    echo -e "${BOLD}📖 Comandos útiles:${RESET}"
    echo -e "  ${CYAN}make up${RESET}        - Iniciar servicios"
    echo -e "  ${CYAN}make down${RESET}      - Detener servicios"
    echo -e "  ${CYAN}make logs${RESET}      - Ver logs"
    echo -e "  ${CYAN}make provider${RESET}  - Cambiar proveedor LLM"
    echo ""
    echo -e "${YELLOW}Para permitir acceso remoto a esta instancia:${RESET}"
    echo -e "  Ejecuta: ${CYAN}./install/setup-server.sh${RESET}"
    echo ""
}

# Main
print_header
check_prerequisites
setup_environment
configure_provider
start_services
show_summary
