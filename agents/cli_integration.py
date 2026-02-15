#!/usr/bin/env python3
"""
Integración de Agentes con TrustGraph CLI

Conecta los agentes Callímaco, Sócrates y Morpheo con la CLI `trus`.
Permite invocar a los agentes desde comandos de terminal.
"""

import os
import sys
import json
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

# Añadir el directorio padre al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.callimaco import CallimacoAgent, CallimacoState, ContentType
from agents.socrates import SocratesAgent, QueryType
from agents.morpheo import MorpheoAgent


# Colores para output
BLUE = '\033[36m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
RED = '\033[31m'
CYAN = '\033[35m'
BOLD = '\033[1m'
RESET = '\033[0m'


# Configuración - mismo archivo que usa la CLI trus
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

AGENTES = ['bibliotecario', 'investigador', 'nocturno']


def load_trus_config() -> Dict[str, Any]:
    """
    Carga la configuración de la CLI trus.
    Lee desde ~/.trustgraph/config.json
    """
    default_config = {
        "host": "localhost",
        "port": 8080,
        "api_gateway": "http://localhost:8080",
        "is_local": True,
        "auth_token": "",
        "global_provider": "openai",
        "global_api_key": "",
        "global_model": "",
        "agentes": {}
    }

    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                stored_config = json.load(f)
                default_config.update(stored_config)
        except (json.JSONDecodeError, IOError) as e:
            print(f"{YELLOW}⚠️  Advertencia: No se pudo leer config: {e}{RESET}")

    return default_config


def get_agent_config(agente: str) -> Dict[str, Any]:
    """
    Obtiene la configuración de un agente específico.
    Si no tiene configuración propia, usa la global.
    """
    config = load_trus_config()

    # Obtener config del agente o defaults
    agent_cfg = config.get('agentes', {}).get(agente, {})

    # Combinar con config global
    return {
        'proveedor': agent_cfg.get('proveedor') or config.get('global_provider', 'openai'),
        'api_key': agent_cfg.get('api_key') or config.get('global_api_key', ''),
        'modelo': agent_cfg.get('modelo') or config.get('global_model') or PROVIDERS.get(
            agent_cfg.get('proveedor') or config.get('global_provider', 'openai'), {}
        ).get('model', ''),
        'activo': agent_cfg.get('activo', True)
    }


