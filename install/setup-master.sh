#!/bin/bash
# TrustGraph Master Setup
# Script maestro con menú visual para todas las operaciones

set -e

BLUE='\033[36m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
CYAN='\033[35m'
BOLD='\033[1m'
RESET='\033[0m'

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CURRENT_SELECTION=0

MENU_OPTIONS=(
    "🖥️  Setup Completo Local (Servidor + CLI)"
    "🌐 Setup Solo CLI (para conectar a servidor remoto)"
    "📦 Setup Servidor Local (sin CLI)"
    "🌍 Configurar Acceso Remoto (para otros agentes)"
    "⚙️  Configurar Proveedor LLM"
    "🚀 Iniciar TrustGraph"
    "🛑 Detener TrustGraph"
    "📊 Ver Estado"
    "🗑️  Desinstalar CLI"
    "💥 Desinstalar Todo"
    "❌ Salir"
)

print_header() {
    clear
    echo ""
    echo -e "${BOLD}${BLUE}╔══════════════════════════════════════════════════════════════╗${RESET}"
    echo -e "${BOLD}${BLUE}║${RESET}     🤖 ${BOLD}TrustGraph Master Setup${RESET}                               ${BLUE}║${RESET}"
    echo -e "${BOLD}${BLUE}║${RESET}        Menú de Instalación y Configuración                   ${BLUE}║${RESET}"
    echo -e "${BOLD}${BLUE}╚══════════════════════════════════════════════════════════════╝${RESET}"
    echo ""
}

print_menu() {
    print_header

    echo -e "${YELLOW}Selecciona una opción:${RESET}"
    echo ""
    echo -e "${CYAN}Usa las flechas ↑↓ para navegar, ENTER para seleccionar${RESET}"
    echo ""

    for i in "${!MENU_OPTIONS[@]}"; do
        if [ $i -eq $CURRENT_SELECTION ]; then
            echo -e "${GREEN}  ▶ ${MENU_OPTIONS[$i]}${RESET}"
        else
            echo -e "    ${MENU_OPTIONS[$i]}"
        fi
    done

    echo ""
    echo -e "${CYAN}───────────────────────────────────────────────────────────────${RESET}"

    # Mostrar detalle de la opción seleccionada
    case $CURRENT_SELECTION in
        0)
            echo -e "\n${BOLD}Detalle:${RESET} Instala TrustGraph completo en esta máquina"
            echo -e "         Incluye: servidor Docker + CLI 'trus'"
            echo -e "         Ideal para: desarrollo local o servidor principal"
            ;;
        1)
            echo -e "\n${BOLD}Detalle:${RESET} Instala solo la CLI para conectarte a un servidor remoto"
            echo -e "         No incluye servidor Docker"
            echo -e "         Ideal para: agentes en otras máquinas"
            ;;
        2)
            echo -e "\n${BOLD}Detalle:${RESET} Instala solo el servidor sin CLI"
            echo -e "         Ideal para: servidores dedicados donde no usarás CLI"
            ;;
        3)
            echo -e "\n${BOLD}Detalle:${RESET} Configura el servidor para aceptar conexiones remotas"
            echo -e "         Abre puertos y configura autenticación"
            ;;
        4)
            echo -e "\n${BOLD}Detalle:${RESET} Cambia el proveedor de LLM (OpenAI, Z.AI, Kimi, etc.)"
            ;;
        5)
            echo -e "\n${BOLD}Detalle:${RESET} Inicia los servicios Docker de TrustGraph"
            ;;
        6)
            echo -e "\n${BOLD}Detalle:${RESET} Detiene los servicios Docker de TrustGraph"
            ;;
        7)
            echo -e "\n${BOLD}Detalle:${RESET} Muestra el estado de los servicios"
            ;;
        8)
            echo -e "\n${BOLD}Detalle:${RESET} Desinstala solo la CLI 'trus'"
            ;;
        9)
            echo -e "\n${BOLD}Detalle:${RESET} Desinstala TODO (CLI + Servidor + Datos)"
            echo -e "         ${RED}⚠️  Esto eliminará todos los datos${RESET}"
            ;;
        10)
            echo -e "\n${BOLD}Detalle:${RESET} Salir del instalador"
            ;;
    esac

    echo ""
}

get_key() {
    # Leer tecla sin Enter
    IFS= read -rs -n1 key

    # Detectar secuencias de escape (flechas)
    if [[ $key == $'\x1b' ]]; then
        read -rs -n2 rest
        key+="$rest"
    fi

    echo "$key"
}

