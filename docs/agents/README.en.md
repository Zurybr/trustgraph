# 🤖 TrustGraph Agents

**Language: [Español](./README.md) | [English](./README.en.md)**

Intelligent multi-agent system for TrustGraph based on LangGraph.

---

## The Three Guardians of Knowledge

### 📚 Callimachus (Καλλίμαχος) - The Librarian of Alexandria

> *"I organize so that knowledge endures for millennia"*

**Responsibility**: Indexing and structured organization of knowledge.

Callimachus is the agent responsible for receiving any type of content (documents, conversations, code, images) and intelligently deciding:

- **What goes to Cassandra (Graph)**: Entities, relationships, structure
- **What goes to Qdrant (Vectors)**: Semantic content, embeddings
- **How to tag**: Hierarchical taxonomy, enriched metadata
- **Quality validation**: Completeness, consistency, non-duplication

**Workflow**:
```
CLASSIFY → EXTRACT → TAG → PLAN → VALIDATE → STORE
```

**CLI Usage**:
```bash
# Index a file
trus agente bibliotecario indexar document.md --tipo documento

# Index entire directory
trus agente bibliotecario indexar-dir ./docs --extensiones .md,.py
```

---

### 🔍 Socrates (Σωκράτης) - The Dialectical Investigator

> *"I know that I know nothing, but I know exactly where to look"*

**Responsibility**: Advanced search and response synthesis.

Socrates receives complex questions and applies the dialectical method:

1. **Maieutic (μαιευτική)**: Extracts the real user intent
2. **Diairesis (διαίρεσις)**: Divides the query into atomic sub-queries
3. **Synagoge (συναγωγή)**: Collects pointers from multiple sources
4. **Anakrisis (ἀνάκρισις)**: Examines and selects the best pointers
5. **Synthesis (σύνθεσις)**: Synthesizes coherent response

**Search Strategies**:
- `vector_puro`: Direct semantic similarity
- `grafo_puro`: Entity and relationship navigation
- `grafo_rag`: Complete GraphRAG
- `hibrido`: Vector + Graph combination
- `entidad_primero`: Find entity then expand

**CLI Usage**:
```bash
# Simple question
trus agente investigator preguntar "¿What is TrustGraph?"

# Interactive mode
trus agente investigator preguntar -i

# Quick vs deep search
trus agente investigator preguntar "architecture" --modo rapido
```

---

### 🌙 Morpheus (Μορφεύς) - The Dream Guardian

> *"In dreams I repair what daylight wears down"*

**Responsibility**: Nighttime maintenance, optimization and repair.

Morpheus runs during low activity hours to:

- **Repair**: Duplicates, orphans, corrupted, obsolete
- **Optimize**: Reindex, consolidate, compress, enrich
- **Defragment**: Reorganize storage for efficiency
- **Consolidate**: Merge related chunks

**Night Cycle (Hypnos)**:
```
SCAN → ANALYZE → PLAN → REPAIR → OPTIMIZE → REPORT
```

**Intensity Levels**:
- `ligero`: Basic reindexing (1-2 hours)
- `normal`: Repairs + consolidation (3-6 hours)
- `profundo`: Everything + complete analysis (6-12 hours)

**CLI Usage**:
```bash
# Run cycle manually
trus agente nocturnal ciclo --intensidad normal --duracion 360

# Schedule automatic cycles
trus agente nocturnal programar --hora 02:00 --frecuencia semanal
```

---

## Reorganized CLI Structure

### 🐳 Infra (Docker and Infrastructure)

```bash
trus infra start          # Start Docker services
trus infra stop          # Stop services
trus infra restart       # Restart services
trus infra status        # Service status
trus infra logs          # View logs
trus infra setup         # Configure .env
trus infra health        # Health check
```

### 🤖 Agents (LLM Configuration)

```bash
# View configuration
trus agentes show         # Show all agents config
trus agentes status      # Agent status

# Global configuration (shared by all)
trus agentes config-global --provider openai
trus agentes config-global -p zai -k TU_API_KEY

# Per-agent configuration (individual)
trus agentes config-agente bibliotecario --provider zai
trus agentes config-agente investigador -k OWN_API_KEY
trus agentes config-agente nocturno --inactivo
```

---

## Agent Configuration

### Global Configuration

All agents can share a common configuration:

```bash
trus agentes config-global -p openai -k sk-... -m gpt-4o
```

### Per-Agent Configuration

Each agent can have its own provider and API key:

