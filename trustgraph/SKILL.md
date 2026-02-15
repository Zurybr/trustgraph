---
name: trustgraph
description: Operar y gestionar TrustGraph - sistema de memoria basado en grafos de conocimiento. Usar cuando el usuario necesite configurar, iniciar, detener, cargar documentación o hacer consultas a TrustGraph. Incluye workflows para setup inicial, ingesta de documentos, consultas GraphRAG, monitoreo y troubleshooting.
---

# TrustGraph Skill

Guía completa para operar TrustGraph - tu "segundo cerebro" digital para el workspace.

## ¿Qué es TrustGraph?

Sistema de memoria basado en grafos de conocimiento que:
- Conecta documentación mediante relaciones semánticas
- Permite consultas inteligentes usando GraphRAG (no solo búsqueda por palabras clave)
- Almacena datos en Cassandra (grafo) y Qdrant (vectores)
- Expone API REST y UI web en localhost:8888

## Requisitos Previos

- Docker y Docker Compose instalados
- Python 3.x con `httpx` (`pip install httpx`)
- API key de LLM (OpenAI, Anthropic, o Ollama local)

## Flujos de Trabajo

### 1. Setup Inicial (Primera vez)

```bash
# 1. Configurar variables de entorno
cp .env.example .env
# Editar .env con API keys

# 2. Crear directorios de datos
make setup
# O manualmente:
mkdir -p data/{cassandra,qdrant,garage,pulsar,prometheus,grafana,loki}
```

### 2. Iniciar TrustGraph

```bash
# Iniciar todos los servicios
make up

# Verificar estado
make status
make health

# Ver logs en tiempo real
make logs
```

Servicios disponibles después de iniciar:
- Workbench UI: http://localhost:8888
- API Gateway: http://localhost:8080
- Grafana: http://localhost:3000 (admin/admin)

### 3. Cargar Documentación

```bash
# Cargar documentación del workspace
make load

# O con opciones avanzadas:
python scripts/load_docs.py --dry-run              # Simular sin enviar
python scripts/load_docs.py --category trustgraph  # Filtrar por categoría
python scripts/load_docs.py /ruta/a/docs          # Directorio específico
```

**Nota:** La primera carga puede tardar varios minutos dependiendo del volumen.

### 4. Consultar Memoria (GraphRAG)

```bash
# Modo interactivo (recomendado)
make query

# Búsqueda directa
make search QUERY="¿Qué es TrustGraph?"

# Comandos avanzados:
python scripts/query_graphrag.py "tu pregunta aquí"
python scripts/query_graphrag.py --search "término"
python scripts/query_graphrag.py --graph --depth 3
python scripts/query_graphrag.py --cores
```

### 5. Detener y Limpiar

```bash
# Detener servicios (conserva datos)
make down

# Limpieza completa (⚠️ elimina todos los datos)
make clean

# Resetear y recargar
make reset
```

## Comandos Makefile Rápidos

| Comando | Descripción |
|---------|-------------|
| `make help` | Ver todos los comandos |
| `make setup` | Configuración inicial |
| `make up` | Iniciar servicios |
| `make down` | Detener servicios |
| `make status` | Estado de servicios |
| `make health` | Health check |
| `make logs` | Ver logs |
| `make load` | Cargar documentación |
| `make query` | Modo interactivo |
| `make search QUERY="..."` | Búsqueda rápida |
| `make clean` | Limpieza total |
| `make backup` | Crear backup |
| `make restore` | Restaurar backup |

## Configuración (.env)

Variables esenciales:

```bash
# Proveedor de LLM
LLM_PROVIDER=openai              # o anthropic, ollama
OPENAI_API_KEY=sk-your-key

# Ollama local
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434

# Configuración del proyecto
CONTEXT_CORE_ID=documentation
COLLECTION_NAME=docs
```

## API REST

Endpoints principales:

```bash
# Health check
curl http://localhost:8080/api/v1/health

# GraphRAG query
curl -X POST http://localhost:8080/api/v1/graphrag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Qué es TrustGraph?",
    "context_core": "documentation",
    "include_sources": true
  }'

# Vector search
curl -X POST http://localhost:8080/api/v1/search/vector \
  -H "Content-Type: application/json" \
  -d '{
    "query": "arquitectura del sistema",
    "collection": "docs",
    "limit": 5
  }'
```

## Troubleshooting

### TrustGraph no responde

```bash
# Verificar servicios
docker compose ps

# Ver logs
docker compose logs -f workbench
docker compose logs -f graphrag

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

# Matar o cambiar puerto en docker-compose.yaml
```

### Problemas de ingesta

```bash
# Verificar que Pulsar esté listo
docker compose logs pulsar

# Reintentar carga
python scripts/load_docs.py --retries 3
```

## Recursos del Sistema

| Recurso | Mínimo | Recomendado |
|---------|--------|-------------|
| CPU | 4 cores | 8+ cores |
| RAM | 8 GB | 16+ GB |
| Disco | 50 GB SSD | 100+ GB SSD |

## Arquitectura Resumida

```
Usuario → Workbench/UI → API Gateway → GraphRAG/Knowledge Builder
                                            ↓
                    Cassandra (Grafo) ← Pulsar → Qdrant (Vectores)
```

## Pipeline de Datos

1. **Ingesta**: Documentos → Knowledge Builder
2. **Procesamiento**: Extracción de entidades y relaciones
3. **Almacenamiento**: Triples → Cassandra, Embeddings → Qdrant
4. **Consulta**: Query → Vector Search → Graph Traversal → Respuesta
