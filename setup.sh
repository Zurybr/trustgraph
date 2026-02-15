#!/bin/bash
# TrustGraph - Setup Script
# Punto de entrada principal para todas las operaciones de setup
#
# Uso:
#   ./setup.sh                    # Menú interactivo completo
#   ./setup.sh makeenv            # Wizard de configuración LLM
#   ./setup.sh install-cli        # Instalar solo CLI
#   ./setup.sh server             # Setup servidor local
#   ./setup.sh remote             # Configurar acceso remoto
#   ./setup.sh help               # Mostrar ayuda

set -e

BLUE='\033[36m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
CYAN='\033[35m'
BOLD='\033[1m'
RESET='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

print_header() {
    echo ""
    echo -e "${BOLD}${BLUE}╔══════════════════════════════════════════════════════════════╗${RESET}"
    echo -e "${BOLD}${BLUE}║${RESET}     🤖 ${BOLD}TrustGraph Setup${RESET}                                      ${BLUE}║${RESET}"
    echo -e "${BOLD}${BLUE}╚══════════════════════════════════════════════════════════════╝${RESET}"
    echo ""
}

show_help() {
    print_header
    echo -e "${BOLD}Uso:${RESET} ./setup.sh [comando]"
    echo ""
    echo -e "${BOLD}Comandos disponibles:${RESET}"
    echo ""
    echo -e "  ${CYAN}(sin argumentos)${RESET}  Inicia el menú maestro interactivo"
    echo ""
    echo -e "  ${CYAN}makeenv${RESET}          Wizard de configuración de proveedor LLM"
    echo -e "  ${CYAN}install-cli${RESET}      Instala solo la CLI 'trus'"
    echo -e "  ${CYAN}server${RESET}           Setup completo del servidor local"
    echo -e "  ${CYAN}remote${RESET}           Configura acceso remoto (para otros agentes)"
    echo ""
    echo -e "  ${CYAN}start${RESET}            Inicia TrustGraph"
    echo -e "  ${CYAN}stop${RESET}             Detiene TrustGraph"
    echo -e "  ${CYAN}status${RESET}           Muestra estado"
    echo ""
    echo -e "  ${CYAN}uninstall-cli${RESET}    Desinstala la CLI"
    echo -e "  ${CYAN}uninstall-all${RESET}    Desinstala TODO (CLI + datos)"
    echo ""
    echo -e "  ${CYAN}help${RESET}             Muestra esta ayuda"
    echo ""
    echo -e "${BOLD}Ejemplos rápidos:${RESET}"
    echo ""
    echo -e "  ${YELLOW}# Instalación completa local:${RESET}"
    echo -e "  ./setup.sh"
    echo ""
    echo -e "  ${YELLOW}# Solo CLI para conectar a servidor remoto:${RESET}"
    echo -e "  ./setup.sh install-cli"
    echo ""
    echo -e "  ${YELLOW}# Configurar proveedor Z.AI (GLM):${RESET}"
    echo -e "  ./setup.sh makeenv"
    echo ""
}

# Si no hay argumentos, ejecutar menú maestro
if [ $# -eq 0 ]; then
    if [ -f "$SCRIPT_DIR/install/setup-master.sh" ]; then
        exec "$SCRIPT_DIR/install/setup-master.sh"
    else
        echo -e "${RED}❌ No se encontró install/setup-master.sh${RESET}"
        exit 1
    fi
fi

# Procesar comando
case "${1:-}" in
    makeenv)
        print_header
        if [ -f "$SCRIPT_DIR/scripts/setup_env.py" ]; then
            python3 "$SCRIPT_DIR/scripts/setup_env.py"
        else
            echo -e "${RED}❌ Wizard no encontrado${RESET}"
            exit 1
        fi
        ;;

    install-cli|cli)
        if [ -f "$SCRIPT_DIR/install/install-cli.sh" ]; then
            exec "$SCRIPT_DIR/install/install-cli.sh"
        else
            echo -e "${RED}❌ Instalador de CLI no encontrado${RESET}"
            exit 1
        fi
        ;;

    server|local)
        if [ -f "$SCRIPT_DIR/install/setup-local.sh" ]; then
            exec "$SCRIPT_DIR/install/setup-local.sh"
        else
            echo -e "${RED}❌ Setup local no encontrado${RESET}"
            exit 1
        fi
        ;;

    remote|server-remote)
        if [ -f "$SCRIPT_DIR/install/setup-server.sh" ]; then
            exec "$SCRIPT_DIR/install/setup-server.sh"
        else
            echo -e "${RED}❌ Setup remoto no encontrado${RESET}"
            exit 1
        fi
        ;;

    start|up)
        cd "$SCRIPT_DIR"
        make up
        ;;

    stop|down)
        cd "$SCRIPT_DIR"
        make down
        ;;

    status)
        cd "$SCRIPT_DIR"
        make status
        if command -v trus &> /dev/null; then
            echo ""
            trus status
        fi
        ;;

    uninstall-cli)
        if [ -f "$SCRIPT_DIR/install/uninstall-cli.sh" ]; then
            exec "$SCRIPT_DIR/install/uninstall-cli.sh"
        else
            echo -e "${RED}❌ Desinstalador no encontrado${RESET}"
            exit 1
        fi
        ;;

    uninstall-all|purge)
        echo -e "${RED}💥 Esto eliminará TODO: CLI, servidor y datos${RESET}"
        read -p "¿Confirmar? [escribe 'eliminar todo']: " confirm
        if [ "$confirm" = "eliminar todo" ]; then
            [ -f "$SCRIPT_DIR/install/uninstall-cli.sh" ] && "$SCRIPT_DIR/install/uninstall-cli.sh" || true
            cd "$SCRIPT_DIR"
            make down -v 2>/dev/null || true
            docker system prune -f 2>/dev/null || true
            rm -rf data/
            echo -e "${GREEN}✅ Desinstalación completa${RESET}"
        else
            echo -e "${YELLOW}❌ Cancelado${RESET}"
        fi
        ;;

    help|--help|-h)
        show_help
        ;;

    *)
        echo -e "${RED}❌ Comando desconocido: $1${RESET}"
        echo ""
        show_help
        exit 1
        ;;
esac
