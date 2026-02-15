#!/bin/bash
# TrustGraph CLI Installer
# Instala la CLI 'trus' en el sistema

set -e

BLUE='\033[36m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
CYAN='\033[35m'
BOLD='\033[1m'
RESET='\033[0m'

INSTALL_DIR="/opt/trustgraph-cli"
BIN_DIR="/usr/local/bin"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

print_header() {
    echo ""
    echo -e "${BOLD}${BLUE}╔══════════════════════════════════════════════════════════════╗${RESET}"
    echo -e "${BOLD}${BLUE}║${RESET}     🤖  ${BOLD}TrustGraph CLI Installer${RESET}                           ${BLUE}║${RESET}"
    echo -e "${BOLD}${BLUE}╚══════════════════════════════════════════════════════════════╝${RESET}"
    echo ""
}

check_prerequisites() {
    echo -e "${BLUE}📋 Verificando prerrequisitos...${RESET}"

    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 no está instalado${RESET}"
        echo "   Instala Python 3.8 o superior"
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✅ Python ${PYTHON_VERSION}${RESET}"

    # Check pip
    if ! command -v pip3 &> /dev/null; then
        echo -e "${YELLOW}⚠️  pip3 no encontrado, intentando instalar...${RESET}"
        python3 -m ensurepip --upgrade 2>/dev/null || {
            echo -e "${RED}❌ No se pudo instalar pip${RESET}"
            exit 1
        }
    fi

    echo -e "${GREEN}✅ pip3 disponible${RESET}"
}

install_cli() {
    echo ""
    echo -e "${BLUE}📦 Instalando TrustGraph CLI...${RESET}"

    # Create install directory
    if [ -d "$INSTALL_DIR" ]; then
        echo -e "${YELLOW}⚠️  El directorio ${INSTALL_DIR} ya existe${RESET}"
        echo -e "${YELLOW}   Se actualizará la instalación${RESET}"
        rm -rf "$INSTALL_DIR"
    fi

    sudo mkdir -p "$INSTALL_DIR"

    # Copy CLI files
    echo -e "${CYAN}   Copiando archivos...${RESET}"
    sudo cp -r "$REPO_DIR/cli/"* "$INSTALL_DIR/"

    # Install Python dependencies
    echo -e "${CYAN}   Instalando dependencias...${RESET}"
    sudo pip3 install -q -r "$INSTALL_DIR/requirements.txt"

    # Create symlink
    echo -e "${CYAN}   Creando enlace simbólico...${RESET}"
    if [ -L "$BIN_DIR/trus" ]; then
        sudo rm "$BIN_DIR/trus"
    fi
    sudo ln -s "$INSTALL_DIR/trus.py" "$BIN_DIR/trus"
    sudo chmod +x "$BIN_DIR/trus"

    echo -e "${GREEN}✅ CLI instalada correctamente${RESET}"
}

verify_installation() {
    echo ""
    echo -e "${BLUE}🔍 Verificando instalación...${RESET}"

    if command -v trus &> /dev/null; then
        echo -e "${GREEN}✅ Comando 'trus' disponible${RESET}"
        trus --version
    else
        echo -e "${RED}❌ El comando 'trus' no se encontró${RESET}"
        echo "   Asegúrate de que /usr/local/bin está en tu PATH"
        exit 1
    fi
}

show_next_steps() {
    echo ""
    echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════════════════════════╗${RESET}"
    echo -e "${BOLD}${GREEN}║${RESET}              ✅ Instalación Completada!                      ${GREEN}${BOLD}║${RESET}"
    echo -e "${BOLD}${GREEN}╚══════════════════════════════════════════════════════════════╝${RESET}"
    echo ""
    echo -e "${YELLOW}📝 Próximos pasos:${RESET}"
    echo ""
    echo -e "  1. ${BOLD}Configurar conexión:${RESET}"
    echo -e "     ${CYAN}trus login${RESET}"
    echo ""
    echo -e "  2. ${BOLD}Ver estado:${RESET}"
    echo -e "     ${CYAN}trus status${RESET}"
    echo ""
    echo -e "  3. ${BOLD}Ver ayuda:${RESET}"
    echo -e "     ${CYAN}trus --help${RESET}"
    echo ""
    echo -e "  ${BOLD}Comandos principales:${RESET}"
    echo -e "    ${CYAN}trus recordar archivo.txt${RESET}   # Indexa un archivo"
    echo -e "    ${CYAN}trus recordar directorio/${RESET}  # Indexa un directorio"
    echo -e "    ${CYAN}trus query "pregunta"${RESET}      # Consulta la memoria"
    echo -e "    ${CYAN}trus config provider zai${RESET}   # Cambia proveedor LLM"
    echo ""
    echo -e "  ${YELLOW}Para desinstalar:${RESET}"
    echo -e "    ${CYAN}./install/uninstall-cli.sh${RESET}"
    echo ""
}

# Main
print_header
check_prerequisites
install_cli
verify_installation
show_next_steps