class AgentCLI:
    """
    Interfaz de línea de comandos para los agentes de TrustGraph.

    Usa la MISMA configuración que la CLI trus principal:
    - ~/.trustgraph/config.json

    Soporta:
    - Configuración global (compartida por todos los agentes)
    - Configuración por agente (individual)

    Comandos disponibles:
    - trus agente bibliotecario indexar ...
    - trus agente investigador preguntar ...
    - trus agente nocturno ciclo ...
    """

    def __init__(self, api_gateway: str = None, agente: str = None):
        # Cargar configuración de trus
        self.config = load_trus_config()

        # Usar api_gateway proporcionado o el de la config
        self.api_gateway = api_gateway or self.config.get('api_gateway', 'http://localhost:8080')

        # Actualizar config con el api_gateway efectivo
        self.config['api_gateway'] = self.api_gateway

        # Agent específico si se proporciona
        self.agente = agente

        self.callimaco = None
        self.socrates = None
        self.morpheo = None

    def get_api_key(self, agente: str = None) -> str:
        """Obtiene la API key del agente o global"""
        agent_name = agente or self.agente or 'bibliotecario'
        cfg = get_agent_config(agent_name)
        return cfg.get('api_key', '')

    def get_provider(self, agente: str = None) -> str:
        """Obtiene el proveedor LLM del agente o global"""
        agent_name = agente or self.agente or 'bibliotecario'
        cfg = get_agent_config(agent_name)
        return cfg.get('proveedor', 'openai')

    def get_model(self, agente: str = None) -> str:
        """Obtiene el modelo del agente o global"""
        agent_name = agente or self.agente or 'bibliotecario'
        cfg = get_agent_config(agent_name)
        return cfg.get('modelo', '')

    def is_agent_active(self, agente: str) -> bool:
        """Verifica si un agente está activo"""
        cfg = get_agent_config(agente)
        return cfg.get('activo', True)

    def _init_callimaco(self):
        """Inicializa el agente Callímaco"""
        if self.callimaco is None:
            agent_cfg = get_agent_config('bibliotecario')
            self.callimaco = CallimacoAgent(
                api_gateway=self.api_gateway,
                llm_config={
                    'provider': agent_cfg['proveedor'],
                    'api_key': agent_cfg['api_key'],
                    'model': agent_cfg['modelo']
                }
            )
        return self.callimaco

    def _init_socrates(self):
        """Inicializa el agente Sócrates"""
        if self.socrates is None:
            agent_cfg = get_agent_config('investigador')
            self.socrates = SocratesAgent(
                api_gateway=self.api_gateway,
                llm_config={
                    'provider': agent_cfg['proveedor'],
                    'api_key': agent_cfg['api_key'],
                    'model': agent_cfg['modelo']
                }
            )
        return self.socrates

    def _init_morpheo(self):
        """Inicializa el agente Morpheo"""
        if self.morpheo is None:
            agent_cfg = get_agent_config('nocturno')
            self.morpheo = MorpheoAgent(
                api_gateway=self.api_gateway,
                llm_config={
                    'provider': agent_cfg['proveedor'],
                    'api_key': agent_cfg['api_key'],
                    'model': agent_cfg['modelo']
                }
            )
        return self.morpheo

    # ═══════════════════════════════════════════════════════════════
    # COMANDOS DEL BIBLIOTECARIO (Callímaco)
    # ═══════════════════════════════════════════════════════════════

    async def bibliotecario_indexar(
        self,
        content: str,
        content_type: str = "documento",
        source: str = "",
        etiquetas: Optional[List[str]] = None,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Indexa contenido usando al agente Callímaco (Καλλίμαχος)

        El bibliotecario griego organiza y estructura la información,
        decidiendo inteligentemente qué va a Cassandra (grafo) y qué a Qdrant (vectores).

        Args:
            content: Contenido a indexar
            content_type: Tipo de contenido (documento, conversacion, codigo, etc.)
            source: Fuente del contenido (archivo, URL, etc.)
            etiquetas: Etiquetas adicionales
            verbose: Mostrar detalles del procesamiento

        Returns:
            Resultado de la indexación con metadatos generados
        """
        agent = self._init_callimaco()

        if verbose:
            print(f"{CYAN}📚 Invocando a Callímaco, el bibliotecario de Alejandría...{RESET}")
            print(f"{BLUE}   Tipo de contenido: {content_type}{RESET}")
            print(f"{BLUE}   Fuente: {source or 'No especificada'}{RESET}")
            print(f"{BLUE}   Tamaño: {len(content)} caracteres{RESET}")
            print()

        # Mapear string a enum
        try:
            ct = ContentType(content_type.lower())
        except ValueError:
            ct = ContentType.DOCUMENTO

        resultado = await agent.indexar(
            content=content,
            content_type=ct,
            source=source,
            metadata={"etiquetas": etiquetas or []}
        )

        if verbose:
            print(f"{GREEN}✅ Indexación completada{RESET}")
            print(f"{CYAN}   Hash de contenido: {resultado.get('content_hash', 'N/A')}{RESET}")
            print(f"{CYAN}   Entidades extraídas: {resultado.get('entities_extracted', 0)}{RESET}")
            print(f"{CYAN}   Relaciones extraídas: {resultado.get('relations_extracted', 0)}{RESET}")

            plan = resultado.get('storage_plan', {})
            print(f"{CYAN}   Destino: {plan.get('destination', 'N/A')}{RESET}")
            print(f"{CYAN}   Ops Cassandra: {plan.get('cassandra_ops', 0)}{RESET}")
            print(f"{CYAN}   Ops Qdrant: {plan.get('qdrant_ops', 0)}{RESET}")

            tags = resultado.get('semantic_tags', {})
            if tags:
                print(f"{CYAN}   Categoría: {tags.get('categoria_primaria', 'N/A')}{RESET}")
                print(f"{CYAN}   Temas: {', '.join(tags.get('temas', [])[:5])}{RESET}")

        return resultado

    async def bibliotecario_indexar_archivo(
        self,
        file_path: str,
        content_type: Optional[str] = None,
        etiquetas: Optional[List[str]] = None,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """Indexa un archivo usando Callímaco"""
        path = Path(file_path)

        if not path.exists():
            return {"error": f"Archivo no encontrado: {file_path}"}

        # Detectar tipo de contenido por extensión
        ext = path.suffix.lower()
        type_mapping = {
            '.py': 'codigo',
            '.js': 'codigo',
            '.ts': 'codigo',
            '.java': 'codigo',
            '.md': 'documento',
            '.txt': 'documento',
            '.json': 'documento',
            '.yaml': 'documento',
            '.yml': 'documento',
        }

        detected_type = type_mapping.get(ext, content_type or 'documento')

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {"error": f"Error leyendo archivo: {str(e)}"}

        return await self.bibliotecario_indexar(
            content=content,
            content_type=detected_type,
            source=str(path.absolute()),
            etiquetas=etiquetas,
            verbose=verbose
        )

    async def bibliotecario_indexar_directorio(
        self,
        dir_path: str,
        extensiones: List[str] = None,
        recursive: bool = True,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """Indexa todos los archivos de un directorio"""
        path = Path(dir_path)

        if not path.exists() or not path.is_dir():
            return {"error": f"Directorio no encontrado: {dir_path}"}

        extensiones = extensiones or ['.md', '.txt', '.py', '.js', '.ts']
        archivos = []

        if recursive:
            for ext in extensiones:
                archivos.extend(path.rglob(f'*{ext}'))
        else:
            for ext in extensiones:
                archivos.extend(path.glob(f'*{ext}'))

        # Excluir directorios comunes
        excluir = ['node_modules', '.git', '__pycache__', '.venv', 'venv', '.env']
        archivos = [a for a in archivos if not any(e in str(a) for e in excluir)]

        if verbose:
            print(f"{CYAN}📁 Indexando directorio: {dir_path}{RESET}")
            print(f"{BLUE}   Archivos encontrados: {len(archivos)}{RESET}")
            print()

        resultados = []
        exitosos = 0

        for i, archivo in enumerate(archivos, 1):
            if verbose:
                print(f"[{i}/{len(archivos)}] {archivo.name}...", end=' ', flush=True)

            resultado = await self.bibliotecario_indexar_archivo(
                file_path=str(archivo),
                verbose=False
            )

            if 'error' not in resultado:
                exitosos += 1
                if verbose:
                    print(f"{GREEN}✓{RESET}")
            else:
                if verbose:
                    print(f"{RED}✗{RESET}")

            resultados.append({
                "archivo": str(archivo),
                "exitoso": 'error' not in resultado,
                "hash": resultado.get('content_hash', '')
            })

        return {
            "total": len(archivos),
            "exitosos": exitosos,
            "fallidos": len(archivos) - exitosos,
            "archivos": resultados
        }

    # ═══════════════════════════════════════════════════════════════
    # COMANDOS DEL INVESTIGADOR (Sócrates)
    # ═══════════════════════════════════════════════════════════════

    async def investigador_preguntar(
        self,
        query: str,
        contexto: Optional[Dict[str, Any]] = None,
        modo: Literal["rapido", "profundo"] = "profundo",
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Realiza una investigación usando al agente Sócrates (Σωκράτης)

        El filósofo descompone la pregunta en sub-consultas, busca en
        múltiples fuentes y devuelve punteros precisos al conocimiento.

        Args:
            query: Pregunta del usuario
            contexto: Contexto adicional (historial, preferencias)
            modo: 'rapido' para respuestas simples, 'profundo' para análisis completo
            verbose: Mostrar detalles del proceso de investigación

        Returns:
            Respuesta sintetizada con punteros a fuentes
        """
        agent = self._init_socrates()

        if verbose:
            print(f"{CYAN}🔍 Invocando a Sócrates, el investigador dialéctico...{RESET}")
            print(f"{BLUE}   Pregunta: {query}{RESET}")
            print(f"{BLUE}   Modo: {modo}{RESET}")
            print()

        resultado = await agent.investigar(
            query=query,
            context=contexto or {}
        )

        if verbose:
            estrategia = resultado.get('estrategia', {})
            print(f"{GREEN}📊 Análisis completado{RESET}")
            print(f"{CYAN}   Tipo de query: {estrategia.get('tipo_query', 'N/A')}{RESET}")
            print(f"{CYAN}   Complejidad: {estrategia.get('complejidad', 0):.2f}{RESET}")
            print(f"{CYAN}   Sub-consultas: {estrategia.get('subconsultas', 0)}{RESET}")
            print(f"{CYAN}   Confianza: {resultado.get('confianza', 0):.2%}{RESET}")
            print()
            print(f"{BOLD}📝 Respuesta:{RESET}")
            print(resultado.get('respuesta', 'Sin respuesta'))
            print()
            print(f"{BOLD}📍 Punteros seleccionados:{RESET}")
            for ptr in resultado.get('punteros', [])[:5]:
                print(f"   • [{ptr.get('relevancia', 0):.0%}] {ptr.get('snippet', 'N/A')[:60]}...")

        return resultado

    async def investigador_preguntar_interactivo(self):
        """Modo interactivo de investigación"""
        print(f"{BOLD}{BLUE}╔══════════════════════════════════════════════════════════════╗{RESET}")
        print(f"{BOLD}{BLUE}║{RESET}  🔍 Sócrates - Modo Interactivo                          {BLUE}║{RESET}")
        print(f"{BOLD}{BLUE}╚══════════════════════════════════════════════════════════════╝{RESET}")
        print(f"{CYAN}Escribe tus preguntas (o 'salir' para terminar, 'help' para ayuda){RESET}\n")

        historial = []

        while True:
            try:
                query = input(f"{BLUE}❓ Pregunta{RESET}: ").strip()

                if not query:
                    continue

                if query.lower() in ['salir', 'exit', 'quit', 'q']:
                    print(f"{GREEN}👋 ¡Hasta luego!{RESET}")
                    break

                if query.lower() == 'help':
                    print(f"\n{BOLD}Comandos disponibles:{RESET}")
                    print(f"  {CYAN}salir, exit, q{RESET} - Terminar sesión")
                    print(f"  {CYAN}help{RESET} - Mostrar esta ayuda")
                    print(f"  {CYAN}historial{RESET} - Ver preguntas previas")
                    print(f"  {CYAN}clear{RESET} - Limpiar historial\n")
                    continue

                if query.lower() == 'historial':
                    print(f"\n{BOLD}Historial de preguntas:{RESET}")
                    for i, h in enumerate(historial[-10:], 1):
                        print(f"  {i}. {h}")
                    print()
                    continue

                if query.lower() == 'clear':
                    historial = []
                    print(f"{YELLOW}Historial limpiado{RESET}\n")
                    continue

                # Ejecutar investigación
                print(f"{BLUE}🤔 Pensando...{RESET}\n")

                resultado = await self.investigador_preguntar(
                    query=query,
                    contexto={"historial": historial[-5:]},
                    verbose=False
                )

                print(f"{GREEN}{BOLD}📝 Respuesta:{RESET}\n")
                print(resultado.get('respuesta', 'Sin respuesta'))

                confianza = resultado.get('confianza', 0)
                bar_length = 20
                filled = int(confianza * bar_length)
                bar = "█" * filled + "░" * (bar_length - filled)
                print(f"\n{CYAN}📊 Confianza: [{bar}] {confianza:.1%}{RESET}")

                if resultado.get('punteros'):
                    print(f"\n{CYAN}📍 Fuentes:{RESET}")
                    for ptr in resultado['punteros'][:3]:
                        print(f"   • {ptr.get('snippet', 'N/A')[:50]}...")

                print()
                historial.append(query)

            except KeyboardInterrupt:
                print(f"\n{GREEN}👋 ¡Hasta luego!{RESET}")
                break
            except EOFError:
                break

    # ═══════════════════════════════════════════════════════════════
    # COMANDOS DEL NOCTURNO (Morpheo)
    # ═══════════════════════════════════════════════════════════════

    async def nocturno_ciclo(
        self,
        intensidad: Literal["ligero", "normal", "profundo"] = "normal",
        duracion_maxima: int = 360,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Ejecuta un ciclo de mantenimiento nocturno usando a Morpheo (Μορφεύς)

        El dios de los sueños repara, optimiza y reorganiza la memoria
durante horas de baja actividad.

        Args:
            intensidad: Nivel de optimización (ligero/normal/profundo)
            duracion_maxima: Minutos máximos de ejecución
            verbose: Mostrar progreso detallado

        Returns:
            Reporte del ciclo de mantenimiento
        """
        agent = self._init_morpheo()

        if verbose:
            print(f"{BOLD}{BLUE}╔══════════════════════════════════════════════════════════════╗{RESET}")
            print(f"{BOLD}{BLUE}║{RESET}  🌙 Morpheo - Ciclo de Sueño                             {BLUE}║{RESET}")
            print(f"{BOLD}{BLUE}╚══════════════════════════════════════════════════════════════╝{RESET}")
            print(f"{CYAN}   Intensidad: {intensidad}{RESET}")
            print(f"{CYAN}   Duración máxima: {duracion_maxima} minutos{RESET}")
            print(f"{CYAN}   Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
            print()

        resultado = await agent.ejecutar_ciclo(
            max_duration_minutes=duracion_maxima,
            intensity=intensidad
        )

        if verbose:
            print(f"\n{BOLD}{GREEN}✅ Ciclo completado{RESET}")
            print(f"{CYAN}   Reparaciones: {resultado.get('reparaciones_hechas', 0)}{RESET}")
            print(f"{CYAN}   Optimizaciones: {resultado.get('optimizaciones_hechas', 0)}{RESET}")

            reporte = resultado.get('reporte', {})
            if reporte:
                print(f"{CYAN}   Issues detectados: {reporte.get('issues_detectados', 0)}{RESET}")
                print(f"{CYAN}   Duración real: {reporte.get('duracion_minutos', 0):.1f} minutos{RESET}")

            errores = resultado.get('errores', [])
            if errores:
                print(f"\n{YELLOW}⚠️  Errores ({len(errores)}):{RESET}")
                for e in errores[:5]:
                    print(f"   • {e}")

        return resultado

    async def nocturno_programar(
        self,
        hora_inicio: str = "02:00",
        frecuencia: Literal["diario", "semanal", "mensual"] = "semanal",
        intensidad: str = "normal"
    ) -> Dict[str, Any]:
        """
        Programa ciclos de mantenimiento nocturno

        En implementación real, esto configuraría un cron job
        o el servicio de scheduling del sistema.
        """
        # Crear script de scheduling
        script_content = f"""#!/bin/bash
# Morpheo Scheduled Cycle - Generado {datetime.now().isoformat()}
# Frecuencia: {frecuencia}, Hora: {hora_inicio}, Intensidad: {intensidad}

export TRUSTGRAPH_API={self.api_gateway}

cd {Path(__file__).parent.parent}
python -m agents.cli_integration nocturno-ciclo --intensidad {intensidad} --duracion 360 --verbose
"""

        script_path = Path.home() / '.trustgraph' / 'morpheo_cron.sh'
        script_path.parent.mkdir(exist_ok=True)

        with open(script_path, 'w') as f:
            f.write(script_content)

        script_path.chmod(0o755)

        # Mostrar instrucciones de cron
        cron_line = f"0 {hora_inicio.split(':')[0]} * * * {script_path}"

        return {
            "programado": True,
            "frecuencia": frecuencia,
            "hora": hora_inicio,
            "intensidad": intensidad,
            "script": str(script_path),
            "instrucciones": f"Añade esta línea a tu crontab: {cron_line}"
        }

    # ═══════════════════════════════════════════════════════════════
    # MÉTODOS DE UTILIDAD
    # ═══════════════════════════════════════════════════════════════

    def verificar_estado_agentes(self) -> Dict[str, Any]:
        """Verifica el estado de los agentes"""
        return {
            "callimaco": {
                "inicializado": self.callimaco is not None,
                "descripcion": "Καλλίμαχος - Bibliotecario de Alejandría"
            },
            "socrates": {
                "inicializado": self.socrates is not None,
                "descripcion": "Σωκράτης - Investigador Dialéctico"
            },
            "morpheo": {
                "inicializado": self.morpheo is not None,
                "descripcion": "Μορφεύς - Guardián del Sueño"
            }
        }


# ═══════════════════════════════════════════════════════════════
# CLI ENTRY POINTS
# ═══════════════════════════════════════════════════════════════

async def main_bibliotecario(args: List[str]):
    """Entry point para comandos del bibliotecario"""
    cli = AgentCLI()

    if len(args) < 1:
        print("Uso: trus agente bibliotecario <comando> [opciones]")
        print("\nComandos:")
        print("  indexar <archivo>     Indexa un archivo")
        print("  indexar-dir <directorio>  Indexa un directorio completo")
        return

    comando = args[0]

    if comando == "indexar" and len(args) >= 2:
        resultado = await cli.bibliotecario_indexar_archivo(
            file_path=args[1],
            verbose=True
        )
        if 'error' in resultado:
            print(f"{RED}❌ {resultado['error']}{RESET}")

    elif comando == "indexar-dir" and len(args) >= 2:
        resultado = await cli.bibliotecario_indexar_directorio(
            dir_path=args[1],
            verbose=True
        )
        print(f"\n{GREEN}✅ Indexación completada:{RESET}")
        print(f"   Total: {resultado.get('total', 0)}")
        print(f"   Exitosos: {resultado.get('exitosos', 0)}")
        print(f"   Fallidos: {resultado.get('fallidos', 0)}")

    else:
        print(f"{RED}❌ Comando no reconocido: {comando}{RESET}")


async def main_investigador(args: List[str]):
    """Entry point para comandos del investigador"""
    cli = AgentCLI()

    if len(args) < 1:
        print("Uso: trus agente investigador <comando> [opciones]")
        print("\nComandos:")
        print("  preguntar 'texto'     Hacer una pregunta")
        print("  interactivo           Modo interactivo")
        return

    comando = args[0]

    if comando == "preguntar" and len(args) >= 2:
        query = " ".join(args[1:])
        resultado = await cli.investigador_preguntar(
            query=query,
            verbose=True
        )

    elif comando == "interactivo":
        await cli.investigador_preguntar_interactivo()

    else:
        print(f"{RED}❌ Comando no reconocido: {comando}{RESET}")


async def main_nocturno(args: List[str]):
    """Entry point para comandos del agente nocturno"""
    cli = AgentCLI()

    if len(args) < 1:
        print("Uso: trus agente nocturno <comando> [opciones]")
        print("\nComandos:")
        print("  ciclo [--intensidad ligero|normal|profundo] [--duracion N]")
        print("  programar [--hora HH:MM] [--frecuencia diario|semanal|mensual]")
        return

    comando = args[0]

    if comando == "ciclo":
        # Parsear argumentos
        intensidad = "normal"
        duracion = 360

        i = 1
        while i < len(args):
            if args[i] == "--intensidad" and i + 1 < len(args):
                intensidad = args[i + 1]
                i += 2
            elif args[i] == "--duracion" and i + 1 < len(args):
                duracion = int(args[i + 1])
                i += 2
            else:
                i += 1

        resultado = await cli.nocturno_ciclo(
            intensidad=intensidad,
            duracion_maxima=duracion,
            verbose=True
        )

    elif comando == "programar":
        hora = "02:00"
        frecuencia = "semanal"
        intensidad = "normal"

        i = 1
        while i < len(args):
            if args[i] == "--hora" and i + 1 < len(args):
                hora = args[i + 1]
                i += 2
            elif args[i] == "--frecuencia" and i + 1 < len(args):
                frecuencia = args[i + 1]
                i += 2
            elif args[i] == "--intensidad" and i + 1 < len(args):
                intensidad = args[i + 1]
                i += 2
            else:
                i += 1

        resultado = await cli.nocturno_programar(
            hora_inicio=hora,
            frecuencia=frecuencia,
            intensidad=intensidad
        )

        print(f"{GREEN}✅ Ciclo nocturno programado{RESET}")
        print(f"   Frecuencia: {resultado['frecuencia']}")
        print(f"   Hora: {resultado['hora']}")
        print(f"   Intensidad: {resultado['intensidad']}")
        print(f"\n{CYAN}{resultado['instrucciones']}{RESET}")

    else:
        print(f"{RED}❌ Comando no reconocido: {comando}{RESET}")


async def main():
    """Entry point principal"""
    import sys

    if len(sys.argv) < 2:
        print("TrustGraph Agents CLI")
        print("\nUso: python -m agents.cli_integration <agente> <comando>")
        print("\nAgentes disponibles:")
        print("  bibliotecario    Callímaco (Καλλίμαχος) - Indexación y organización")
        print("  investigador     Sócrates (Σωκράτης) - Búsqueda y síntesis")
        print("  nocturno         Morpheo (Μορφεύς) - Mantenimiento nocturno")
        print("\nEjemplos:")
        print("  python -m agents.cli_integration bibliotecario indexar doc.md")
        print("  python -m agents.cli_integration investigador interactivo")
        print("  python -m agents.cli_integration nocturno ciclo --intensidad profundo")
        return

    agente = sys.argv[1]
    args = sys.argv[2:]

    if agente == "bibliotecario":
        await main_bibliotecario(args)
    elif agente == "investigador":
        await main_investigador(args)
    elif agente == "nocturno":
        await main_nocturno(args)
    else:
        print(f"Agente no reconocido: {agente}")
        print("Agentes disponibles: bibliotecario, investigador, nocturno")


if __name__ == "__main__":
    asyncio.run(main())
