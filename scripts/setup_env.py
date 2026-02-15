#!/usr/bin/env python3
"""
TrustGraph - Interactive Environment Setup
Configura .env de forma interactiva con menús navegables

Uso:
    python3 scripts/setup_env.py
    ./setup.sh makeenv
"""

import os
import sys
import subprocess
from pathlib import Path

# Colores para la terminal
BLUE = '\033[36m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
RED = '\033[31m'
CYAN = '\033[35m'
RESET = '\033[0m'
BOLD = '\033[1m'

# Configuración de proveedores
PROVIDERS = {
    "openai": {
        "name": "OpenAI",
        "description": "GPT-4, GPT-4o, GPT-3.5 - El estándar de la industria",
        "url": "https://platform.openai.com/api-keys",
        "env_key": "OPENAI_API_KEY",
        "model_default": "gpt-4o",
        "compatible": "OpenAI API",
    },
    "anthropic": {
        "name": "Anthropic",
        "description": "Claude 3.5 Sonnet - Excelente para código y análisis",
        "url": "https://console.anthropic.com/settings/keys",
        "env_key": "ANTHROPIC_API_KEY",
        "model_default": "claude-3-5-sonnet-20241022",
        "compatible": "Anthropic API",
    },
    "zai": {
        "name": "Z.AI (智谱AI / GLM)",
        "description": "GLM-5, GLM-4.6V - Modelos chinos avanzados",
        "url": "https://open.bigmodel.cn/usercenter/apikeys",
        "env_key": "ZAI_API_KEY",
        "model_default": "glm-5",
        "compatible": "OpenAI API (compatible)",
    },
    "kimi": {
        "name": "Kimi (Moonshot AI)",
        "description": "Kimi K2, Kimi Code - Especializado en coding",
        "url": "https://platform.moonshot.cn/console/api-keys",
        "env_key": "KIMI_API_KEY",
        "model_default": "kimi-k2",
        "compatible": "Anthropic API (compatible)",
    },
    "minimax": {
        "name": "MiniMax",
        "description": "MiniMax-M2.5 - Modelo chino con gran contexto",
        "url": "https://www.minimaxi.com/platform/settings/api-keys",
        "env_key": "MINIMAX_API_KEY",
        "model_default": "MiniMax-M2.5",
        "compatible": "Anthropic API (compatible)",
    },
    "ollama": {
        "name": "Ollama (Local)",
        "description": "Modelos locales - Privacidad total, sin costos",
        "url": "https://ollama.com/download",
        "env_key": None,
        "model_default": "llama3.1",
        "compatible": "Local (requiere Ollama instalado)",
    },
}

def clear_screen():
    """Limpia la pantalla."""
    os.system('clear' if os.name != 'nt' else 'cls')

def print_header():
    """Imprime el header del wizard."""
    print(f"""
{BOLD}{BLUE}╔══════════════════════════════════════════════════════════════╗{RESET}
{BOLD}{BLUE}║{RESET}     🤖  {BOLD}TrustGraph - Configuración de Proveedor LLM{RESET}         {BLUE}║{RESET}
{BOLD}{BLUE}╚══════════════════════════════════════════════════════════════╝{RESET}
""")

def print_provider_menu(current_selection=0):
    """Imprime el menú de selección de proveedor."""
    clear_screen()
    print_header()

    print(f"{YELLOW}📋 Selecciona tu proveedor de LLM:{RESET}\n")
    print(f"{CYAN}Usa las flechas ↑↓ para navegar, ENTER para seleccionar:{RESET}\n")

    providers_list = list(PROVIDERS.keys())

    for idx, key in enumerate(providers_list):
        provider = PROVIDERS[key]
        if idx == current_selection:
            print(f"{GREEN}  ▶ [{idx + 1}] {provider['name']:<20} {provider['description']}{RESET}")
        else:
            print(f"    [{idx + 1}] {provider['name']:<20} {provider['description']}")

    print(f"\n{CYAN}───────────────────────────────────────────────────────────────{RESET}")

    # Mostrar detalle del seleccionado
    selected = providers_list[current_selection]
    provider = PROVIDERS[selected]
    print(f"\n{BOLD}Detalle:{RESET}")
    print(f"  {YELLOW}Modelo por defecto:{RESET} {provider['model_default']}")
    print(f"  {YELLOW}Tipo API:{RESET} {provider['compatible']}")
    print(f"  {YELLOW}Obtener API key:{RESET} {provider['url']}")

    return providers_list