```bash
# Librarian with Z.AI
trus agentes config-agente bibliotecario -p zai -k ZAI_API_KEY

# Investigator with OpenAI
trus agentes config-agente investigador -p openai -k OPENAI_API_KEY

# Night agent with Anthropic
trus agentes config-agente nocturno -p anthropic -k ANTHROPIC_API_KEY
```

### Configuration Hierarchy

1. **Agent configuration** (most specific)
2. **Global configuration** (fallback)
3. **Default values** (last resort)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     LangGraph Engine                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐    │
│  │   States    │  │    Nodes    │  │  Conditionals   │    │
│  │  (Dataclass)│  │ (Functions) │  │    (Routes)     │    │
│  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘    │
│         │                │                   │             │
│         └────────────────┴───────────────────┘             │
│                          │                                 │
│                    ┌─────┴─────┐                          │
│                    │  Graph    │  ← Workflow defined    │
│                    │ Compiled  │     specifically        │
│                    └─────┬─────┘                          │
└──────────────────────────┼────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │ Callimachus│  │  Socrates  │  │  Morpheus  │
    │  (Index)   │  │  (Search)  │  │ (Maintain) │
    └─────┬──────┘  └─────┬──────┘  └─────┬──────┘
          │               │               │
          └───────────────┼───────────────┘
                          ▼
              ┌─────────────────────┐
              │  TrustGraph API       │
              │   localhost:8080     │
              └─────────────────────┘
```

---

## Installation

```bash
# Install dependencies
pip install -r agents/requirements.txt

# Or with the complete project
pip install -e .
```

---

## Programmatic Usage

```python
import asyncio
from agents import CallimacoAgent, SocratesAgent, MorpheoAgent
from agents.callimaco import ContentType

async def full_flow():
    # 1. Callimachus indexes content
    callimaco = CallimacoAgent(
        api_gateway="http://localhost:8080",
        llm_config={
            "provider": "openai",
            "api_key": "sk-...",
            "model": "gpt-4o"
        }
    )

    with open("doc.md") as f:
        index_result = await callimaco.indexar(
            content=f.read(),
            content_type=ContentType.DOCUMENTO,
            source="doc.md"
        )

    print(f"Indexed: {index_result['entities_extracted']} entities")

    # 2. Socrates investigates
    socrates = SocratesAgent(
        api_gateway="http://localhost:8080",
        llm_config={"provider": "anthropic", "api_key": "sk-..."}
    )

    search_result = await socrates.investigar(
        query="What entities were created?"
    )

    print(f"Answer: {search_result['respuesta']}")

    # 3. Morpheus optimizes
    morpheus = MorpheoAgent(
        api_gateway="http://localhost:8080",
        llm_config={"provider": "openai", "api_key": "sk-..."}
    )

    maintenance_result = await morpheus.ejecutar_ciclo(
        max_duration_minutes=360,
        intensity="normal"
    )

    print(f"Repairs: {maintenance_result['reparaciones_hechas']}")

asyncio.run(full_flow())
```

---

## Command Reference

### Main CLI (trus)

| Command | Description |
|---------|-------------|
| `trus infra *` | Docker management |
| `trus agentes *` | Agent configuration |
| `trus recordar archivo <path>` | Index file |
| `trus recordar directorio <path>` | Index directory |
| `trus query "text"` | Query memory |
| `trus status` | General status |

### Infra

| Command | Description |
|---------|-------------|
| `trus infra start` | Start Docker |
| `trus infra stop` | Stop Docker |
| `trus infra restart` | Restart Docker |
| `trus infra status` | Docker status |
| `trus infra logs` | View logs |
| `trus infra health` | Health check |

### Agents

| Command | Description |
|---------|-------------|
| `trus agentes show` | View configuration |
| `trus agentes status` | Agent status |
| `trus agentes config-global` | Global LLM config |
| `trus agentes config-agente <agent>` | Specific agent config |

---

## Supported Providers

| Provider | Default Model | API Key Variable |
|----------|---------------|------------------|
| `openai` | gpt-4o | OPENAI_API_KEY |
| `anthropic` | claude-3-5-sonnet | ANTHROPIC_API_KEY |
| `zai` | glm-5 | ZAI_API_KEY |
| `kimi` | kimi-k2 | KIMI_API_KEY |
| `minimax` | MiniMax-M2.5 | MINIMAX_API_KEY |
| `ollama` | llama3.1 | (local) |

---

## License

MIT License - TrustGraph Team
