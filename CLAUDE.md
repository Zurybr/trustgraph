# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TrustGraph is a knowledge graph-based memory system for workspaces. It transforms documentation into an intelligent context graph using GraphRAG (Graph Retrieval-Augmented Generation). The system connects documents through semantic relationships, enabling intelligent queries beyond simple keyword search.

**Language**: Spanish (default for all user-facing content and documentation)

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Workbench  │────▶│ API Gateway  │────▶│   GraphRAG      │
│   (UI)      │     │   (8080)     │     │   Service       │
└─────────────┘     └──────────────┘     └────────┬────────┘
     8888                                         │
                                                  ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Grafana   │     │  Prometheus  │     │     Pulsar      │
│   (3000)    │     │   (9090)     │     │  (Message Bus)  │
└─────────────┘     └──────────────┘     └────────┬────────┘
                                                  │
                       ┌──────────────────────────┘
                       │
                       ▼
    ┌─────────────────────────────────────────────────────┐
    │  Cassandra (Graph)          Qdrant (Vectors)        │
    │  - Entity triples             - Document embeddings  │
    │  - Relationships              - Vector search        │
    └─────────────────────────────────────────────────────┘
```

### Data Flow

**Ingestion Pipeline:**
```
Document → Knowledge Builder → Entity Extraction → Cassandra (Triples)
                           ↓
                    Embeddings Generation → Qdrant (Vectors)
```

**Query Pipeline:**
```
Query → Vector Search → Graph Traversal → Context Assembly → LLM Response
```

## TrustGraph CLI (`trus`)

TrustGraph incluye una CLI robusta para gestionar el sistema desde cualquier terminal, con soporte para conexiones locales y remotas.

### Instalación CLI

```bash
# Instalar CLI (desde el repositorio)
./install/install-cli.sh

# O instalar desde remoto
curl -fsSL https://tu-dominio/install-cli.sh | bash
```

### Comandos Principales de la CLI

**Configuración y Conexión:**
```bash
trus login                    # Configurar conexión (local/remoto)
trus status                   # Ver estado de conexión
```

**Guardar e Indexar:**
```bash
trus recordar archivo documento.md
trus recordar directorio ./docs/
trus recordar proyecto       # Indexa proyecto completo
```

**Consultar Memoria:**
```bash
trus query "¿Qué es TrustGraph?"
trus query -i                # Modo interactivo
```

**Configurar Proveedor LLM:**
```bash
trus config provider zai     # Cambiar a Z.AI
trus config provider kimi    # Cambiar a Kimi
trus config apikey           # Configurar API key
trus config show             # Ver configuración
```

**Gestión de Servicios (solo local):**
```bash
trus servicios start         # Iniciar TrustGraph
trus servicios stop          # Detener
trus servicios restart       # Reiniciar
trus servicios logs          # Ver logs
```

### Configuración de Acceso Remoto

Para permitir que otros agentes se conecten a tu TrustGraph:

**En el servidor:**
```bash
./setup.sh remote            # Configura acceso remoto
```

**En el agente cliente:**
```bash
./setup.sh install-cli       # Instala solo CLI
trus login --host IP_SERVIDOR --port 8080
```

## Common Commands (Makefile)

All development commands are available through the Makefile:

```bash
# Setup and Configuration
make setup          # Initial setup: creates .env and data directories
make help           # Show all available commands

# Lifecycle Management
make up             # Start all services (docker compose up -d)
make down           # Stop all services
make status         # Check service status
make health         # Health check API endpoint
make logs           # View logs from all services
make dev            # Development mode with verbose logging

# Data Operations
make load           # Load documentation into TrustGraph
make query          # Interactive query mode
make search QUERY="..."  # Quick search (requires QUERY parameter)
make reset          # Reset all data and reload (interactive confirmation)
make clean          # Complete cleanup including volumes (interactive confirmation)

# Backup/Restore
make backup         # Create backup of data/
make restore        # Restore from latest backup
make update         # Pull latest images and restart