def get_key():
    """Lee una tecla del teclado sin necesidad de Enter."""
    try:
        import tty
        import termios
        import sys

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)

            # Detectar secuencias de escape (flechas)
            if ch == '\x1b':
                ch += sys.stdin.read(2)

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    except:
        # Fallback para Windows o si no hay soporte tty
        try:
            import msvcrt
            return msvcrt.getch().decode('utf-8')
        except:
            # Último fallback: input normal
            return input()

def select_provider_interactive():
    """Muestra menú interactivo y retorna el proveedor seleccionado."""
    providers_list = list(PROVIDERS.keys())
    current = 0

    while True:
        print_provider_menu(current)

        key = get_key()

        # Flecha arriba
        if key == '\x1b[A' or key == 'k':
            current = (current - 1) % len(providers_list)
        # Flecha abajo
        elif key == '\x1b[B' or key == 'j':
            current = (current + 1) % len(providers_list)
        # Enter
        elif key == '\r' or key == '\n':
            return providers_list[current]
        # Números 1-6
        elif key.isdigit():
            num = int(key) - 1
            if 0 <= num < len(providers_list):
                return providers_list[num]
        # q para salir
        elif key == 'q':
            print(f"\n{RED}❌ Cancelado por usuario{RESET}")
            sys.exit(0)

def select_provider_simple():
    """Fallback simple si no hay soporte para teclas especiales."""
    clear_screen()
    print_header()

    print(f"{YELLOW}📋 Selecciona tu proveedor de LLM:{RESET}\n")

    providers_list = list(PROVIDERS.keys())
    for idx, key in enumerate(providers_list, 1):
        provider = PROVIDERS[key]
        print(f"  {GREEN}[{idx}]{RESET} {provider['name']:<20} - {provider['description']}")

    print(f"\n  {RED}[0]{RESET} Cancelar")

    while True:
        try:
            choice = input(f"\n{CYAN}Selecciona una opción (0-{len(providers_list)}): {RESET}")

            if choice == "0":
                print(f"\n{RED}❌ Cancelado{RESET}")
                sys.exit(0)

            idx = int(choice) - 1
            if 0 <= idx < len(providers_list):
                return providers_list[idx]
            else:
                print(f"{RED}❌ Opción inválida{RESET}")
        except ValueError:
            print(f"{RED}❌ Por favor ingresa un número{RESET}")
        except KeyboardInterrupt:
            print(f"\n\n{RED}❌ Cancelado{RESET}")
            sys.exit(0)

def prompt_api_key(provider_key):
    """Solicita la API key del proveedor."""
    provider = PROVIDERS[provider_key]
    env_key = provider['env_key']

    if env_key is None:
        # Ollama no necesita API key
        return None

    clear_screen()
    print_header()

    print(f"{YELLOW}🔑 Configuración de {provider['name']}{RESET}\n")
    print(f"{CYAN}Obtén tu API key en:{RESET} {provider['url']}\n")

    while True:
        api_key = input(f"{CYAN}Ingresa tu {env_key}: {RESET}").strip()

        if not api_key:
            print(f"{RED}❌ La API key no puede estar vacía{RESET}")
            continue

        if api_key.lower() in ['cancelar', 'cancel', 'q', 'quit']:
            print(f"\n{RED}❌ Cancelado{RESET}")
            sys.exit(0)

        # Validación básica
        if len(api_key) < 10:
            print(f"{YELLOW}⚠️  La API key parece muy corta. ¿Estás seguro? (s/n){RESET}")
            confirm = input().strip().lower()
            if confirm not in ['s', 'si', 'y', 'yes']:
                continue

        return api_key

def prompt_model(provider_key, default_model):
    """Permite cambiar el modelo si se desea."""
    provider = PROVIDERS[provider_key]

    print(f"\n{CYAN}───────────────────────────────────────────────────────────────{RESET}")
    print(f"{YELLOW}🤖 Modelo seleccionado:{RESET} {GREEN}{default_model}{RESET}")

    change = input(f"\n{CYAN}¿Deseas cambiar el modelo? (s/N): {RESET}").strip().lower()

    if change in ['s', 'si', 'y', 'yes']:
        custom_model = input(f"{CYAN}Ingresa el nombre del modelo: {RESET}").strip()
        if custom_model:
            return custom_model

    return default_model

