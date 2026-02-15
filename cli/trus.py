#!/usr/bin/env python3
"""
TrustGraph CLI - trus
Interfaz de línea de comandos para TrustGraph

Uso:
    trus --help
    trus login
    trus status
    trus recordar <archivo>
    trus recordar --directorio <ruta>
    trus recordar --proyecto
    trus query "pregunta"
    trus config provider zai
    trus config apikey
"""

import os
import sys
import json
import click
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict

# Colores
BLUE = '\033[36m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
RED = '\033[31m'
CYAN = '\033[35m'
BOLD = '\033[1m'
RESET = '\033[0m'

CONFIG_DIR = Path.home() / '.trustgraph'
CONFIG_FILE = CONFIG_DIR / 'config.json'

PROVIDERS = {
    'openai': {'name': 'OpenAI', 'model': 'gpt-4o', 'url': 'https://api.openai.com'},
    'anthropic': {'name': 'Anthropic', 'model': 'claude-3-5-sonnet', 'url': 'https://api.anthropic.com'},
    'zai': {'name': 'Z.AI (GLM)', 'model': 'glm-5', 'url': 'https://api.z.ai'},
    'kimi': {'name': 'Kimi', 'model': 'kimi-k2', 'url': 'https://api.kimi.com'},
    'minimax': {'name': 'MiniMax', 'model': 'MiniMax-M2.5', 'url': 'https://api.minimax.io'},
    'ollama': {'name': 'Ollama (Local)', 'model': 'llama3.1', 'url': 'http://localhost:11434'},
}


@dataclass
class TrustGraphConfig:
    """Configuración de TrustGraph CLI"""
    host: str = 'localhost'
    port: int = 8080
    api_gateway: str = 'http://localhost:8080'
    provider: str = 'openai'
    api_key: str = ''
    model: str = ''
    is_local: bool = True
    auth_token: str = ''

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


def ensure_config_dir():
    """Crea el directorio de configuración si no existe"""
    CONFIG_DIR.mkdir(exist_ok=True, parents=True)


def load_config() -> TrustGraphConfig:
    """Carga la configuración del usuario"""
    ensure_config_dir()
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
        return TrustGraphConfig.from_dict(data)
    return TrustGraphConfig()


def save_config(config: TrustGraphConfig):
    """Guarda la configuración del usuario"""
    ensure_config_dir()
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config.to_dict(), f, indent=2)


def check_connection(config: TrustGraphConfig) -> bool:
    """Verifica la conexión con TrustGraph"""
    try:
        response = requests.get(
            f"{config.api_gateway}/api/v1/health",
            timeout=5
        )
        return response.status_code == 200
    except:
        return False


def print_header(title: str):
    """Imprime un header formateado"""
    click.echo(f"""
{BOLD}{BLUE}╔══════════════════════════════════════════════════════════════╗{RESET}
{BOLD}{BLUE}║{RESET}  {title:<58} {BLUE}║{RESET}
{BOLD}{BLUE}╚══════════════════════════════════════════════════════════════╝{RESET}
""")


# ═══════════════════════════════════════════════════════════════
# GRUPO PRINCIPAL CLI
# ═══════════════════════════════════════════════════════════════

@click.group()
@click.version_option(version='1.0.0', prog_name='trus')
@click.pass_context
def cli(ctx):
    """
    🤖 TrustGraph CLI - Gestiona tu memoria de conocimiento

    Comandos principales:

    \b
      login      - Configura conexión local o remota
      recordar   - Guarda e indexa archivos/directorios
    \b
      query      - Consulta la memoria con GraphRAG
      status     - Verifica estado de TrustGraph
    \b
      config     - Configura proveedores LLM y opciones
      servicios  - Gestiona servicios (start/stop/logs)
    """
    ctx.ensure_object(dict)
    ctx.obj['config'] = load_config()


# ═══════════════════════════════════════════════════════════════
# COMANDO: LOGIN
# ═══════════════════════════════════════════════════════════════