# Direct Docker Compose (when needed)
docker compose up -d
docker compose logs -f [service]
docker compose exec api-gateway /bin/sh
```

## Service Ports

| Service | Port | Purpose |
|---------|------|---------|
| Workbench UI | 8888 | Main web interface |
| API Gateway | 8080 | REST API / WebSocket |
| Grafana | 3000 | Monitoring dashboards (admin/admin) |
| Prometheus | 9090 | Metrics collection |
| Qdrant | 6333 | Vector database API |

## Key Files and Locations

### Configuration
- `.env` - Environment variables (created from `.env.example` during setup)
- `config/context-core.yaml` - Knowledge base schema and collections config
- `config/garage.toml` - Object storage configuration
- `docker-compose.yaml` - Service orchestration

### Scripts
- `scripts/load_docs.py` - Document ingestion into TrustGraph
- `scripts/query_graphrag.py` - Query interface and CLI tool
- `scripts/mcp_server.py` - MCP server for Claude Code integration
- `scripts/switch_provider.py` - Switch between LLM providers (openai, zai, kimi, minimax, ollama)
- `scripts/setup_env.py` - Interactive environment setup wizard

### CLI (`cli/`)
- `cli/trus.py` - Main CLI implementation (installs as `trus` command)
- `cli/requirements.txt` - CLI dependencies
- `cli/README.md` - CLI documentation

### Install Scripts (`install/`)
- `install/setup-master.sh` - Master interactive menu with arrow navigation
- `install/setup-local.sh` - Setup local TrustGraph server
- `install/setup-server.sh` - Configure remote access
- `install/install-cli.sh` - Install CLI only
- `install/uninstall-cli.sh` - Uninstall CLI
- `install/quick-install-cli.sh` - Standalone remote installer

### Data Directories (gitignored, persistent)
- `data/cassandra/` - Graph database storage
- `data/qdrant/` - Vector database storage
- `data/pulsar/` - Message broker data
- `data/grafana/` - Dashboard configurations
- `data/prometheus/` - Metrics data
- `data/loki/` - Log aggregation

## Installation Guide

### Option 1: Interactive Master Setup (Recommended)
```bash
./setup.sh
```
Shows interactive menu with arrow navigation to select installation type.

### Option 2: Complete Local Setup
```bash
./setup.sh server    # Setup TrustGraph server + CLI
```

### Option 3: CLI Only (for remote agents)
```bash
./setup.sh install-cli
# Then configure connection:
trus login --host IP_REMOTO
```

### Setup Commands Reference
```bash
./setup.sh                    # Master menu (interactive)
./setup.sh makeenv           # Configure LLM provider
./setup.sh server            # Setup local server
./setup.sh remote            # Configure remote access
./setup.sh install-cli       # Install CLI only
./setup.sh uninstall-cli     # Remove CLI
./setup.sh uninstall-all     # Remove everything
```

## Python Scripts Usage

### Loading Documents
```bash
# Load default documentation directory
python scripts/load_docs.py

# Load specific directory
python scripts/load_docs.py /path/to/docs

# Dry run (simulate without sending)
python scripts/load_docs.py --dry-run

# Filter by category
python scripts/load_docs.py --category trustgraph
```

Supported file types: `.md`, `.txt`, `.rst`, `.py`, `.js`, `.ts`, `.json`, `.yaml`, `.yml`, `.toml`

### Querying
```bash
# Simple question
python scripts/query_graphrag.py "¿Qué es TrustGraph?"

# Interactive mode
python scripts/query_graphrag.py --interactive

# Vector search only
python scripts/query_graphrag.py --search "instalación"

# Graph exploration
python scripts/query_graphrag.py --graph --depth 3

# List context cores
python scripts/query_graphrag.py --cores
```

## API Usage

### Health Check
```bash
curl http://localhost:8080/api/v1/health
```

### GraphRAG Query
```bash
curl -X POST http://localhost:8080/api/v1/graphrag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Qué es TrustGraph?",
    "context_core": "documentation",
    "include_sources": true
  }'
```

### Vector Search
```bash
curl -X POST http://localhost:8080/api/v1/search/vector \
  -H "Content-Type: application/json" \
  -d '{
    "query": "arquitectura del sistema",
    "collection": "docs",
    "limit": 5
  }'