def create_env_file(provider_key, api_key=None, model=None):
    """Crea o actualiza el archivo .env."""
    env_path = Path('.env')
    env_example = Path('.env.example')

    # Si no existe .env, copiar de .env.example
    if not env_path.exists() and env_example.exists():
        print(f"\n{BLUE}📝 Creando .env desde .env.example...{RESET}")
        with open(env_example, 'r') as f:
            content = f.read()
    elif env_path.exists():
        print(f"\n{YELLOW}📝 Actualizando .env existente...{RESET}")
        with open(env_path, 'r') as f:
            content = f.read()
    else:
        content = ""

    # Actualizar variables del proveedor seleccionado
    provider = PROVIDERS[provider_key]

    # Actualizar LLM_PROVIDER
    if 'LLM_PROVIDER=' in content:
        content = subprocess.run(
            ['sed', f's/LLM_PROVIDER=.*/LLM_PROVIDER={provider_key}/'],
            input=content, capture_output=True, text=True
        ).stdout
    else:
        content += f"\nLLM_PROVIDER={provider_key}\n"

    # Actualizar API key si aplica
    if api_key and provider['env_key']:
        env_key = provider['env_key']
        if f'{env_key}=' in content:
            # Reemplazar existente
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                if line.startswith(f'{env_key}='):
                    new_lines.append(f'{env_key}={api_key}')
                else:
                    new_lines.append(line)
            content = '\n'.join(new_lines)
        else:
            content += f"{env_key}={api_key}\n"

    # Actualizar modelo
    model_key = f"{provider_key.upper()}_MODEL"
    if f'{model_key}=' in content:
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if line.startswith(f'{model_key}='):
                new_lines.append(f"{model_key}={model}")
            else:
                new_lines.append(line)
        content = '\n'.join(new_lines)
    else:
        content += f"{model_key}={model}\n"

    # Guardar archivo
    with open(env_path, 'w') as f:
        f.write(content)

    print(f"{GREEN}✅ Archivo .env actualizado{RESET}")

def show_summary(provider_key, api_key, model):
    """Muestra resumen de la configuración."""
    provider = PROVIDERS[provider_key]
    has_key = "✅ Configurada" if api_key else "⚪ No requerida"

    print(f"""
{GREEN}{BOLD}╔══════════════════════════════════════════════════════════════╗{RESET}
{GREEN}{BOLD}║{RESET}              ✅ Configuración Completada                      {GREEN}{BOLD}║{RESET}
{GREEN}{BOLD}╚══════════════════════════════════════════════════════════════╝{RESET}

  {YELLOW}Proveedor:{RESET}  {provider['name']}
  {YELLOW}Modelo:{RESET}     {model}
  {YELLOW}API Key:{RESET}    {has_key}

  {CYAN}Próximos pasos:{RESET}
    1. {BOLD}make up{RESET}     - Iniciar TrustGraph
    2. {BOLD}make load{RESET}   - Cargar documentación
    3. {BOLD}make query{RESET}  - Empezar a consultar

  {CYAN}Para cambiar de proveedor después:{RESET}
    {BOLD}make provider USE=nombre{RESET}
    # o
    {BOLD}python3 scripts/switch_provider.py{RESET}
""")

def main():
    try:
        # Intentar modo interactivo con flechas
        try:
            import tty
            import termios
            interactive_mode = True
        except ImportError:
            interactive_mode = False

        if interactive_mode:
            provider_key = select_provider_interactive()
        else:
            provider_key = select_provider_simple()

        # Obtener API key si es necesario
        api_key = prompt_api_key(provider_key)

        # Confirmar modelo
        provider = PROVIDERS[provider_key]
        model = prompt_model(provider_key, provider['model_default'])

        # Crear archivo .env
        create_env_file(provider_key, api_key, model)

        # Mostrar resumen
        clear_screen()
        show_summary(provider_key, api_key, model)

    except KeyboardInterrupt:
        print(f"\n\n{RED}❌ Cancelado por usuario{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}❌ Error: {e}{RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
