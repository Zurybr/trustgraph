# 🤖 TrustGraph Agents - Resumen Ejecutivo

## ¿Qué se ha creado?

Un sistema **multi-agente inteligente** basado en **LangGraph** que transforma TrustGraph en un sistema de gestión del conocimiento autónomo y sofisticado.

---

## CLI Reorganizada

### 🐳 Infra (Docker)

```bash
trus infra start          # Inicia servicios Docker
trus infra stop           # Detiene servicios
trus infra restart        # Reinicia servicios
trus infra status         # Estado de servicios
trus infra logs           # Ver logs
trus infra setup         # Configura .env
trus infra health        # Health check
```

### 🤖 Agentes (Config LLM)

```bash
# Ver configuración
trus agentes show
trus agentes status

# Config global (compartida)
trus agentes config-global -p openai -k TU_API_KEY

# Config por agente (individual)
trus agentes config-agente bibliotecario -p zai
trus agentes config-agente investigador -k API_KEY_PROPIA
trus agentes config-agente nocturno --inactivo
```

---

## Los Tres Agentes

### 1️⃣ 📚 Callímaco (Καλλίμαχος) - El Bibliotecario

**Propósito**: Organizar y estructurar todo el conocimiento que entra a TrustGraph.

**Capacidades**:
- ✅ Clasifica automáticamente el tipo de contenido (documento, código, conversación, etc.)
- ✅ Extrae entidades y relaciones usando NLP
- ✅ Decide inteligentemente qué va a Cassandra (grafo) vs Qdrant (vectores)
- ✅ Genera etiquetas semánticas jerárquicas "nivel dios"
- ✅ Valida calidad antes de almacenar
- ✅ Maneja reintentos y errores gracefully

**Flujo**: `Clasificar → Extraer → Etiquetar → Planificar → Validar → Almacenar`

**Uso**:
```bash
trus agente bibliotecario indexar documento.md
trus agente bibliotecario indexar-dir ./docs --extensiones .md,.py
```

---

### 2️⃣ 🔍 Sócrates (Σωκράτης) - El Investigador

**Propósito**: Responder preguntas complejas descomponiéndolas y buscando estratégicamente.

**Capacidades**:
- ✅ Extrae la intención REAL del usuario (método maieutico)
- ✅ Divide queries complejas en sub-consultas atómicas
- ✅ Elige estrategia óptima: vector, grafo, híbrido, o entidad-primero
- ✅ Devuelve **punteros precisos** (no contenido completo) para eficiencia
- ✅ Sintetiza respuestas coherentes de múltiples fuentes
- ✅ Reporta confianza y fuentes utilizadas

**Flujo**: `Maieutica → Diairesis → Synagoge → Anakrisis → Synthesis`

**Uso**:
```bash
trus agente investigador preguntar "¿Qué es TrustGraph?"
trus agente investigador preguntar -i  # Modo interactivo
```

---

### 3️⃣ 🌙 Morpheo (Μορφεύς) - El Guardián Nocturno

**Propósito**: Mantener la salud del sistema durante horas de baja actividad.

**Capacidades**:
- ✅ Detecta duplicados, huérfanos, corruptos, obsoletos
- ✅ Repara automáticamente con rollback si falla
- ✅ Optimiza embeddings y reindexa contenido
- ✅ Consolidada chunks fragmentados
- ✅ Genera reportes detallados del ciclo
- ✅ Programable para ejecución automática

**Flujo**: `Escanear → Analizar → Planificar → Reparar → Optimizar → Reportar`

**Uso**:
```bash
trus agente nocturno ciclo --intensidad normal
trus agente nocturno programar --hora 02:00 --frecuencia semanal
```

---

## Arquitectura Técnica

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
              │  TrustGraph API     │
              │   localhost:8080    │
              └─────────────────────┘
```

---

## Archivos Creados

| Archivo | Líneas | Descripción |
|---------|--------|-------------|
| `agents/__init__.py` | 25 | Inicialización del módulo |
| `agents/callimaco.py` | 850 | Bibliotecario - indexación |
| `agents/socrates.py` | 750 | Investigador - búsqueda |
| `agents/morpheo.py` | 700 | Nocturno - mantenimiento |
| `agents/cli_integration.py` | 650 | Integración con CLI |
| `agents/requirements.txt` | 20 | Dependencias |
| `agents/README.md` | 400 | Documentación completa |
| `agents/ARCHITECTURE.md` | 450 | Diagramas y arquitectura |
| `cli/trus.py` (actualizado) | +300 | Nuevos comandos CLI |
| `Makefile` (actualizado) | +100 | Comandos make para agentes |

**Total**: ~4,000 líneas de código Python de producción

---

## Comandos CLI Disponibles

### Bibliotecario (Callímaco)

```bash
# Indexar archivo
trus agente bibliotecario indexar documento.md
trus agente bibliotecario indexar codigo.py --tipo codigo
trus agente bibliotecario indexar chat.txt --tipo conversacion

