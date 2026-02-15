#!/bin/bash
# TrustGraph CLI - Quick Installer
# Script standalone para instalar la CLI rápidamente
# Uso: curl -fsSL https://tudominio.com/install-cli.sh | bash
#   o: wget -qO- https://tudominio.com/install-cli.sh | bash

set -e

BLUE='\033[36m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
CYAN='\033[35m'
BOLD='\033[1m'
RESET='\033[0m'

REPO_URL="${TRUSTGRAPH_REPO:-https://github.com/tu-usuario/trustgraph}"
INSTALL_DIR="/opt/trustgraph-cli"
BIN_DIR="/usr/local/bin"
TEMP_DIR=$(mktemp -d)

cleanup() {
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

print_header() {
    echo ""
    echo -e "${BOLD}${BLUE}╔══════════════════════════════════════════════════════════════╗${RESET}"
    echo -e "${BOLD}${BLUE}║${RESET}     🤖 ${BOLD}TrustGraph CLI - Quick Install${RESET}                      ${BLUE}║${RESET}"
    echo -e "${BOLD}${BLUE}╚══════════════════════════════════════════════════════════════╝${RESET}"
    echo ""
}

download_cli() {
    echo -e "${BLUE}📥 Descargando TrustGraph CLI...${RESET}"

    # Intentar clonar o descargar
    if command -v git &> /dev/null; then
        git clone --depth 1 "$REPO_URL" "$TEMP_DIR/trustgraph" 2>/dev/null || {
            echo -e "${YELLOW}⚠️  No se pudo clonar, usando método alternativo...${RESET}"
            curl -fsSL "${REPO_URL}/archive/refs/heads/main.tar.gz" | tar -xz -C "$TEMP_DIR"
            mv "$TEMP_DIR"/*-main "$TEMP_DIR/trustgraph" 2>/dev/null || true
        }
    else
        curl -fsSL "${REPO_URL}/archive/refs/heads/main.tar.gz" | tar -xz -C "$TEMP_DIR"
        mv "$TEMP_DIR"/*-main "$TEMP_DIR/trustgraph"
    fi

    if [ ! -d "$TEMP_DIR/trustgraph/cli" ]; then
        echo -e "${RED}❌ No se pudo descargar la CLI${RESET}"
        exit 1
    fi

    echo -e "${GREEN}✅ Descarga completada${RESET}"
}

install_cli() {
    echo -e "${BLUE}📦 Instalando...${RESET}"

    # Crear directorio
    sudo mkdir -p "$INSTALL_DIR"

    # Copiar archivos
    sudo cp -r "$TEMP_DIR/trustgraph/cli/"* "$INSTALL_DIR/"

    # Instalar dependencias
    echo -e "${CYAN}   Instalando dependencias...${RESET}"
    sudo pip3 install -q -r "$INSTALL_DIR/requirements.txt" 2>/dev/null || {
        echo -e "${YELLOW}⚠️  Intentando con pip...${RESET}"
        sudo pip install -q -r "$INSTALL_DIR/requirements.txt"
    }

    # Crear enlace
    sudo ln -sf "$INSTALL_DIR/trus.py" "$BIN_DIR/trus"
    sudo chmod +x "$BIN_DIR/trus"

    echo -e "${GREEN}✅ Instalación completada${RESET}"
}

verify_installation() {
    if command -v trus &> /dev/null; then
        echo ""
        echo -e "${GREEN}✅ CLI instalada correctamente${RESET}"
        trus --version
        echo ""
        return 0
    else
        echo -e "${RED}❌ Error en la instalación${RESET}"
        return 1
    fi
}

show_next_steps() {
    echo -e "${BOLD}${CYAN}📝 Próximos pasos:${RESET}"
    echo ""
    echo -e "1. ${BOLD}Configurar conexión a tu servidor TrustGraph:${RESET}"
    echo -e "   ${GREEN}trus login${RESET}"
    echo ""
    echo -e "2. ${BOLD}Verificar conexión:${RESET}"
    echo -e "   ${GREEN}trus status${RESET}"
    echo ""
    echo -e "3. ${BOLD}Ver ayuda:${RESET}"
    echo -e "   ${GREEN}trus --help${RESET}"
    echo ""
}

# Main
print_header

# Verificar prerequisitos
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 es requerido${RESET}"
    exit 1
fi

if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo -e "${RED}❌ pip es requerido${RESET}"
    exit 1
fi

echo -e "${BLUE}📋 Verificando prerrequisitos...${RESET}"
echo -e "${GREEN}✅ Python disponible${RESET}"
echo ""

download_cli
install_cli

if verify_installation; then
    show_next_steps
fi
