# TrustGraph - Memoria del Workspace

Sistema Operativo de Contexto basado en grafos de conocimiento para el workspace. Transforma la documentación existente en un grafo de contexto inteligente que puede ser consultado usando GraphRAG.

## 🎯 Instalación Rápida con Skill (Recomendado)

Instala TrustGraph como una skill de AI agent para acceso instantáneo:

```bash
# Buscar la skill
npx skills find trustgraph

# Instalar la skill
npx skills add tu-usuario/trustgraph
```

Una vez instalada, Kimi reconocerá automáticamente comandos como:
- "Inicia TrustGraph"
- "Carga documentación en TrustGraph"
- "Consulta TrustGraph sobre..."

Para una guía paso a paso detallada, ver [README_DUMMIES.md](README_DUMMIES.md).

## 🚀 Quick Start (Manual)

### Opción A - Setup con Wizard Interactivo (Recomendado)

```bash
# 1. Configuración interactiva con menús navegables
./setup.sh makeenv
# ↑↓ para navegar, ENTER para seleccionar proveedor

# 2. Iniciar TrustGraph
make up

# 3. Cargar documentación
make load

# 4. Acceder al Workbench
open http://localhost:8888
```

### Opción B - Setup Manual

```bash
# 1. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys manualmente

# 2-4. Igual que Opción A
make up && make load
```

## 📁 Estructura del Proyecto

```
trustgraph/
├── docker-compose.yaml          # Configuración de servicios
├── .env.example                 # Variables de entorno de ejemplo
├── README.md                    # Esta documentación
├── config/                      # Configuraciones
│   ├── context-core.yaml       # Configuración del knowledge base
│   ├── garage.toml             # Object storage config
│   ├── prometheus.yml          # Métricas
│   ├── loki.yml                # Logging
│   ├── promtail.yml            # Log collector
│   └── grafana/                # Dashboards
├── scripts/                     # Scripts de utilidad
│   ├── load_docs.py            # Cargar documentación
│   └── query_graphrag.py       # Consultar memoria
└── data/                        # Datos persistentes (gitignored)
    ├── cassandra/              # Graph database
    ├── qdrant/                 # Vector database
    ├── garage/                 # Object storage
    ├── pulsar/                 # Message broker
    ├── prometheus/             # Métricas
    ├── grafana/                # Dashboards
    └── loki/                   # Logs
```