run_interactive_menu() {
    while true; do
        print_menu
        key=$(get_key)

        # Flecha arriba
        if [[ $key == $'\x1b[A' ]]; then
            CURRENT_SELECTION=$((CURRENT_SELECTION - 1))
            if [ $CURRENT_SELECTION -lt 0 ]; then
                CURRENT_SELECTION=$((${#MENU_OPTIONS[@]} - 1))
            fi
        # Flecha abajo
        elif [[ $key == $'\x1b[B' ]]; then
            CURRENT_SELECTION=$((CURRENT_SELECTION + 1))
            if [ $CURRENT_SELECTION -ge ${#MENU_OPTIONS[@]} ]; then
                CURRENT_SELECTION=0
            fi
        # Enter
        elif [[ $key == $'\r' || $key == $'\n' ]]; then
            execute_option $CURRENT_SELECTION
            read -p "Presiona ENTER para continuar..."
        # q para salir
        elif [[ $key == 'q' ]]; then
            clear
            echo -e "${GREEN}👋 Adiós!${RESET}"
            exit 0
        fi
    done
}

execute_option() {
    clear
    cd "$REPO_DIR"

    case $1 in
        0)
            echo -e "${BLUE}🖥️  Ejecutando Setup Completo Local...${RESET}"
            ./install/setup-local.sh
            echo ""
            read -p "¿Deseas instalar la CLI también? [Y/n] " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                ./install/install-cli.sh
            fi
            ;;
        1)
            echo -e "${BLUE}🌐 Instalando Solo CLI...${RESET}"
            ./install/install-cli.sh
            echo ""
            echo -e "${YELLOW}Ahora configura la conexión a tu servidor:${RESET}"
            echo -e "   ${CYAN}trus login${RESET}"
            ;;
        2)
            echo -e "${BLUE}📦 Instalando Solo Servidor...${RESET}"
            ./install/setup-local.sh
            ;;
        3)
            echo -e "${BLUE}🌍 Configurando Acceso Remoto...${RESET}"
            ./install/setup-server.sh
            ;;
        4)
            echo -e "${BLUE}⚙️  Configurando Proveedor LLM...${RESET}"
            if [ -f "scripts/setup_env.py" ]; then
                python3 scripts/setup_env.py
            else
                echo -e "${YELLOW}Wizard no encontrado, editando .env manualmente...${RESET}"
                make provider
            fi
            ;;
        5)
            echo -e "${BLUE}🚀 Iniciando TrustGraph...${RESET}"
            make up
            ;;
        6)
            echo -e "${BLUE}🛑 Deteniendo TrustGraph...${RESET}"
            make down
            ;;
        7)
            echo -e "${BLUE}📊 Estado de TrustGraph...${RESET}"
            make status
            if command -v trus &> /dev/null; then
                trus status
            fi
            ;;
        8)
            echo -e "${BLUE}🗑️  Desinstalando CLI...${RESET}"
            ./install/uninstall-cli.sh
            ;;
        9)
            echo -e "${RED}💥 Desinstalando Todo...${RESET}"
            read -p "¿ESTÁS SEGURO? Esto eliminará todos los datos [escribe 'si' para confirmar]: " confirm
            if [ "$confirm" = "si" ]; then
                ./install/uninstall-cli.sh 2>/dev/null || true
                make down -v 2>/dev/null || true
                docker system prune -f 2>/dev/null || true
                rm -rf data/
                echo -e "${GREEN}✅ Desinstalación completa${RESET}"
            else
                echo -e "${YELLOW}❌ Cancelado${RESET}"
            fi
            ;;
        10)
            echo -e "${GREEN}👋 Adiós!${RESET}"
            exit 0
            ;;
    esac
}

# Modo simple (sin flechas) como fallback
run_simple_menu() {
    while true; do
        print_header
        echo -e "${YELLOW}Selecciona una opción:${RESET}\n"

        for i in "${!MENU_OPTIONS[@]}"; do
            num=$((i + 1))
            echo -e "  ${CYAN}[$num]${RESET} ${MENU_OPTIONS[$i]}"
        done

        echo ""
        echo -e "${CYAN}[0]${RESET} Salir"
        echo ""

        read -p "Opción: " choice

        case $choice in
            0) echo -e "${GREEN}👋 Adiós!${RESET}"; exit 0 ;;
            [1-9]|10|11)
                execute_option $((choice - 1))
                read -p "Presiona ENTER para continuar..."
                ;;
            *)
                echo -e "${RED}Opción inválida${RESET}"
                sleep 1
                ;;
        esac
    done
}

# Main
if [ -t 0 ] && [ -t 1 ]; then
    # Terminal interactiva disponible
    run_interactive_menu
else
    # Fallback para no-TTY
    run_simple_menu
fi
