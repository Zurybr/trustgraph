#!/usr/bin/env python3
"""
TrustGraph CLI - trus
Interfaz de línea de comandos para TrustGraph

Estructura:
  trus infra     - Gestión de infraestructura Docker
  trus agentes   - Configuración de agentes y LLM
  trus recordar  - Indexar contenido
  trus query     - Consultar memoria
"""

import os
import sys
import json
import click
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict, field

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

# Proveedores disponibles
PROVIDERS = {
    'openai': {'name': 'OpenAI', 'model': 'gpt-4o', 'url': 'https://api.openai.com'},
    'anthropic': {'name': 'Anthropic', 'model': 'claude-3-5-sonnet', 'url': 'https://api.anthropic.com'},
    'zai': {'name': 'Z.AI (GLM)', 'model': 'glm-5', 'url': 'https://api.z.ai'},
    'kimi': {'name': 'Kimi', 'model': 'kimi-k2', 'url': 'https://api.kimi.com'},
    'minimax': {'name': 'MiniMax', 'model': 'MiniMax-M2.5', 'url': 'https://api.minimax.io'},
    'ollama': {'name': 'Ollama (Local)', 'model': 'llama3.1', 'url': 'http://localhost:11434'},
}

# Agentes disponibles
AGENTES = ['bibliotecario', 'investigador', 'nocturno']


@dataclass
class AgentConfig:
    """Configuración de un agente específico"""
    proveedor: str = 'openai'
    api_key: str = ''
    modelo: str = ''
    activo: bool = True

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


@dataclass
class TrustGraphConfig:
    """Configuración principal de TrustGraph"""
    host: str = 'localhost'
    port: int = 8080
    api_gateway: str = 'http://localhost:8080'
    is_local: bool = True
    auth_token: str = ''

    # Configuración global de LLM (para compartir)
    global_provider: str = 'openai'
    global_api_key: str = ''
    global_model: str = ''

    # Configuración por agente
    agentes: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def get_agent_config(self, agente: str) -> AgentConfig:
        """Obtiene configuración de un agente específico"""
        if agente in self.agentes:
            return AgentConfig.from_dict(self.agentes[agente])
        return AgentConfig()

    def set_agent_config(self, agente: str, config: AgentConfig):
        """Guarda configuración de un agente"""
        self.agentes[agente] = config.to_dict()


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


def check_connection(api_gateway: str) -> bool:
    """Verifica la conexión con TrustGraph"""
    try:
        response = requests.get(f"{api_gateway}/api/v1/health", timeout=5)
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
@click.version_option(version='2.0.0', prog_name='trus')
@click.pass_context
def cli(ctx):
    """
    🤖 TrustGraph CLI - Gestiona tu memoria de conocimiento

    Comandos principales:

    \b
      infra       - Gestión de infraestructura Docker
      agentes     - Configuración de agentes y LLM
      recordar    - Indexa archivos en TrustGraph
      query       - Consulta la memoria
    """
    ctx.ensure_object(dict)
    ctx.obj['config'] = load_config()


# ═══════════════════════════════════════════════════════════════
# GRUPO: INFRAESTRUCTURA (Docker)
# ═══════════════════════════════════════════════════════════════

@cli.group()
def infra():
    """
    🐳 Gestión de infraestructura Docker

    Comandos:

    \b
      start     - Inicia los servicios Docker
      stop      - Detiene los servicios
      restart   - Reinicia los servicios
      status    - Ver estado de servicios
      logs      - Ver logs de servicios
      setup     - Configura entorno Docker
    """
    pass


@infra.command()
@click.pass_context
def start(ctx):
    """Inicia los servicios Docker de TrustGraph"""
    print_header("🐳 Iniciando TrustGraph")
    os.system('docker compose up -d')
    click.echo(f"{GREEN}✅ Servicios iniciados{RESET}")


@infra.command()
@click.pass_context
def stop(ctx):
    """Detiene los servicios Docker"""
    print_header("🛑 Deteniendo TrustGraph")
    os.system('docker compose down')
    click.echo(f"{GREEN}✅ Servicios detenidos{RESET}")


@infra.command()
@click.pass_context
def restart(ctx):
    """Reinicia los servicios Docker"""
    print_header("🔄 Reiniciando TrustGraph")
    os.system('docker compose restart')
    click.echo(f"{GREEN}✅ Servicios reiniciados{RESET}")


@infra.command()
@click.pass_context
def status(ctx):
    """Muestra el estado de los servicios Docker"""
    print_header("📊 Estado de Servicios")
    os.system('docker compose ps')


