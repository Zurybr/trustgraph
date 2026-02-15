# 📚 TrustGraph Documentation

**Idioma**: [Español](./README.md) | [English](./README.en.md)

---

## Documentation Structure

```
docs/
├── README.md              # This file - Main index
├── README.en.md          # English index
│
├── guides/               # Guides and tutorials
│   ├── QUICKSTART.md     # Quick start guide
│   ├── INSTALLATION.md   # Detailed installation
│   └── TROUBLESHOOTING.md
│
├── agents/               # Agents documentation
│   ├── README.md         # Main agents guide
│   ├── README.en.md      # English version
│   ├── ARCHITECTURE.md   # Technical architecture
│   ├── CALLIMACO.md     # Callimachus docs
│   ├── SOCRATES.md       # Socrates docs
│   └── MORPHEO.md        # Morpheus docs
│
├── providers/            # LLM Providers
│   ├── PROVIDER_SETUP.md # Provider setup
│   └── SISTEMA_PROVEEDORES.md
│
└── api/                  # API documentation
    ├── REFERENCE.md      # API reference
    └── ENDPOINTS.md      # Available endpoints
```

---

## Quick Navigation

### 🔰 Quick Start

```bash
# 1. Install TrustGraph
./setup.sh

# 2. Configure LLM provider
trus agentes config-global -p openai -k YOUR_API_KEY

# 3. Start services
trus infra start

# 4. Index documents
trus recordar proyecto

# 5. Query
trus query "¿What is TrustGraph?"
```

### 🤖 Agents

- **[Agents Guide](./agents/README.md)** - Introduction to Callimachus, Socrates and Morpheus
- **[Architecture](./agents/ARCHITECTURE.md)** - Technical diagrams and details

### 🌐 LLM Providers

- **[Provider Setup](./providers/PROVIDER_SETUP.md)** - Complete configuration

### 💻 CLI

```bash
trus infra          # Docker management
trus agentes        # LLM configuration
trus recordar       # Index content
trus query          # Query memory
```

---

## Essential Commands

| Command | Description |
|---------|-------------|
| `trus infra start` | Start services |
| `trus infra stop` | Stop services |
| `trus agentes config-global -p <provider>` | Configure LLM |
| `trus recordar archivo <path>` | Index file |
| `trus query "question"` | Query |

---

## Resources

- **GitHub**: https://github.com/trustgraph
- **Web**: https://trustgraph.ai

---

*TrustGraph Documentation v2.0*