@cli.command()
@click.option('--host', '-h', help='Host de TrustGraph (default: localhost)')
@click.option('--port', '-p', default=8080, help='Puerto del API Gateway')
@click.option('--remote', is_flag=True, help='Conexión remota')
@click.pass_context
def login(ctx, host, port, remote):
    """
    🔐 Configura la conexión con TrustGraph

    Pregunta interactivamente por la configuración si no se
    proporcionan opciones.
    """
    print_header("🔐 TrustGraph Login")

    config = ctx.obj['config']

    # Preguntar si es local o remoto
    if remote:
        config.is_local = False
    else:
        is_local = click.confirm(
            f"{CYAN}¿Es una instalación local?{RESET}",
            default=config.is_local
        )
        config.is_local = is_local

    # Configurar host
    if not host:
        default_host = 'localhost' if config.is_local else config.host
        host = click.prompt(
            f"{CYAN}Host de TrustGraph{RESET}",
            default=default_host
        )
    config.host = host
    config.port = port
    config.api_gateway = f"http://{host}:{port}"

    # Si es remoto, preguntar por token de autenticación
    if not config.is_local:
        click.echo(f"\n{YELLOW}⚠️  Conexión remota detectada{RESET}")
        token = click.prompt(
            f"{CYAN}Token de autenticación (opcional){RESET}",
            default=config.auth_token,
            hide_input=True
        )
        config.auth_token = token

    # Probar conexión
    click.echo(f"\n{BLUE}🔄 Probando conexión con {config.api_gateway}...{RESET}")

    if check_connection(config):
        click.echo(f"{GREEN}✅ Conexión exitosa!{RESET}")
        save_config(config)
        click.echo(f"\n{GREEN}💾 Configuración guardada en {CONFIG_FILE}{RESET}")
    else:
        click.echo(f"{YELLOW}⚠️  No se pudo conectar a {config.api_gateway}{RESET}")
        click.echo(f"{YELLOW}   Verifica que TrustGraph esté ejecutándose{RESET}")

        if click.confirm(f"{CYAN}¿Guardar configuración de todos modos?{RESET}"):
            save_config(config)


# ═══════════════════════════════════════════════════════════════
# COMANDO: RECORDAR (Guardar/Indexar)
# ═══════════════════════════════════════════════════════════════

@cli.group()
def recordar():
    """
    💾 Guarda e indexa información en TrustGraph

    Subcomandos:

    \b
      archivo     - Indexa un archivo específico
      directorio  - Indexa todos los archivos de un directorio
      proyecto    - Indexa el proyecto actual completo
    """
    pass


@recordar.command()
@click.argument('ruta', type=click.Path(exists=True))
@click.option('--categoria', '-c', default='documentacion', help='Categoría del documento')
@click.option('--etiquetas', '-t', help='Etiquetas separadas por coma')
@click.pass_context
def archivo(ctx, ruta, categoria, etiquetas):
    """Indexa un archivo específico"""
    config = ctx.obj['config']

    print_header(f"💾 Indexando: {Path(ruta).name}")

    # Verificar conexión
    if not check_connection(config):
        click.echo(f"{RED}❌ No hay conexión con TrustGraph{RESET}")
        click.echo(f"{YELLOW}   Ejecuta: trus login{RESET}")
        return

    # Leer archivo
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            contenido = f.read()
    except Exception as e:
        click.echo(f"{RED}❌ Error leyendo archivo: {e}{RESET}")
        return

    # Enviar a TrustGraph
    click.echo(f"{BLUE}📤 Enviando a TrustGraph...{RESET}")

    try:
        response = requests.post(
            f"{config.api_gateway}/api/v1/documents/upload",
            json={
                'path': ruta,
                'content': contenido,
                'category': categoria,
                'tags': etiquetas.split(',') if etiquetas else [],
            },
            timeout=60
        )

        if response.status_code == 200:
            click.echo(f"{GREEN}✅ Archivo indexado correctamente{RESET}")
            data = response.json()
            click.echo(f"{CYAN}   Entidades extraídas: {data.get('entities', 0)}{RESET}")
            click.echo(f"{CYAN}   Relaciones: {data.get('relations', 0)}{RESET}")
        else:
            click.echo(f"{RED}❌ Error: {response.status_code}{RESET}")
            click.echo(f"{RED}   {response.text}{RESET}")

    except Exception as e:
        click.echo(f"{RED}❌ Error de conexión: {e}{RESET}")