@infra.command()
@click.option('--seguir', '-f', is_flag=True, help='Seguir logs en tiempo real')
@click.pass_context
def logs(ctx, seguir):
    """Muestra los logs de los servicios"""
    if seguir:
        os.system('docker compose logs -f')
    else:
        os.system('docker compose logs --tail=100')


@infra.command()
@click.pass_context
def setup(ctx):
    """Configura el entorno Docker (crea .env si no existe)"""
    print_header("⚙️ Setup de Infraestructura")

    env_file = Path('.env')
    env_example = Path('.env.example')

    if env_file.exists():
        click.echo(f"{YELLOW}ℹ️  El archivo .env ya existe{RESET}")
    elif env_example.exists():
        click.echo(f"{CYAN}📄 Copiando .env.example → .env{RESET}")
        import shutil
        shutil.copy('.env.example', '.env')
        click.echo(f"{GREEN}✅ Archivo .env creado{RESET}")
        click.echo(f"{YELLOW}⚠️  Edita .env con tus configuraciones{RESET}")
    else:
        click.echo(f"{RED}❌ No se encontró .env.example{RESET}")


@infra.command()
@click.pass_context
def health(ctx):
    """Verifica la salud de los servicios"""
    config = ctx.obj['config']
    api_url = f"{config.api_gateway}/api/v1/health"

    print_header("🏥 Health Check")

    if check_connection(config.api_gateway):
        try:
            response = requests.get(api_url, timeout=5)
            data = response.json()
            click.echo(f"{GREEN}✅ API Gateway: OK{RESET}")
            click.echo(f"   Versión: {data.get('version', 'N/A')}")
            click.echo(f"   Estado: {data.get('status', 'N/A')}")
        except Exception as e:
            click.echo(f"{RED}❌ Error: {e}{RESET}")
    else:
        click.echo(f"{RED}❌ API Gateway no responde{RESET}")
        click.echo(f"{YELLOW}   URL: {api_url}{RESET}")


# ═══════════════════════════════════════════════════════════════
# GRUPO: AGENTES (Configuración LLM)
# ═══════════════════════════════════════════════════════════════

@cli.group()
def agentes():
    """
    🤖 Configuración de agentes inteligentes

    Comandos:

    \b
      config      - Configura proveedor y API key
      config-global   - Configura LLM compartido por todos
      config-agente   - Configura LLM de un agente específico
      show        - Muestra configuración actual
      status      - Muestra estado de los agentes
    """
    pass


@agentes.command()
@click.pass_context
def show(ctx):
    """Muestra la configuración de todos los agentes"""
    config = ctx.obj['config']

    print_header("⚙️ Configuración de Agentes")

    # Configuración global
    click.echo(f"{BOLD}📡 Configuración Global:{RESET}")
    click.echo(f"   Proveedor: {CYAN}{config.global_provider}{RESET}")
    click.echo(f"   Modelo: {CYAN}{config.global_model or 'Por defecto'}{RESET}")
    click.echo(f"   API Key: {CYAN}{'*' * 8 if config.global_api_key else 'No configurada'}{RESET}")

    click.echo(f"\n{BOLD}📱 Configuración por Agente:{RESET}")

    for agente in AGENTES:
        agent_cfg = config.get_agent_config(agente)

        # Si no tiene config específica, usar la global
        if not agent_cfg.api_key:
            proveedor = agent_cfg.proveedor or config.global_provider
            modelo = agent_cfg.modelo or config.global_model or PROVIDERS.get(proveedor, {}).get('model', '')
            api_key = f"{'*' * 8} (global)"
        else:
            proveedor = agent_cfg.proveedor
            modelo = agent_cfg.modelo or PROVIDERS.get(proveedor, {}).get('model', '')
            api_key = f"{'*' * 8}"

        status_icon = f"{GREEN}✅" if agent_cfg.activo else f"{YELLOW}⏸️"

        click.echo(f"\n   {status_icon} {agente.capitalize()}:")
        click.echo(f"      Proveedor: {CYAN}{proveedor}{RESET}")
        click.echo(f"      Modelo: {CYAN}{modelo}{RESET}")
        click.echo(f"      API Key: {CYAN}{api_key}{RESET}")

    click.echo(f"\n{BOLD}📁 Archivo de configuración:{RESET}")
    click.echo(f"   {CONFIG_FILE}")


