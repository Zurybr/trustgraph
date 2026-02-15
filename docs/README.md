# 📚 TrustGraph Documentation

**Idioma**: [Español](./README.md) | [English](./---

## Estructura deREADME.en.md)

 Documentación

```
docs/
├── README.md              # Este archivo - Índice principal
├── README.en.md          # English index
│
├── guides/               # Guías y tutoriales
│   ├── QUICKSTART.md     # Inicio rápido
│   ├── INSTALLATION.md   # Instalación detallada
│   └── TROUBLESHOOTING.md
│
├── agents/               # Documentación de Agentes
│   ├── README.md         # Guía principal de agentes
│   ├── README.en.md      # English version
│   ├── ARCHITECTURE.md   # Arquitectura técnica
│   ├── CALLIMACO.md     # Documentación Callímaco
│   ├── SOCRATES.md       # Documentación Sócrates
│   └── MORPHEO.md        # Documentación Morpheo
│
├── providers/            # Proveedores LLM
│   ├── PROVIDER_SETUP.md # Configuración de proveedores
│   └── SISTEMA_PROVEEDORES.md
│
└── api/                  # Documentación de API
    ├── REFERENCE.md      # Referencia de API
    └── ENDPOINTS.md      # Endpoints disponibles
```

---

## quick navigation

### 🔰 Inicio Rápido

```bash
# 1. Instalar TrustGraph
./setup.sh

# 2. Configurar proveedor LLM
trus agentes config-global -p openai -k TU_API_KEY

# 3. Iniciar servicios
trus infra start

# 4. Indexar documentos
trus recordar proyecto

# 5. Consultar
trus query "¿Qué es TrustGraph?"
```

### 🤖 Agentes

- **[Guía de Agentes](./agents/README.md)** - Introducción a Callímaco, Sócrates y Morpheo
- **[Arquitectura](./agents/ARCHITECTURE.md)** - Diagramas y detalles técnicos
- **[Configuración](./agents/SETUP.md)** - Cómo configurar cada agente

### 🌐 Proveedores LLM

- **[Setup de Proveedores](./providers/PROVIDER_SETUP.md)** - Configuración completa
- **[Sistema de Proveedores](./providers/SISTEMA_PROVEEDORES.md)** - Comparativa

### 💻 CLI

```bash
trus infra          # Gestión de Docker
trus agentes        # Configuración de LLM
trus recordar       # Indexar contenido
trus query          # Consultar memoria
```

---

## Comandos Esenciales

| Comando | Descripción |
|---------|-------------|
| `trus infra start` | Iniciar servicios |
| `trus infra stop` | Detener servicios |
| `trus agentes config-global -p <provider>` | Configurar LLM |
| `trus recordar archivo <ruta>` | Indexar archivo |
| `trus query "pregunta"` | Consultar |

---

## Recursos

- **GitHub**: https://github.com/trustgraph
- **Web**: https://trustgraph.ai
- **Issues**: https://github.com/trustgraph/issues

---

*Documentación TrustGraph v2.0*