@recordar.command()
@click.argument('ruta', type=click.Path(exists=True, file_okay=False))
@click.option('--extensiones', '-e', default='.md,.txt,.py,.js,.ts', help='Extensiones a indexar')
@click.option('--excluir', '-x', help='Patrones a excluir (separados por coma)')
@click.option('--recursive', '-r', is_flag=True, default=True, help='Incluir subdirectorios')
@click.pass_context
def directorio(ctx, ruta, extensiones, excluir, recursive):
    """Indexa todos los archivos de un directorio"""
    config = ctx.obj['config']

    print_header(f"📁 Indexando directorio: {ruta}")

    if not check_connection(config):
        click.echo(f"{RED}❌ No hay conexión con TrustGraph{RESET}")
        return

    ext_list = extensiones.split(',')
    exclude_patterns = excluir.split(',') if excluir else ['node_modules', '.git', '__pycache__']

    # Encontrar archivos
    archivos = []
    base_path = Path(ruta)

    if recursive:
        for ext in ext_list:
            archivos.extend(base_path.rglob(f'*{ext}'))
    else:
        for ext in ext_list:
            archivos.extend(base_path.glob(f'*{ext}'))

    # Filtrar excluidos
    archivos = [a for a in archivos if not any(p in str(a) for p in exclude_patterns)]

    click.echo(f"{CYAN}📊 Encontrados {len(archivos)} archivos{RESET}\n")

    # Indexar cada archivo
    exitosos = 0
    for i, arch in enumerate(archivos, 1):
        click.echo(f"[{i}/{len(archivos)}] {arch.name}...", nl=False)
        try:
            with open(arch, 'r', encoding='utf-8') as f:
                contenido = f.read()

            response = requests.post(
                f"{config.api_gateway}/api/v1/documents/upload",
                json={'path': str(arch), 'content': contenido, 'category': 'documentacion'},
                timeout=60
            )

            if response.status_code == 200:
                click.echo(f" {GREEN}✓{RESET}")
                exitosos += 1
            else:
                click.echo(f" {RED}✗{RESET}")
        except:
            click.echo(f" {RED}✗{RESET}")

    click.echo(f"\n{GREEN}✅ Indexación completada: {exitosos}/{len(archivos)} exitosos{RESET}")


@recordar.command()
@click.pass_context
def proyecto(ctx):
    """Indexa el proyecto actual completo"""
    directorio(ctx, ruta='.', extensiones='.md,.txt,.py,.js,.ts,.json,.yaml,.yml')


# ═══════════════════════════════════════════════════════════════
# COMANDO: QUERY (Consultar)
# ═══════════════════════════════════════════════════════════════

@cli.command()
@click.argument('pregunta', required=False)
@click.option('--interactivo', '-i', is_flag=True, help='Modo interactivo')
@click.option('--fuentes', '-s', is_flag=True, help='Mostrar fuentes')
@click.pass_context
def query(ctx, pregunta, interactivo, fuentes):
    """
    🔍 Consulta la memoria con GraphRAG

    Ejemplos:

        trus query "¿Qué es TrustGraph?"

        trus query -i              # Modo interactivo

        trus query "arquitectura" --fuentes
    """
    config = ctx.obj['config']

    if not check_connection(config):
        click.echo(f"{RED}❌ No hay conexión con TrustGraph{RESET}")
        click.echo(f"{YELLOW}   Ejecuta: trus login{RESET}")
        return

    if interactivo or not pregunta:
        # Modo interactivo
        print_header("🔍 TrustGraph Query - Modo Interactivo")
        click.echo(f"{CYAN}Escribe 'salir' o 'quit' para terminar{RESET}\n")

        while True:
            pregunta = click.prompt(f"{BLUE}❓ Pregunta{RESET}")

            if pregunta.lower() in ['salir', 'quit', 'exit', 'q']:
                break

            _ejecutar_query(config, pregunta, fuentes)
            click.echo("")
    else:
        print_header("🔍 TrustGraph Query")
        _ejecutar_query(config, pregunta, fuentes)


def _ejecutar_query(config: TrustGraphConfig, pregunta: str, fuentes: bool):
    """Ejecuta una consulta GraphRAG"""
    click.echo(f"{BLUE}🤔 Pensando...{RESET}\n")

    try:
        response = requests.post(
            f"{config.api_gateway}/api/v1/graphrag/query",
            json={
                'query': pregunta,
                'context_core': 'documentation',
                'include_sources': fuentes,
            },
            timeout=120
        )

        if response.status_code == 200:
            data = response.json()
            respuesta = data.get('response', 'Sin respuesta')

            click.echo(f"{GREEN}📝 Respuesta:{RESET}\n")
            click.echo(respuesta)

            if fuentes and 'sources' in data:
                click.echo(f"\n{CYAN}📚 Fuentes:{RESET}")
                for src in data['sources'][:5]:
                    click.echo(f"   • {src}")
        else:
            click.echo(f"{RED}❌ Error: {response.status_code}{RESET}")
            click.echo(f"{RED}   {response.text}{RESET}")

    except Exception as e:
        click.echo(f"{RED}❌ Error: {e}{RESET}")


