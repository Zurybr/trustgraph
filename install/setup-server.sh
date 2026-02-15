#!/bin/bash
# TrustGraph Server Setup
# Configura TrustGraph para acceso remoto desde otros agentes

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
    echo -e "${BOLD}${BLUE}║${RESET}     🌐 ${BOLD}TrustGraph Server Setup (Remote Access)${RESET}              ${BLUE}║${RESET}"
    echo -e "${BOLD}${BLUE}╚══════════════════════════════════════════════════════════════╝${RESET}"
    echo ""
}

check_trustgraph_running() {
    echo -e "${BLUE}🔍 Verificando TrustGraph...${RESET}"

    if ! curl -s http://localhost:8080/api/v1/health > /dev/null 2>&1; then
        echo -e "${RED}❌ TrustGraph no está ejecutándose${RESET}"
        echo -e "${YELLOW}   Primero inicia TrustGraph:${RESET}"
        echo -e "   make up"
        exit 1
    fi

    echo -e "${GREEN}✅ TrustGraph está activo${RESET}"
    echo ""
}

configure_network() {
    echo -e "${BLUE}🌐 Configuración de Red${RESET}"
    echo ""

    # Detectar IP
    IP_LOCAL=$(hostname -I | awk '{print $1}')

    echo -e "${CYAN}IP detectada:${RESET} $IP_LOCAL"
    echo ""

    echo -e "${YELLOW}Para permitir acceso remoto, necesitas:${RESET}"
    echo ""
    echo -e "1. ${BOLD}Abrir puertos en el firewall:${RESET}"
    echo -e "   ${CYAN}sudo ufw allow 8080/tcp${RESET}  # API Gateway"
    echo -e "   ${CYAN}sudo ufw allow 8888/tcp${RESET}  # Workbench (opcional)"
    echo ""
    echo -e "2. ${BOLD}O configurar un reverse proxy (recomendado para producción):${RESET}"
    echo -e "   - Nginx con SSL"
    echo -e "   - Traefik"
    echo -e "   - Caddy"
    echo ""

    read -p "¿Abrir puertos automáticamente con ufw? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v ufw &> /dev/null; then
            sudo ufw allow 8080/tcp
            sudo ufw allow 8888/tcp
            echo -e "${GREEN}✅ Puertos abiertos${RESET}"
        else
            echo -e "${YELLOW}⚠️  ufw no instalado, abre los puertos manualmente${RESET}"
        fi
    fi

    echo ""
}

configure_authentication() {
    echo -e "${BLUE}🔐 Configuración de Autenticación${RESET}"
    echo ""

    echo -e "${YELLOW}Para acceso remoto seguro, se recomienda:${RESET}"
    echo ""
    echo -e "1. ${BOLD}Token de autenticación simple (básico)${RESET}"
    echo -e "2. ${BOLD}Reverse proxy con autenticación${RESET}"
    echo -e "3. ${BOLD}VPN (WireGuard, OpenVPN)${RESET} - Más seguro"
    echo ""

    read -p "¿Configurar token de autenticación básico? [y/N] " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        TOKEN=$(openssl rand -hex 32 2>/dev/null || head -c 64 /dev/urandom | xxd -p | head -c 64)

        echo -e "${GREEN}Token generado:${RESET}"
        echo -e "${CYAN}${TOKEN}${RESET}"
        echo ""

        # Guardar token
        echo "$TOKEN" > "$REPO_DIR/.auth_token"
        chmod 600 "$REPO_DIR/.auth_token"

        echo -e "${YELLOW}⚠️  Guarda este token de forma segura${RESET}"
        echo -e "${YELLOW}   Se ha guardado en:${RESET} $REPO_DIR/.auth_token"
        echo ""

        echo -e "${BOLD}Para conectar desde otro agente:${RESET}"
        echo -e "   ${CYAN}trus login --host $IP_LOCAL --port 8080${RESET}"
        echo -e "   Token: ${TOKEN:0:16}..."
    fi

    echo ""
}

generate_connection_info() {
    echo -e "${BLUE}📋 Información de Conexión${RESET}"
    echo ""

    IP_LOCAL=$(hostname -I | awk '{print $1}')

    echo -e "${BOLD}Para conectar agentes remotos:${RESET}"
    echo ""
    echo -e "${CYAN}Host:${RESET} $IP_LOCAL"
    echo -e "${CYAN}Puerto:${RESET} 8080"
    echo -e "${CYan}URL:${RESET} http://$IP_LOCAL:8080"
    echo ""

    echo -e "${BOLD}Comandos en los agentes clientes:${RESET}"
    echo ""
    echo -e "1. ${BOLD}Instalar CLI:${RESET}"
    echo -e "   curl -fsSL http://$IP_LOCAL:8888/install.sh | bash"
    echo -e "   # O descargar desde: $REPO_DIR/install/"
    echo ""
    echo -e "2. ${BOLD}Configurar conexión:${RESET}"
    echo -e "   ${CYAN}trus login --host $IP_LOCAL --port 8080${RESET}"
    echo ""
    echo -e "3. ${BOLD}Verificar:${RESET}"
    echo -e "   ${CYAN}trus status${RESET}"
    echo ""
}

show_summary() {
    echo ""
    echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════════════════════════╗${RESET}"
    echo -e "${BOLD}${GREEN}║${RESET}              ✅ Server Setup Completado!                     ${GREEN}${BOLD}║${RESET}"
    echo -e "${BOLD}${GREEN}╚══════════════════════════════════════════════════════════════╝${RESET}"
    echo ""

    echo -e "${YELLOW}⚠️  Notas de seguridad:${RESET}"
    echo ""
    echo -e "  • ${BOLD}No expongas TrustGraph directamente a internet${RESET} sin:"
    echo -e "    - SSL/TLS (HTTPS)"
    echo -e "    - Autenticación robusta"
    echo -e "    - Firewall configurado"
    echo ""
    echo -e "  • ${BOLD}Recomendaciones:${RESET}"
    echo -e "    - Usa VPN (WireGuard) para acceso remoto"
    echo -e "    - Configura Nginx como reverse proxy con SSL"
    echo -e "    - Limita acceso por IP"
    echo ""
}

# Main
print_header
check_trustgraph_running
configure_network
configure_authentication
generate_connection_info
show_summary
