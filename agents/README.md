# 🤖 TrustGraph Agents

**Language: [Español](./README.md) | [English](./docs/agents/README.en.md)**

> 📖 **Documentación completa**: [docs/agents/](./docs/agents/)

Sistema multi-agente inteligente para TrustGraph basado en LangGraph.

---

## Los Tres Guardianes del Conocimiento

### 📚 Callímaco (Καλλίμαχος) - El Bibliotecario de Alejandría

> *"Organizo para que el conocimiento perdure milenios"*

**Responsabilidad**: Indexación y organización estructurada del conocimiento.

Callímaco es el agente encargado de recibir cualquier tipo de contenido (documentos, conversaciones, código, imágenes) y decidir inteligentemente:

- **Qué va a Cassandra (Grafo)**: Entidades, relaciones, estructura
- **Qué va a Qdrant (Vectores)**: Contenido semántico, embeddings
- **Cómo se etiqueta**: Taxonomía jerárquica, metadatos enriquecidos
- **Validación de calidad**: Completitud, consistencia, no-duplicación

**Flujo de Trabajo**:
```
CLASIFICAR → EXTRAER → ETIQUETAR → PLANIFICAR → VALIDAR → ALMACENAR
```

**Uso desde CLI**:
```bash
# Indexar un archivo
trus agente bibliotecario indexar documento.md --tipo documento

# Indexar directorio completo
trus agente bibliotecario indexar-dir ./docs --extensiones .md,.py
```

---

### 🔍 Sócrates (Σωκράτης) - El Investigador Dialéctico

> *"Solo sé que no sé nada, pero sé exactamente dónde buscar"*

**Responsabilidad**: Búsqueda avanzada y síntesis de respuestas.

Sócrates recibe preguntas complejas y aplica el método dialéctico:

1. **Maieutica (μαιευτική)**: Extrae la intención real del usuario
2. **Diairesis (διαίρεσις)**: Divide la query en sub-consultas atómicas
3. **Synagogé (συναγωγή)**: Recolecta punteros de múltiples fuentes
4. **Anakrisis (ἀνάκρισις)**: Examina y selecciona los mejores punteros
5. **Synthesis (σύνθεσις)**: Sintetiza respuesta coherente

**Estrategias de Búsqueda**:
- `vector_puro`: Similitud semántica directa
- `grafo_puro`: Navegación de entidades y relaciones
- `grafo_rag`: GraphRAG completo
- `hibrido`: Combinación vector + grafo
- `entidad_primero`: Buscar entidad luego expandir

**Uso desde CLI**:
```bash
# Pregunta simple
trus agente investigador preguntar "¿Qué es TrustGraph?"

# Modo interactivo
trus agente investigador preguntar -i

# Búsqueda rápida vs profunda
trus agente investigador preguntar "arquitectura" --modo rapido
```

---

### 🌙 Morpheo (Μορφεύς) - El Guardián del Sueño

> *"En los sueños reparo lo que el día desgasta"*

**Responsabilidad**: Mantenimiento nocturno, optimización y reparación.

Morpheo ejecuta durante horas de baja actividad para:

- **Reparar**: Duplicados, huérfanos, corruptos, obsoletos
- **Optimizar**: Reindexar, consolidar, comprimir, enriquecer
- **Defragmentar**: Reorganizar almacenamiento para eficiencia
- **Consolidar**: Fusionar chunks relacionados

**Ciclo Nocturno (Hypnos)**:
```
ESCANEAR → ANALIZAR → PLANIFICAR → REPARAR → OPTIMIZAR → REPORTAR
```

**Niveles de Intensidad**:
- `ligero`: Reindexación básica (1-2 horas)
- `normal`: Reparaciones + consolidación (3-6 horas)
- `profundo`: Todo + análisis completo (6-12 horas)

**Uso desde CLI**:
```bash
# Ejecutar ciclo manualmente
trus agente nocturno ciclo --intensidad normal --duracion 360

# Programar ciclos automáticos
trus agente nocturno programar --hora 02:00 --frecuencia semanal
```

---

## Estructura CLI Reorganizada

### 🐳 Infra (Docker e Infraestructura)

```bash
trus infra start          # Inicia servicios Docker
trus infra stop          # Detiene servicios
trus infra restart       # Reinicia servicios
trus infra status        # Estado de servicios
trus infra logs          # Ver logs
trus infra setup         # Configura .env
trus infra health        # Health check
```

### 🤖 Agentes (Configuración de LLM)

```bash
# Ver configuración
trus agentes show         # Muestra configuración de todos
trus agentes status      # Estado de agentes

# Configuración global (compartida por todos)
trus agentes config-global --provider openai
trus agentes config-global -p zai -k TU_API_KEY

# Configuración por agente (individual)
trus agentes config-agente bibliotecario --provider zai
trus agentes config-agente investigador -k API_KEY_PROPIA
trus agentes config-agente nocturno --inactivo
```

---

## Configuración de Agentes

### Configuración Global