# Indexar directorio
trus agente bibliotecario indexar-dir ./docs
trus agente bibliotecario indexar-dir ./src --extensiones .py,.js
```

### Investigador (Sócrates)

```bash
# Pregunta simple
trus agente investigador preguntar "¿Qué es TrustGraph?"

# Modo interactivo (chat continuo)
trus agente investigador preguntar -i

# Modo rápido vs profundo
trus agente investigador preguntar "arquitectura" --modo rapido
trus agente investigador preguntar "análisis detallado" --modo profundo
```

### Nocturno (Morpheo)

```bash
# Ejecutar ciclo manual
trus agente nocturno ciclo
trus agente nocturno ciclo --intensidad ligero
trus agente nocturno ciclo --intensidad profundo --duracion 720

# Programar automático
trus agente nocturno programar --hora 02:00 --frecuencia diario
trus agente nocturno programar --hora 03:00 --frecuencia semanal --intensidad profundo
```

### Estado y Utilidades

```bash
# Ver estado de agentes
trus agente status

# Instalar dependencias
make agent-install

# Probar agentes
make agent-test
```

---

## Ejemplos de Uso Programático

### Python Async

```python
import asyncio
from agents import CallimacoAgent, SocratesAgent, MorpheoAgent
from agents.callimaco import ContentType

async def flujo_completo():
    # 1. Callímaco indexa contenido
    callimaco = CallimacoAgent()

    with open("doc.md") as f:
        resultado_index = await callimaco.indexar(
            content=f.read(),
            content_type=ContentType.DOCUMENTO,
            source="doc.md"
        )

    print(f"Indexado: {resultado_index['entities_extracted']} entidades")

    # 2. Sócrates investiga
    socrates = SocratesAgent()

    resultado_busqueda = await socrates.investigar(
        query="¿Qué entidades fueron creadas?",
        context={"recent_index": resultado_index['content_hash']}
    )

    print(f"Respuesta: {resultado_busqueda['respuesta']}")

    # 3. Morpheo optimiza (ejecutar en noche)
    morpheo = MorpheoAgent()

    resultado_mantenimiento = await morpheo.ejecutar_ciclo(
        max_duration_minutes=360,
        intensity="normal"
    )

    print(f"Reparaciones: {resultado_mantenimiento['reparaciones_hechas']}")

asyncio.run(flujo_completo())
```

---

## Características Clave

### 🔧 Robusto
- Reintentos automáticos en errores
- Rollback en operaciones fallidas
- Validaciones en cada etapa
- Fallbacks heurísticos si no hay LLM

### ⚡ Eficiente
- Procesamiento paralelo de sub-consultas
- Batching de operaciones
- Punteros en lugar de contenido completo
- Optimización continua

### 🧠 Inteligente
- Toma de decisiones basada en contenido
- Estrategias adaptativas de búsqueda
- Aprendizaje de patrones (extensible)
- Clasificación semántica automática

### 🔌 Integrable
- CLI nativa (`trus agente ...`)
- API Python async/sync
- Scheduling automático
- Webhook-friendly

---

## Flujo de Trabajo Típico

### Día - Trabajo Activo

```
Usuario: Edita documentos, codea, tiene conversaciones
    ↓
Callímaco: Indexa todo automáticamente vía CLI
    ↓
Sócrates: Responde preguntas sobre el conocimiento
```

### Noche - Mantenimiento

```
02:00 AM: Cron dispara Morpheo
    ↓
Morpheo: Escanear → Analizar → Reparar → Optimizar
    ↓
06:00 AM: Reporte enviado, sistema optimizado
```

---

## Beneficios

| Antes | Después (con Agentes) |
|-------|----------------------|
| Indexación manual | Indexación inteligente automática |
| Búsqueda por keywords | Búsqueda semántica + grafo |
| Metadatos planos | Taxonomía jerárquica enriquecida |
| Problemas acumulados | Mantenimiento proactivo nocturno |
| Decisión humana de dónde guardar | Decisión automática óptima |
| Respuestas sin fuentes | Respuestas con punteros verificables |

---

## Próximos Pasos

1. **Conectar LLM real**: Integrar OpenAI/Anthropic para máxima inteligencia
2. **Web Dashboard**: UI para monitorear agentes en tiempo real
3. **Multi-agent colaborativo**: Agentes que se llaman entre sí
4. **Personalización**: Aprendizaje de preferencias del usuario
5. **Métricas avanzadas**: Observabilidad completa del sistema

---

## Filosofía del Diseño

> *"Damos a cada agente un nombre griego porque, como los filósofos de Alejandría,
> su trabajo es preservar y organizar el conocimiento humano para las generaciones futuras."*

- **Callímaco** → Como el bibliotecario que creó el Pinakes (primer catálogo de biblioteca)
- **Sócrates** → Como el filósofo que enseñaba mediante preguntas y diálogo
- **Morpheo** → Como el dios que da forma a los sueños durante el descanso

---

**TrustGraph Agents** - *La memoria del workspace, organizada por expertos digitales*