@agentes.command()
@click.pass_context
def status(ctx):
    """Muestra el estado de los agentes"""
    config = ctx.obj['config']
    api_ok = check_connection(config.api_gateway)

    print_header("🤖 Estado de Agentes")

    click.echo(f"{GREEN}✅" if api_ok else f"{RED}❌", end='')
    click.echo(f" API Gateway: {config.api_gateway}")

    for agente in AGENTES:
        agent_cfg = config.get_agent_config(agente)

        # Verificar si tiene API key (local o global)
        has_key = bool(agent_cfg.api_key or config.global_api_key)

        icon = f"{GREEN}✅" if has_key else f"{YELLOW}⚠️"
        status = "Configurado" if has_key else "Sin API Key"

        click.echo(f"{icon} {agente.capitalize()}: {status}")

    click.echo(f"\n{CYAN}💡 Usa 'trus agentes config --help' para configurar{RESET}")


@agentes.command()
@click.option('--provider', '-p', help='Proveedor LLM')
@click.option('--apikey', '-k', help='API Key')
@click.option('--model', '-m', help='Modelo específico')
@click.pass_context
def config_global(ctx, provider, apikey, model):
    """
    Configura el LLM global compartido por todos los agentes

    Ejemplos:

    \b
      trus agentes config-global --provider openai
      trus agentes config-global -p zai -k TU_API_KEY
    """
    config = ctx.obj['config']

    # Si no hay parámetros, modo interactivo
    if not provider and not apikey and not model:
        print_header("⚙️ Configuración Global de LLM")

        # Seleccionar proveedor
        click.echo(f"{CYAN}Selecciona proveedor:{RESET}")
        for i, (key, info) in enumerate(PROVIDERS.items(), 1):
            click.echo(f"   {i}. {key} - {info['name']}")

        idx = click.prompt("\nOpción", type=int, default=1)
        provider = list(PROVIDERS.keys())[idx - 1]

        # Solicitar API key
        if provider != 'ollama':
            apikey = click.prompt(f"{CYAN}API Key para {PROVIDERS[provider]['name']}{RESET}",
                                  hide_input=True)

        # Modelo
        default_model = PROVIDERS[provider]['model']
        model = click.prompt(f"{CYAN}Modelo (default: {default_model}){RESET}",
                            default=default_model)

    # Aplicar configuración
    if provider:
        if provider not in PROVIDERS:
            click.echo(f"{RED}❌ Proveedor no válido: {provider}{RESET}")
            return
        config.global_provider = provider
        click.echo(f"{GREEN}✅ Proveedor: {provider}{RESET}")

    if apikey:
        config.global_api_key = apikey
        click.echo(f"{GREEN}✅ API Key configurada{RESET}")

    if model:
        config.global_model = model
        click.echo(f"{GREEN}✅ Modelo: {model}{RESET}")

    save_config(config)
    click.echo(f"\n{GREEN}✅ Configuración global guardada{RESET}")


@agentes.command()
@click.argument('agente', type=click.Choice(AGENTES))
@click.option('--provider', '-p', help='Proveedor LLM')
@click.option('--apikey', '-k', help='API Key específica del agente')
@click.option('--model', '-m', help='Modelo específico')
@click.option('--activo/--inactivo', default=True, help='Activar/desactivar agente')
@click.pass_context
def config_agente(ctx, agente, provider, apikey, model, activo):
    """
    Configura un agente específico con su propio LLM

    Si no especifica provider/apikey, usará la configuración global.

    Ejemplos:

    \b
      trus agentes config-agente bibliotecario --provider zai
      trus agentes config-agente bibliotecario -k API_KEY_PROPIA
      trus agentes config-agente investigador --inactivo
    """
    config = ctx.obj['config']
    agent_cfg = config.get_agent_config(agente)

    # Modo interactivo si no hay parámetros
    if not provider and not apikey and not model and activo:
        print_header(f"⚙️ Configurar Agente: {agente.capitalize()}")

        # Mostrar configuración actual
        current_provider = agent_cfg.proveedor or config.global_provider
        current_model = agent_cfg.modelo or config.global_model or PROVIDERS.get(current_provider, {}).get('model', '')
        has_own_key = bool(agent_cfg.api_key)

        click.echo(f"{CYAN}Proveedor actual: {current_provider}{RESET}")
        click.echo(f"{CYAN}Modelo actual: {current_model}{RESET}")
        click.echo(f"{CYAN}API Key propia: {'Sí' if has_own_key else 'No (usa global)'}{RESET}\n")

        # Preguntar qué cambiar
        if click.confirm(f"{CYAN}¿Cambiar proveedor?{RESET}"):
            click.echo(f"\n{GREEN}Proveedores disponibles:{RESET}")
            for key, info in PROVIDERS.items():
                click.echo(f"  {key}: {info['name']}")

            provider = click.prompt(f"{CYAN}Nuevo proveedor{RESET}", type=str)

        if click.confirm(f"{CYAN}¿Agregar API Key propia?{RESET}"):
            if provider != 'ollama':
                apikey = click.prompt(f"{CYAN}API Key para {agente}{RESET}", hide_input=True)
            else:
                click.echo(f"{YELLOW}ℹ️  Ollama no requiere API key{RESET}")

        if click.confirm(f"{CYAN}¿Cambiar modelo?{RESET}"):
            default = PROVIDERS.get(provider or current_provider, {}).get('model', '')
            model = click.prompt(f"{CYAN}Modelo{RESET}", default=default)

    # Aplicar cambios
    if provider:
        if provider not in PROVIDERS:
            click.echo(f"{RED}❌ Proveedor no válido: {provider}{RESET}")
            return
        agent_cfg.proveedor = provider

    if apikey:
        agent_cfg.api_key = apikey

    if model:
        agent_cfg.modelo = model

    agent_cfg.activo = activo

    # Guardar
    config.set_agent_config(agente, agent_cfg)
    save_config(config)

    # Resumen
    click.echo(f"\n{GREEN}✅ Configuración de {agente.capitalize()} guardada:{RESET}")
    click.echo(f"   Proveedor: {agent_cfg.proveedor or '(global)'}")
    click.echo(f"   Modelo: {agent_cfg.modelo or '(global)'}")
    click.echo(f"   API Key: {'Propia' if agent_cfg.api_key else '(global)'}")
    click.echo(f"   Estado: {'Activo' if agent_cfg.activo else 'Inactivo'}")


