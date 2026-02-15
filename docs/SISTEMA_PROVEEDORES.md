# Sistema de Proveedores LLM - Resumen Técnico

## 🎯 Objetivo
Sistema flexible para configurar y cambiar entre múltiples proveedores de LLM (especialmente modelos chinos) de forma sencilla.

## 📁 Archivos Modificados/Creados

### 1. Configuración Base
- **`.env.example`** - Variables de entorno organizadas por proveedor
- **`docker-compose.yaml`** - Pasa todas las variables a los contenedores

### 2. Scripts de Configuración
- **`scripts/setup_env.py`** - Wizard interactivo con menús navegables
- **`scripts/switch_provider.py`** - Cambio rápido de proveedor
- **`setup.sh`** - Ahora soporta comando `makeenv`

### 3. Comandos Makefile
- **`make makeenv`** - Ejecuta wizard de configuración
- **`make provider`** - Muestra menú/cambia proveedor
- **`make provider USE=<nombre>`** - Cambio directo

### 4. Documentación
- **`CLAUDE.md`** - Guía rápida actualizada
- **`README.md`** - Quick start con wizard
- **`trustgraph/SKILL.md`** - Comandos de skill
- **`docs/PROVIDER_SETUP.md`** - Guía detallada completa

## 🎮 Flujos de Uso

### Flujo 1: Primera Instalación (Wizard)
```bash
./setup.sh makeenv
# o
make makeenv
```
Navega con flechas, selecciona proveedor, ingresa API key, ¡listo!

### Flujo 2: Cambio Rápido (Comando General)
```bash
make provider USE=zai    # Cambia a Z.AI
make provider USE=kimi   # Cambia a Kimi
# etc.
```

### Flujo 3: Manual (Avanzado)
```bash
nano .env  # Editar directamente
docker compose restart
```

## 🔧 Proveedores Soportados

| Tipo | Proveedores | Formato API |
|------|-------------|-------------|
| OpenAI-compatible | OpenAI, Z.AI (GLM) | OpenAI |
| Anthropic-compatible | Anthropic, Kimi, MiniMax | Anthropic |
| Local | Ollama | Ollama API |

## 🌐 Endpoints y Modelos

### Z.AI (智谱AI)
- URL: https://api.z.ai/api/paas/v4
- Modelos: glm-5, glm-4.6v
- Variable: ZAI_API_KEY

### Kimi (Moonshot AI)
- URL: https://api.kimi.com/coding
- Modelos: kimi-k2, kimi-for-coding
- Variable: KIMI_API_KEY

### MiniMax
- URL: https://api.minimax.io/anthropic
- Modelos: MiniMax-M2.5
- Variable: MINIMAX_API_KEY

## 🧪 Testing

Probar el wizard:
```bash
python3 scripts/setup_env.py
```

Probar cambio de proveedor:
```bash
python3 scripts/switch_provider.py
```

Verificar variables:
```bash
grep "LLM_PROVIDER\|API_KEY" .env
```

## 📝 Notas de Implementación

1. **Navegación con flechas**: Usa tty/termios en Linux/Mac, fallback a input numérico
2. **Validación**: Verifica que las API keys no estén vacías ni sean placeholders
3. **Persistencia**: Todo se guarda en `.env`, compatible con docker-compose
4. **Flexibilidad**: Cada proveedor tiene su propio modelo, URL y key

## 🚀 Próximos Pasos Sugeridos

1. Probar el wizard: `./setup.sh makeenv`
2. Configurar proveedor preferido
3. Iniciar TrustGraph: `make up`
4. Cargar documentación: `make load`

---

Creado: 2026-02-15
Sistema: TrustGraph Multi-Provider LLM Configuration