Todos los agentes pueden compartir una configuración común:

```bash
trus agentes config-global -p openai -k sk-... -m gpt-4o
```

### Configuración por Agente

Cada agente puede tener su propio proveedor y API key:

```bash
# Bibliotecario con Z.AI
trus agentes config-agente bibliotecario -p zai -k API_KEY_ZAI

# Investigador con OpenAI
trus agentes config-agente investigador -p openai -k API_KEY_OPENAI

# Nocturno con Anthropic
trus agentes config-agente nocturno -p anthropic -k API_KEY_ANTHROPIC
```

### Jerarquía de Configuración

1. **Configuración del agente** (más específica)
2. **Configuración global** (fallback)
3. **Valores por defecto** (último recurso)

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                     LangGraph Engine                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐    │
│  │   Estados   │  │    Nodos    │  │  Condicionales  │    │
│  │  (Dataclass)│  │ (Funciones) │  │   (Rutas)       │    │
│  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘    │
│         │                │                   │             │
│         └────────────────┴───────────────────┘             │
│                          │                                 │
│                    ┌─────┴─────┐                          │
│                    │  Graph    │  ← Flujo de trabajo     │
│                    │ Compiled  │     definido             │
│                    └─────┬─────┘                          │
└──────────────────────────┼────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │ Callímaco  │  │  Sócrates  │  │  Morpheo   │
    │  (Index)   │  │  (Search)  │  │ (Maintain) │
    └─────┬──────┘  └─────┬──────┘  └─────┬──────┘
          │               │               │
          └───────────────┼───────────────┘
                          ▼
              ┌─────────────────────┐
              │  TrustGraph API      │
              │   localhost:8080    │
              └─────────────────────┘
```

---

## Instalación

```bash
# Instalar dependencias
pip install -r agents/requirements.txt

# O con el proyecto completo
pip install -e .
```

---

## Uso Programático

```python
import asyncio
from agents import CallimacoAgent, SocratesAgent, MorpheoAgent
from agents.callimaco import ContentType

async def flujo_completo():
    # 1. Callímaco indexa contenido
    callimaco = CallimacoAgent(
        api_gateway="http://localhost:8080",
        llm_config={
            "provider": "openai",
            "api_key": "sk-...",
            "model": "gpt-4o"
        }
    )

    with open("doc.md") as f:
        resultado_index = await callimaco.indexar(
            content=f.read(),
            content_type=ContentType.DOCUMENTO,
            source="doc.md"
        )

    print(f"Indexado: {resultado_index['entities_extracted']} entidades")

    # 2. Sócrates investiga
    socrates = SocratesAgent(
        api_gateway="http://localhost:8080",
        llm_config={"provider": "anthropic", "api_key": "sk-..."}
    )

    resultado_busqueda = await socrates.investigar(
        query="¿Qué entidades fueron creadas?"
    )

    print(f"Respuesta: {resultado_busqueda['respuesta']}")

    # 3. Morpheo optimiza
    morpheo = MorpheoAgent(
        api_gateway="http://localhost:8080",
        llm_config={"provider": "openai", "api_key": "sk-..."}
    )

    resultado_mantenimiento = await morpheo.ejecutar_ciclo(
        max_duration_minutes=360,
        intensity="normal"
    )

    print(f"Reparaciones: {resultado_mantenimiento['reparaciones_hechas']}")

asyncio.run(flujo_completo())
```

---

## Referencia de Comandos

### CLI Principal (trus)

| Comando | Descripción |
|---------|-------------|
| `trus infra *` | Gestión de Docker |
| `trus agentes *` | Configuración de agentes |
| `trus recordar archivo <ruta>` | Indexa archivo |
| `trus recordar directorio <ruta>` | Indexa directorio |
| `trus query "texto"` | Consulta memoria |
| `trus status` | Estado general |

### Infra

| Comando | Descripción |
|---------|-------------|
| `trus infra start` | Inicia Docker |
| `trus infra stop` | Detiene Docker |
| `trus infra restart` | Reinicia Docker |
| `trus infra status` | Estado Docker |
| `trus infra logs` | Ver logs |
| `trus infra health` | Health check |

### Agentes

| Comando | Descripción |
|---------|-------------|
| `trus agentes show` | Ver configuración |
| `trus agentes status` | Estado agentes |
| `trus agentes config-global` | Config global LLM |
| `trus agentes config-agente <agente>` | Config agente específico |

---

## Proveedores Soportados

| Proveedor | Modelo por defecto | Variable de API Key |
|-----------|-------------------|---------------------|
| `openai` | gpt-4o | OPENAI_API_KEY |
| `anthropic` | claude-3-5-sonnet | ANTHROPIC_API_KEY |
| `zai` | glm-5 | ZAI_API_KEY |
| `kimi` | kimi-k2 | KIMI_API_KEY |
| `minimax` | MiniMax-M2.5 | MINIMAX_API_KEY |
| `ollama` | llama3.1 | (local) |

---

## Licencia

MIT License - TrustGraph Team