@agentes.command()
@click.option('--provider', '-p', help='Proveedor LLM')
@click.option('--apikey', '-k', help='API Key')
@click.option('--model', '-m', help='Modelo')
@click.pass_context
def config(ctx, provider, apikey, model):
    """
    Configura la API key global (atajo para config-global)

    Ejemplo: trus agentes config -p openai -k TU_API_KEY
    """
    # Delegar a config-global
    ctx.invoke(config_global, provider=provider, apikey=apikey, model=model)


# Alias para compatibilidad
@agentes.command(name='configurar')
@click.pass_context
def configurar(ctx):
    """Alias de 'config' para compatibilidad"""
    ctx.invoke(config_global)


# ═══════════════════════════════════════════════════════════════
# COMANDOS: RECORDAR (Indexar)
# ═══════════════════════════════════════════════════════════════

@cli.group()
def recordar():
    """
    💾 Indexa contenido en TrustGraph

    Comandos:

    \b
      archivo     - Indexa un archivo
      directorio  - Indexa un directorio
      proyecto    - Indexa el proyecto actual
    """
    pass


@recordar.command()
@click.argument('ruta', type=click.Path(exists=True))
@click.option('--categoria', '-c', default='documentacion')
@click.option('--etiquetas', '-t')
@click.pass_context
def archivo(ctx, ruta, categoria, etiquetas):
    """Indexa un archivo específico"""
    config = ctx.obj['config']

    if not check_connection(config.api_gateway):
        click.echo(f"{RED}❌ No hay conexión con TrustGraph{RESET}")
        return

    print_header(f"💾 Indexando: {Path(ruta).name}")

    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            contenido = f.read()

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
            data = response.json()
            click.echo(f"{GREEN}✅ Indexado correctamente{RESET}")
            click.echo(f"   Entidades: {data.get('entities', 0)}")
            click.echo(f"   Relaciones: {data.get('relations', 0)}")
        else:
            click.echo(f"{RED}❌ Error: {response.status_code}{RESET}")

    except Exception as e:
        click.echo(f"{RED}❌ Error: {e}{RESET}")