# ═══════════════════════════════════════════════════════════════
# COMANDO: STATUS
# ═══════════════════════════════════════════════════════════════

@cli.command()
@click.pass_context
def status(ctx):
    """
    📊 Muestra el estado de TrustGraph y la configuración
    """
    config = ctx.obj['config']

    print_header("📊 TrustGraph Status")

    # Configuración
    click.echo(f"{BOLD}⚙️  Configuración:{RESET}")
    click.echo(f"   Host: {config.host}")
    click.echo(f"   Puerto: {config.port}")
    click.echo(f"   API Gateway: {config.api_gateway}")
    click.echo(f"   Tipo: {'Local' if config.is_local else 'Remoto'}")
    click.echo(f"   Proveedor LLM: {PROVIDERS.get(config.provider, {}).get('name', config.provider)}")
    click.echo("")

    # Conexión
    click.echo(f"{BOLD}🔌 Conectividad:{RESET}")
    if check_connection(config):
        click.echo(f"   {GREEN}✅ TrustGraph está activo{RESET}")

        try:
            response = requests.get(f"{config.api_gateway}/api/v1/health")
            data = response.json()
            click.echo(f"   Versión: {data.get('version', 'N/A')}")
            click.echo(f"   Estado: {data.get('status', 'N/A')}")
        except:
            pass
    else:
        click.echo(f"   {RED}❌ TrustGraph no responde{RESET}")
        click.echo(f"   {YELLOW}   Verifica que esté ejecutándose:{RESET}")
        if config.is_local:
            click.echo(f"   {YELLOW}   make up{RESET}")

    click.echo("")


# ═══════════════════════════════════════════════════════════════
# COMANDO: CONFIG
# ═══════════════════════════════════════════════════════════════

@cli.group()
def config():
    """
    ⚙️  Configura TrustGraph y proveedores LLM

    Subcomandos:

    \b
      provider   - Cambia el proveedor de LLM
      apikey     - Configura la API key
      model      - Cambia el modelo
      show       - Muestra configuración actual
    """
    pass


@config.command()
@click.pass_context
def show(ctx):
    """Muestra la configuración actual"""
    config = ctx.obj['config']

    print_header("⚙️  Configuración Actual")

    click.echo(f"{BOLD}Conexión:{RESET}")
    click.echo(f"  Host: {CYAN}{config.host}{RESET}")
    click.echo(f"  Puerto: {CYAN}{config.port}{RESET}")
    click.echo(f"  API Gateway: {CYAN}{config.api_gateway}{RESET}")
    click.echo(f"  Local: {CYAN}{config.is_local}{RESET}")

    click.echo(f"\n{BOLD}Proveedor LLM:{RESET}")
    click.echo(f"  Proveedor: {CYAN}{config.provider}{RESET}")
    click.echo(f"  Modelo: {CYAN}{config.model or 'Por defecto'}{RESET}")
    click.echo(f"  API Key: {CYAN}{'*' * 8 if config.api_key else 'No configurada'}{RESET}")

    click.echo(f"\n{BOLD}Archivo:{RESET}")
    click.echo(f"  {CONFIG_FILE}")


