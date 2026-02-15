#!/bin/bash
# TrustGraph CLI Uninstaller
# Desinstala la CLI 'trus' del sistema

set -e

BLUE='\033[36m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
BOLD='\033[1m'
RESET='\033[0m'

INSTALL_DIR="/opt/trustgraph-cli"
BIN_DIR="/usr/local/bin"
CONFIG_DIR="$HOME/.trustgraph"

print_header() {
    echo ""
    echo -e "${BOLD}${BLUE}╔══════════════════════════════════════════════════════════════╗${RESET}"
    echo -e "${BOLD}${BLUE}║${RESET}     🗑️  ${BOLD}TrustGraph CLI Uninstaller${RESET}                         ${BLUE}║${RESET}"
    echo -e "${BOLD}${BLUE}╚══════════════════════════════════════════════════════════════╝${RESET}"
    echo ""
}

ask_confirmation() {
    echo -e "${YELLOW}⚠️  Esto eliminará:${RESET}"
    echo "   - CLI en: $INSTALL_DIR"
    echo "   - Enlace en: $BIN_DIR/trus"
    echo "   - Configuración en: $CONFIG_DIR"
    echo ""
    read -p "¿Continuar? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}❌ Cancelado${RESET}"
        exit 0
    fi
}

uninstall_cli() {
    echo ""
    echo -e "${BLUE}🗑️  Desinstalando TrustGraph CLI...${RESET}"

    # Remove symlink
    if [ -L "$BIN_DIR/trus" ]; then
        echo -e "${CYAN}   Eliminando enlace simbólico...${RESET}"
        sudo rm "$BIN_DIR/trus"
    fi

    # Remove install directory
    if [ -d "$INSTALL_DIR" ]; then
        echo -e "${CYAN}   Eliminando archivos...${RESET}"
        sudo rm -rf "$INSTALL_DIR"
    fi

    # Ask about config
    echo ""
    read -p "¿Eliminar configuración ($CONFIG_DIR)? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -d "$CONFIG_DIR" ]; then
            echo -e "${CYAN}   Eliminando configuración...${RESET}"
            rm -rf "$CONFIG_DIR"
        fi
    fi

    echo ""
    echo -e "${GREEN}✅ CLI desinstalada correctamente${RESET}"
}

# Main
print_header
ask_confirmation
uninstall_cli

echo ""
echo -e "${GREEN}🗑️  Desinstalación completada${RESET}"
echo ""