## 🔧 Servicios

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| Workbench UI | [8888](http://localhost:8888) | Interfaz web principal |
| API Gateway | [8080](http://localhost:8080) | API REST/WebSocket |
| Grafana | [3000](http://localhost:3000) | Dashboards (admin/admin) |
| Prometheus | [9090](http://localhost:9090) | Métricas |
| Qdrant | [6333](http://localhost:6333) | Vector DB API |

## 🧠 Uso

### Cargar Documentación

```bash
# Cargar todo desde documentation/
python scripts/load_docs.py

# Cargar directorio específico
python scripts/load_docs.py ../otros-docs

# Simular sin enviar (dry-run)
python scripts/load_docs.py --dry-run

# Filtrar por categoría
python scripts/load_docs.py --category trustgraph
```

### Consultar Memoria

```bash
# Pregunta simple
python scripts/query_graphrag.py "¿Qué es TrustGraph?"

# Modo interactivo
python scripts/query_graphrag.py --interactive

# Búsqueda vectorial
python scripts/query_graphrag.py --search "instalación"

# Explorar grafo
python scripts/query_graphrag.py --graph --depth 3

# Listar context cores
python scripts/query_graphrag.py --cores
```

### API REST

```bash
# Health check
curl http://localhost:8080/api/v1/health

# GraphRAG Query
curl -X POST http://localhost:8080/api/v1/graphrag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Qué es TrustGraph?",
    "context_core": "documentation",
    "include_sources": true
  }'

# Vector Search
curl -X POST http://localhost:8080/api/v1/search/vector \
  -H "Content-Type: application/json" \
  -d '{
    "query": "arquitectura del sistema",
    "collection": "docs",
    "limit": 5
  }'
```

## ⚙️ Configuración

### Variables de Entorno

```bash
# LLM Provider: openai, anthropic, zai, kimi, minimax, ollama
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key

# O usar modelos chinos (Z.AI GLM, Kimi, MiniMax)
LLM_PROVIDER=zai
ZAI_API_KEY=your-zai-key

# O usar Ollama local
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434

# Configuración del proyecto
CONTEXT_CORE_ID=documentation
COLLECTION_NAME=docs
```

### Cambio Rápido de Proveedor

**Wizard Interactivo (con menús navegables):**
```bash
# Configuración completa con flechas ↑↓ para navegar
make makeenv
# o
./setup.sh makeenv
```

**Comando General Rápido:**
```bash
# Ver menú interactivo
make provider

# Cambiar directamente a cualquier proveedor
make provider USE=zai       # Z.AI (GLM-5)
make provider USE=kimi      # Kimi (K2)
make provider USE=minimax   # MiniMax (M2.5)
make provider USE=openai    # OpenAI (GPT-4o)
make provider USE=ollama    # Ollama local

# Reiniciar para aplicar cambios
docker compose restart
```

### Proveedores Soportados

| Proveedor | Modelos | Tipo API |
|-----------|---------|----------|
| OpenAI | GPT-4, GPT-4o, GPT-3.5 | OpenAI |
| Anthropic | Claude 3.5 Sonnet, Claude 3 Opus | Anthropic |
| **Z.AI (智谱AI)** | **GLM-5, GLM-4.6V** | OpenAI-compatible |
| **Kimi** | **Kimi K2, Kimi Code** | Anthropic-compatible |
| **MiniMax** | **MiniMax-M2.5** | Anthropic-compatible |
| Ollama | llama3.1, qwen, etc. | Local |

### Recursos Requeridos

| Recurso | Mínimo | Recomendado |
|---------|--------|-------------|
| CPU | 4 cores | 8+ cores |
| RAM | 8 GB | 16+ GB |
| Disco | 50 GB SSD | 100+ GB SSD |

## 🐳 Comandos Docker

```bash
# Iniciar todo
docker compose up -d

# Ver logs
docker compose logs -f

# Ver logs de un servicio
docker compose logs -f graphrag

# Escalar servicio
docker compose up -d --scale graphrag=3

# Detener todo
docker compose down

# Detener y eliminar datos
docker compose down -v

# Reconstruir
docker compose up -d --build
```

## 📊 Monitoreo

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Métricas**: LLM latency, error rates, token throughput

## 🔄 Pipeline GraphRAG

```
Documento → Text Load → Knowledge Builder → Triples → Cassandra
                                    ↓
                            Embeddings → Qdrant

Query → GraphRAG → Vector Search → Graph Traversal → Context Assembly → Response
```

## 🛠️ Troubleshooting

### TrustGraph no responde

```bash
# Verificar servicios
docker compose ps

# Ver logs
docker compose logs -f workbench

# Reiniciar
docker compose restart
```

### Error de API Key

```bash
# Verificar variable
echo $OPENAI_API_KEY

# Recargar .env
source .env

# Reiniciar servicios
docker compose restart
```

### Puerto ocupado

```bash
# Encontrar proceso
lsof -i :8888

# Matar proceso o cambiar puerto en docker-compose.yaml
```

## 📚 Documentación

- [TrustGraph Docs](https://docs.trustgraph.ai)
- [TrustGraph GitHub](https://github.com/trustgraph-ai/trustgraph)
- [API Reference](../documentation/trustgraph/api-reference.md)

## 🤝 Integración con Claude Code

TrustGraph puede integrarse con Claude Code a través de MCP:

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

Ver [integracion-claude.md](../documentation/ecosystem/trustgraph/integracion-claude.md) para más detalles.

## 📝 Notas

- Los datos se almacenan en `data/` (persistentes entre reinicios)
- Para producción, usa Kubernetes y configura backups
- La primera carga de documentos puede tardar varios minutos
- Usa `--dry-run` para probar antes de cargar

## 🆘 Soporte

- GitHub Issues: https://github.com/trustgraph-ai/trustgraph/issues
- Discord: https://discord.gg/trustgraph