@recordar.command()
@click.argument('ruta', type=click.Path(exists=True, file_okay=False))
@click.option('--extensiones', '-e', default='.md,.txt,.py,.js,.ts')
@click.pass_context
def directorio(ctx, ruta, extensiones):
    """Indexa todos los archivos de un directorio"""
    config = ctx.obj['config']

    if not check_connection(config.api_gateway):
        click.echo(f"{RED}❌ No hay conexión con TrustGraph{RESET}")
        return

    print_header(f"📁 Indexando: {ruta}")

    archivos = []
    for ext in extensiones.split(','):
        archivos.extend(Path(ruta).rglob(f'*{ext}'))

    archivos = [a for a in archivos if 'node_modules' not in str(a)]

    click.echo(f"{CYAN}Encontrados {len(archivos)} archivos{RESET}\n")

    exitosos = 0
    for i, arch in enumerate(archivos, 1):
        click.echo(f"[{i}/{len(archivos)}] {arch.name}...", nl=False)
        try:
            with open(arch, 'r', encoding='utf-8') as f:
                contenido = f.read()

            response = requests.post(
                f"{config.api_gateway}/api/v1/documents/upload",
                json={'path': str(arch), 'content': contenido},
                timeout=60
            )

            if response.status_code == 200:
                click.echo(f" {GREEN}✓{RESET}")
                exitosos += 1
            else:
                click.echo(f" {RED}✗{RESET}")
        except:
            click.echo(f" {RED}✗{RESET}")

    click.echo(f"\n{GREEN}✅ Completado: {exitosos}/{len(archivos)}{RESET}")


@recordar.command()
@click.pass_context
def proyecto(ctx):
    """Indexa el proyecto actual"""
    ctx.invoke(directorio, ruta='.', extensiones='.md,.txt,.py,.js,.ts,.json,.yaml')


# ═══════════════════════════════════════════════════════════════
# COMANDO: QUERY
# ═══════════════════════════════════════════════════════════════

@cli.command()
@click.argument('pregunta', required=False)
@click.option('--interactivo', '-i', is_flag=True)
@click.pass_context
def query(ctx, pregunta, interactivo):
    """Consulta la memoria de TrustGraph"""
    config = ctx.obj['config']

    if not check_connection(config.api_gateway):
        click.echo(f"{RED}❌ No hay conexión con TrustGraph{RESET}")
        return

    if interactivo or not pregunta:
        print_header("🔍 Modo Interactivo")
        click.echo(f"{CYAN}Escribe 'salir' para terminar{RESET}\n")

        while True:
            pregunta = click.prompt(f"{BLUE}❓ Pregunta{RESET}")
            if pregunta.lower() in ['salir', 'quit', 'exit']:
                break
            _ejecutar_query(config, pregunta)
    else:
        _ejecutar_query(config, pregunta)


def _ejecutar_query(config: TrustGraphConfig, pregunta: str):
    """Ejecuta una consulta"""
    click.echo(f"{BLUE}🤔 Pensando...{RESET}\n")

    try:
        response = requests.post(
            f"{config.api_gateway}/api/v1/graphrag/query",
            json={'query': pregunta, 'context_core': 'documentation'},
            timeout=120
        )

        if response.status_code == 200:
            data = response.json()
            click.echo(f"{GREEN}📝 Respuesta:{RESET}\n")
            click.echo(data.get('response', 'Sin respuesta'))
        else:
            click.echo(f"{RED}❌ Error: {response.status_code}{RESET}")

    except Exception as e:
        click.echo(f"{RED}❌ Error: {e}{RESET}")


# ═══════════════════════════════════════════════════════════════
# COMANDO: LOGIN (legacy)
# ═══════════════════════════════════════════════════════════════

@cli.command()
@click.option('--host', '-h', default='localhost')
@click.option('--port', '-p', default=8080)
@click.pass_context
def login(ctx, host, port):
    """Configura la conexión con TrustGraph"""
    config = ctx.obj['config']

    config.host = host
    config.port = port
    config.api_gateway = f"http://{host}:{port}"

    save_config(config)

    click.echo(f"{GREEN}✅ Configuración guardada:{RESET}")
    click.echo(f"   Host: {host}")
    click.echo(f"   Puerto: {port}")
    click.echo(f"   API: {config.api_gateway}")


# ═══════════════════════════════════════════════════════════════
# COMANDO: STATUS (legacy)
# ═══════════════════════════════════════════════════════════════

@cli.command()
@click.pass_context
def status(ctx):
    """Muestra el estado general de TrustGraph"""
    config = ctx.obj['config']

    print_header("📊 Estado de TrustGraph")

    click.echo(f"{BOLD}Conexión:{RESET}")
    click.echo(f"   API: {config.api_gateway}")

    if check_connection(config.api_gateway):
        click.echo(f"   {GREEN}✅ Conectado{RESET}")
        try:
            r = requests.get(f"{config.api_gateway}/api/v1/health", timeout=5)
            data = r.json()
            click.echo(f"   Versión: {data.get('version', 'N/A')}")
        except:
            pass
    else:
        click.echo(f"   {RED}❌ Desconectado{RESET}")

    click.echo(f"\n{BOLD}Agentes:{RESET}")
    ctx.invoke(agentes.status)


# ═══════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    cli()
