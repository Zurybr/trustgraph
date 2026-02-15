#!/usr/bin/env python3
"""
TrustGraph - Provider Switcher
Facilita el cambio entre diferentes proveedores de LLM

Uso:
    python switch_provider.py <provider>

Proveedores soportados:
    openai    - OpenAI GPT-4/GPT-3.5
    anthropic - Anthropic Claude
    zai       - Z.AI GLM-5/GLM-4.6V (OpenAI-compatible)
    kimi      - Kimi K2/Kimi Code (Anthropic-compatible)
    minimax   - MiniMax-M2.5 (Anthropic-compatible)
    ollama    - Modelos locales via Ollama

Ejemplos:
    python switch_provider.py zai
    python switch_provider.py kimi
    python switch_provider.py minimax
"""

import os
import sys
import re
from pathlib import Path

# Configuración de proveedores
PROVIDERS = {
    "openai": {
        "name": "OpenAI",
        "description": "GPT-4, GPT-3.5, GPT-4o",
        "env_vars": {
            "LLM_PROVIDER": "openai",
            "OPENAI_BASE_URL": "https://api.openai.com/v1",
            "OPENAI_MODEL": "gpt-4o",
        },
        "required_keys": ["OPENAI_API_KEY"],
    },
    "anthropic": {
        "name": "Anthropic",
        "description": "Claude 3.5 Sonnet, Claude 3 Opus",
        "env_vars": {
            "LLM_PROVIDER": "anthropic",
            "ANTHROPIC_BASE_URL": "https://api.anthropic.com",
            "ANTHROPIC_MODEL": "claude-3-5-sonnet-20241022",
        },
        "required_keys": ["ANTHROPIC_API_KEY"],
    },
    "zai": {
        "name": "Z.AI (智谱AI/GLM)",
        "description": "GLM-5, GLM-4.6V, GLM-Image",
        "env_vars": {
            "LLM_PROVIDER": "zai",
            "ZAI_BASE_URL": "https://api.z.ai/api/paas/v4",
            "ZAI_MODEL": "glm-5",
        },
        "required_keys": ["ZAI_API_KEY"],
        "note": "Para Coding usa: https://api.z.ai/api/coding/paas/v4",
    },
    "kimi": {
        "name": "Kimi (Moonshot AI)",
        "description": "Kimi K2, Kimi Code",
        "env_vars": {
            "LLM_PROVIDER": "kimi",
            "KIMI_BASE_URL": "https://api.kimi.com/coding",
            "KIMI_MODEL": "kimi-k2",
        },
        "required_keys": ["KIMI_API_KEY"],
        "note": "Compatible con API Anthropic",
    },
    "minimax": {
        "name": "MiniMax",
        "description": "MiniMax-M2.5",
        "env_vars": {
            "LLM_PROVIDER": "minimax",
            "MINIMAX_BASE_URL": "https://api.minimax.io/anthropic",
            "MINIMAX_MODEL": "MiniMax-M2.5",
        },
        "required_keys": ["MINIMAX_API_KEY"],
        "note": "Usa https://api.minimaxi.com/anthropic para China",
    },
    "ollama": {
        "name": "Ollama (Local)",
        "description": "Modelos locales: llama3.1, qwen, etc.",
        "env_vars": {
            "LLM_PROVIDER": "ollama",
            "OLLAMA_BASE_URL": "http://host.docker.internal:11434",
            "OLLAMA_MODEL": "llama3.1",
        },
        "required_keys": [],
        "note": "Requiere Ollama instalado localmente",
    },
}


def get_project_root() -> Path:
    """Obtiene la raíz del proyecto."""
    return Path(__file__).parent.parent.resolve()


def read_env_file() -> dict:
    """Lee el archivo .env y devuelve un diccionario."""
    env_path = get_project_root() / ".env"
    env_vars = {}

    if not env_path.exists():
        print(f"❌ Archivo .env no encontrado en {env_path}")
        print("   Ejecuta primero: cp .env.example .env")
        return env_vars

    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env_vars[key] = value

    return env_vars


def write_env_file(env_vars: dict):
    """Escribe el diccionario al archivo .env."""
    env_path = get_project_root() / ".env"

    # Leer el contenido actual para preservar comentarios
    if env_path.exists():
        with open(env_path, "r") as f:
            lines = f.readlines()
    else:
        lines = []

    # Actualizar variables existentes
    updated_vars = set()
    new_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0]
            if key in env_vars:
                new_lines.append(f"{key}={env_vars[key]}\n")
                updated_vars.add(key)
                continue
        new_lines.append(line)

    # Agregar variables nuevas al final
    for key, value in env_vars.items():
        if key not in updated_vars:
            new_lines.append(f"{key}={value}\n")

    with open(env_path, "w") as f:
        f.writelines(new_lines)


def check_provider_config(provider: str, env_vars: dict) -> bool:
    """Verifica si el proveedor tiene la configuración necesaria."""
    if provider not in PROVIDERS:
        return False

    config = PROVIDERS[provider]
    missing = []

    for key in config["required_keys"]:
        if not env_vars.get(key) or env_vars.get(key) == f"your-{provider}-api-key":
            missing.append(key)

    if missing:
        print(f"\n⚠️  Faltan las siguientes API keys en .env:")
        for key in missing:
            print(f"   - {key}")
        print(f"\n📝 Edita el archivo .env y agrega tus credenciales.")
        return False

    return True