```

## Environment Configuration

### LLM Provider Selection

TrustGraph supports multiple LLM providers. Edit `.env` and set `LLM_PROVIDER`:

| Provider | Type | Models | Base URL |
|----------|------|--------|----------|
| `openai` | OpenAI-compatible | GPT-4, GPT-4o, GPT-3.5 | https://api.openai.com/v1 |
| `anthropic` | Anthropic-compatible | Claude 3.5 Sonnet, Claude 3 Opus | https://api.anthropic.com |
| `zai` | OpenAI-compatible | GLM-5, GLM-4.6V | https://api.z.ai/api/paas/v4 |
| `kimi` | Anthropic-compatible | Kimi K2, Kimi Code | https://api.kimi.com/coding |
| `minimax` | Anthropic-compatible | MiniMax-M2.5 | https://api.minimax.io/anthropic |
| `ollama` | Local | llama3.1, qwen, etc. | http://host.docker.internal:11434 |

### Quick Provider Switch (Comando General)

**Wizard Interactivo de Configuración (Recomendado para primera vez):**
```bash
# Configuración guiada paso a paso con menús
make makeenv
# o
./setup.sh makeenv
# o
python3 scripts/setup_env.py
```

Este wizard te permite:
- Navegar con flechas ↑↓ entre proveedores
- Ver detalles de cada modelo
- Ingresar tu API key
- Confirmar el modelo a usar

**Cambio rápido (para usuarios avanzados):**
```bash
# Ver menú interactivo
make provider

# Cambiar directamente a cualquier proveedor
make provider USE=zai
make provider USE=kimi
make provider USE=minimax
make provider USE=openai
make provider USE=ollama
```

Después de cambiar, reinicia TrustGraph:
```bash
docker compose restart
```

**📖 Documentación detallada:** Ver `docs/PROVIDER_SETUP.md` para guías completas de cada proveedor.

### Required Variables

**OpenAI:**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-4o
```

**Z.AI (智谱AI/GLM):**
```bash
LLM_PROVIDER=zai
ZAI_API_KEY=your-zai-key
ZAI_MODEL=glm-5
# Use https://api.z.ai/api/coding/paas/v4 for Coding endpoint
```

**Kimi (Moonshot AI):**
```bash
LLM_PROVIDER=kimi
KIMI_API_KEY=sk-kimi-your-key
KIMI_MODEL=kimi-k2
```

**MiniMax:**
```bash
LLM_PROVIDER=minimax
MINIMAX_API_KEY=your-minimax-key
MINIMAX_MODEL=MiniMax-M2.5
# Use https://api.minimaxi.com/anthropic for China
```

**Ollama (Local):**
```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.1
```

### Project Settings
```bash
CONTEXT_CORE_ID=documentation
COLLECTION_NAME=docs
```

## Project Structure Conventions

- **Language**: All documentation and user-facing content in Spanish
- **Scripts**: Python 3.x with httpx or requests for HTTP calls
- **Configuration**: YAML for complex config, TOML for service-specific
- **Documentation**: Markdown files, stored in `documentation/` or project root
- **Data persistence**: All data in `data/` directory (gitignored)

## Troubleshooting

### Services not responding
```bash
docker compose ps
docker compose logs -f workbench
docker compose restart
```

### API key errors
```bash
source .env
docker compose restart
```

### Port conflicts
```bash
lsof -i :8888  # Find process using port
# Or modify ports in docker-compose.yaml
```

### Reset everything (destructive)
```bash
make clean  # Removes all data and volumes
make setup  # Reconfigure
make up     # Restart
make load   # Reload documents
```

## Resource Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 4 cores | 8+ cores |
| RAM | 8 GB | 16+ GB |
| Disk | 50 GB SSD | 100+ GB SSD |

## Integration with Claude Code

TrustGraph includes an MCP server for Claude Code integration:

```json
// ~/.claude/settings.json
{
  "mcpServers": {
    "trustgraph": {
      "command": "python",
      "args": ["/path/to/trustgraph/scripts/mcp_server.py"]
    }
  }
}
```

The project also defines a skill in `trustgraph/SKILL.md` that can be installed via:
```bash
npx skills add trustgraph
```
