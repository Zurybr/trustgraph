# TrustGraph - Memoria del Workspace

> Sistema Operativo de Contexto basado en grafos de conocimiento para el workspace.

## 🚀 Inicio Rápido

```bash
# 1. Setup interactivo
./setup.sh

# 2. Configurar LLM
trus agentes config-global -p openai -k TU_API_KEY

# 3. Iniciar servicios
trus infra start

# 4. Indexar
trus recordar proyecto

# 5. Consultar
trus query "¿Qué es TrustGraph?"
```

## 📖 Documentación

| Guía | Descripción |
|------|-------------|
| [docs/](./docs/README.md) | Índice de documentación |
| [docs/guides/QUICKSTART.md](./docs/guides/QUICKSTART.md) | Inicio rápido |
| [docs/agents/](./docs/agents/README.md) | Guía de agentes |
| [docs/providers/](./docs/providers/PROVIDER_SETUP.md) | Configurar LLMs |

## 🤖 CLI

```bash
trus infra start          # Iniciar Docker
trus agentes config-global # Configurar LLM
trus recordar archivo X   # Indexar
trus query "pregunta"     # Consultar
```

## 🏗️ Arquitectura

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Workbench  │────▶│ API Gateway  │────▶│   GraphRAG      │
│   (8888)    │     │   (8080)     │     │   Service       │
└─────────────┘     └──────────────┘     └────────┬────────┘
                                                  │
                          ┌────────────────────────┘
                          ▼
    ┌─────────────────────────────────────────────┐
    │  Cassandra (Grafo)     Qdrant (Vectores)    │
    │  - Entidades            - Embeddings        │
    └─────────────────────────────────────────────┘
```

## 🌐 Proveedores LLM Soportados

- **OpenAI** (gpt-4o)
- **Anthropic** (claude-3-5-sonnet)
- **Z.AI/GLM** (glm-5)
- **Kimi** (kimi-k2)
- **MiniMax** (MiniMax-M2.5)
- **Ollama** (local)

## 📚 Recursos

- **Web**: https://trustgraph.ai
- **GitHub**: https://github.com/trustgraph
- **CLI Help**: `trus --help`

## License

MIT