@config.command()
@click.argument('nombre', required=False)
@click.pass_context
def provider(ctx, nombre):
    """
    Cambia el proveedor de LLM

    Proveedores: openai, anthropic, zai, kimi, minimax, ollama
    """
    config = ctx.obj['config']

    if not nombre:
        # Mostrar menú
        print_header("🤖 Selecciona Proveedor LLM")

        for key, info in PROVIDERS.items():
            marker = "👉" if key == config.provider else "  "
            click.echo(f"{marker} {GREEN}{key:12}{RESET} - {info['name']}")
            click.echo(f"      {info['description']}")

        nombre = click.prompt(f"\n{CYAN}Proveedor{RESET}", type=str)

    if nombre not in PROVIDERS:
        click.echo(f"{RED}❌ Proveedor '{nombre}' no soportado{RESET}")
        click.echo(f"{YELLOW}   Opciones: {', '.join(PROVIDERS.keys())}{RESET}")
        return

    config.provider = nombre
    config.model = PROVIDERS[nombre]['model']
    save_config(config)

    click.echo(f"{GREEN}✅ Proveedor cambiado a: {PROVIDERS[nombre]['name']}{RESET}")
    click.echo(f"{CYAN}   Modelo: {config.model}{RESET}")

    # Si es local, también actualizar .env
    if config.is_local:
        click.echo(f"\n{YELLOW}⚠️  Para aplicar cambios en el servidor local:{RESET}")
        click.echo(f"   make provider USE={nombre}")
        click.echo(f"   docker compose restart")


@config.command()
@click.pass_context
def apikey(ctx):
    """Configura la API key del proveedor actual"""
    config = ctx.obj['config']

    provider_info = PROVIDERS.get(config.provider, {})
    provider_name = provider_info.get('name', config.provider)

    print_header(f"🔑 API Key - {provider_name}")

    if config.provider == 'ollama':
        click.echo(f"{YELLOW}ℹ️  Ollama no requiere API key{RESET}")
        return

    click.echo(f"{CYAN}Obtén tu API key en:{RESET} {provider_info.get('url', 'N/A')}\n")

    api_key = click.prompt(
        f"{CYAN}API Key para {provider_name}{RESET}",
        hide_input=True
    )

    if api_key:
        config.api_key = api_key
        save_config(config)
        click.echo(f"{GREEN}✅ API key guardada{RESET}")

        if config.is_local:
            click.echo(f"\n{YELLOW}⚠️  También actualiza el archivo .env del servidor{RESET}")


@config.command()
@click.argument('nombre', required=False)
@click.pass_context
def model(ctx, nombre):
    """Cambia el modelo del proveedor actual"""
    config = ctx.obj['config']

    provider_info = PROVIDERS.get(config.provider, {})
    default_model = config.model or provider_info.get('model', '')

    if not nombre:
        nombre = click.prompt(
            f"{CYAN}Modelo{RESET}",
            default=default_model
        )

    config.model = nombre
    save_config(config)

    click.echo(f"{GREEN}✅ Modelo cambiado a: {nombre}{RESET}")


# ═══════════════════════════════════════════════════════════════
# COMANDO: SERVICIOS (Gestión de servicios locales)
# ═══════════════════════════════════════════════════════════════

@cli.group()
def servicios():
    """
    🚀 Gestiona los servicios TrustGraph (solo local)

    Subcomandos:

    \b
      start    - Inicia TrustGraph
      stop     - Detiene TrustGraph
      restart  - Reinicia TrustGraph
      logs     - Muestra logs
    """
    pass


@servicios.command()
@click.pass_context
def start(ctx):
    """Inicia TrustGraph"""
    config = ctx.obj['config']

    if not config.is_local:
        click.echo(f"{RED}❌ Este comando solo funciona en modo local{RESET}")
        return

    print_header("🚀 Iniciando TrustGraph")
    os.system('docker compose up -d')


@servicios.command()
@click.pass_context
def stop(ctx):
    """Detiene TrustGraph"""
    config = ctx.obj['config']

    if not config.is_local:
        click.echo(f"{RED}❌ Este comando solo funciona en modo local{RESET}")
        return

    print_header("🛑 Deteniendo TrustGraph")
    os.system('docker compose down')


@servicios.command()
@click.pass_context
def restart(ctx):
    """Reinicia TrustGraph"""
    config = ctx.obj['config']

    if not config.is_local:
        click.echo(f"{RED}❌ Este comando solo funciona en modo local{RESET}")
        return

    print_header("🔄 Reiniciando TrustGraph")
    os.system('docker compose restart')


@servicios.command()
@click.option('--seguir', '-f', is_flag=True, help='Seguir logs en tiempo real')
@click.pass_context
def logs(ctx, seguir):
    """Muestra los logs de TrustGraph"""
    config = ctx.obj['config']

    if not config.is_local:
        click.echo(f"{RED}❌ Este comando solo funciona en modo local{RESET}")
        return

    if seguir:
        os.system('docker compose logs -f')
    else:
        os.system('docker compose logs --tail=100')


# ═══════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    cli()