def switch_provider(provider: str):
    """Cambia el proveedor de LLM."""
    if provider not in PROVIDERS:
        print(f"❌ Proveedor '{provider}' no soportado.")
        print(f"\nProveedores disponibles:")
        for key, config in PROVIDERS.items():
            print(f"   {key:12} - {config['name']}: {config['description']}")
        sys.exit(1)

    config = PROVIDERS[provider]
    env_vars = read_env_file()

    print(f"\n🔧 Cambiando a proveedor: {config['name']}")
    print(f"   {config['description']}")

    # Actualizar variables
    for key, value in config["env_vars"].items():
        env_vars[key] = value

    write_env_file(env_vars)

    print(f"\n✅ Configuración actualizada en .env")

    if "note" in config:
        print(f"\n💡 Nota: {config['note']}")

    # Verificar configuración
    if check_provider_config(provider, env_vars):
        print(f"\n🚀 Todo listo. Reinicia TrustGraph para aplicar cambios:")
        print(f"   docker compose restart")
    else:
        print(f"\n⚠️  Configuración incompleta. Agrega tus API keys antes de reiniciar.")


def show_current_provider():
    """Muestra el proveedor actual."""
    env_vars = read_env_file()
    current = env_vars.get("LLM_PROVIDER", "openai")

    print(f"\n📊 Proveedor actual: {current}")

    if current in PROVIDERS:
        config = PROVIDERS[current]
        print(f"   Nombre: {config['name']}")
        print(f"   Modelo: {config['env_vars'].get(f'{current.upper()}_MODEL', 'N/A')}")

        # Verificar si las credenciales están configuradas
        if check_provider_config(current, env_vars):
            print(f"   Estado: ✅ Configurado")
        else:
            print(f"   Estado: ⚠️  Falta configurar credenciales")
    else:
        print(f"   ⚠️  Proveedor no reconocido")


def show_status():
    """Muestra el estado de todos los proveedores."""
    env_vars = read_env_file()
    current = env_vars.get("LLM_PROVIDER", "openai")

    print(f"\n📊 Estado de Proveedores LLM")
    print("=" * 60)

    for key, config in PROVIDERS.items():
        is_active = key == current
        status_icon = "🟢" if is_active else "⚪"

        # Verificar credenciales
        has_creds = all(
            env_vars.get(k) and not env_vars.get(k).startswith("your-")
            for k in config["required_keys"]
        ) if config["required_keys"] else True

        cred_icon = "🔑" if has_creds else "❌"

        print(f"\n{status_icon} {key:12} {cred_icon} {config['name']}")
        print(f"   Modelo: {config['env_vars'].get(f'{key.upper()}_MODEL', 'N/A')}")

        if is_active:
            base_url = config["env_vars"].get(f"{key.upper()}_BASE_URL", "")
            if base_url:
                print(f"   URL: {base_url}")

    print(f"\n" + "=" * 60)
    print(f"Para cambiar de proveedor: python switch_provider.py <nombre>")


def interactive_menu():
    """Muestra un menú interactivo para seleccionar proveedor."""
    print("\n" + "=" * 60)
    print("🤖  TrustGraph - Selector de Proveedor LLM")
    print("=" * 60)

    # Mostrar estado actual
    env_vars = read_env_file()
    current = env_vars.get("LLM_PROVIDER", "openai")
    print(f"\n📍 Proveedor actual: {current}")

    # Mostrar opciones
    print("\n📋 Proveedores disponibles:")
    print("-" * 60)

    providers_list = list(PROVIDERS.keys())
    for i, key in enumerate(providers_list, 1):
        config = PROVIDERS[key]
        marker = "👉" if key == current else "  "
        print(f"{marker} {i}. {key:12} - {config['name']}")
        print(f"      {config['description']}")

    print("-" * 60)
    print("  0. Cancelar / Salir")
    print("=" * 60)

    try:
        choice = input("\nSelecciona una opción (0-{}): ".format(len(providers_list)))

        if choice == "0":
            print("\n❌ Cancelado")
            sys.exit(0)

        idx = int(choice) - 1
        if 0 <= idx < len(providers_list):
            return providers_list[idx]
        else:
            print("\n❌ Opción inválida")
            sys.exit(1)
    except ValueError:
        print("\n❌ Por favor ingresa un número")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n❌ Cancelado")
        sys.exit(0)


def main():
    if len(sys.argv) < 2:
        # Sin argumentos: mostrar menú interactivo
        provider = interactive_menu()
        switch_provider(provider)
    else:
        command = sys.argv[1]

        if command in ["status", "--status", "-s"]:
            show_status()
        elif command in ["--help", "-h", "help"]:
            print(__doc__)
            print(f"\nProveedores soportados:")
            for key, config in PROVIDERS.items():
                print(f"   {key:12} - {config['name']}: {config['description']}")
        else:
            switch_provider(command)


if __name__ == "__main__":
    main()
