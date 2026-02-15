# Guía de Configuración de Proveedores LLM

TrustGraph soporta múltiples proveedores de LLM, incluyendo modelos chinos (Z.AI, Kimi, MiniMax) y modelos occidentales (OpenAI, Anthropic).

## 🚀 Métodos de Configuración

### 1. Wizard Interactivo (Recomendado)

El método más fácil y rápido para configurar tu proveedor:

```bash
# Usando make (recomendado)
make makeenv

# Usando el script de setup
./setup.sh makeenv

# Directamente con Python
python3 scripts/setup_env.py
```

**Características del wizard:**
- ✅ Navegación con flechas ↑↓
- ✅ Descripción detallada de cada proveedor
- ✅ Validación de API keys
- ✅ Confirmación de modelos
- ✅ Compatible con todas las terminales

### 2. Comando General Rápido

Para cambiar de proveedor después de la configuración inicial:

```bash
# Ver menú interactivo
make provider

# Cambiar directamente
make provider USE=zai
make provider USE=kimi
make provider USE=minimax
make provider USE=openai
make provider USE=anthropic
make provider USE=ollama
```

### 3. Configuración Manual

Para usuarios avanzados que prefieren editar directamente:

```bash
# Editar el archivo .env
nano .env
```

## 📋 Proveedores Soportados

### Z.AI (智谱AI / GLM)

**Modelos disponibles:**
- `glm-5` - Modelo flagship (recomendado)
- `glm-4.6v` - Multimodal con visión

**Endpoints:**
- General: `https://api.z.ai/api/paas/v4`
- Coding: `https://api.z.ai/api/coding/paas/v4`

**Configuración:**
```bash
LLM_PROVIDER=zai
ZAI_API_KEY=your-api-key
ZAI_BASE_URL=https://api.z.ai/api/paas/v4
ZAI_MODEL=glm-5
```

**Obtener API key:** [Z.AI Open Platform](https://open.bigmodel.cn/usercenter/apikeys)

---

### Kimi (Moonshot AI)

**Modelos disponibles:**
- `kimi-k2` - Modelo principal
- `kimi-for-coding` - Optimizado para coding

**Endpoint:**
- `https://api.kimi.com/coding`

**Configuración:**
```bash
LLM_PROVIDER=kimi
KIMI_API_KEY=sk-kimi-your-key
KIMI_BASE_URL=https://api.kimi.com/coding
KIMI_MODEL=kimi-k2
```

**Compatibilidad:** Usa formato API Anthropic

**Obtener API key:** [Kimi Platform](https://platform.moonshot.cn/console/api-keys)

---

### MiniMax

**Modelos disponibles:**
- `MiniMax-M2.5` - Modelo principal

**Endpoints:**
- Internacional: `https://api.minimax.io/anthropic`
- China: `https://api.minimaxi.com/anthropic`

**Configuración:**
```bash
LLM_PROVIDER=minimax
MINIMAX_API_KEY=your-api-key
MINIMAX_BASE_URL=https://api.minimax.io/anthropic
MINIMAX_MODEL=MiniMax-M2.5
```

**Compatibilidad:** Usa formato API Anthropic

**Obtener API key:** [MiniMax Platform](https://www.minimaxi.com/platform/settings/api-keys)

---

### OpenAI

**Modelos disponibles:**
- `gpt-4o` - Modelo recomendado
- `gpt-4-turbo`
- `gpt-3.5-turbo`

**Configuración:**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o
```

**Obtener API key:** [OpenAI Platform](https://platform.openai.com/api-keys)

---

### Anthropic

**Modelos disponibles:**
- `claude-3-5-sonnet-20241022` - Recomendado
- `claude-3-opus-20240229`
- `claude-3-haiku-20240307`

**Configuración:**
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key
ANTHROPIC_BASE_URL=https://api.anthropic.com
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

**Obtener API key:** [Anthropic Console](https://console.anthropic.com/settings/keys)

---

### Ollama (Local)

**Modelos disponibles:**
- `llama3.1`
- `qwen`
- `mistral`
- Cualquier modelo de Ollama

**Configuración:**
```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.1
```

**Requisitos:** Tener Ollama instalado y ejecutándose localmente.

**Descargar:** [Ollama](https://ollama.com/download)

---

## 🔄 Cambio Entre Proveedores

### Después de Cambiar el Proveedor

Siempre reinicia TrustGraph para aplicar los cambios:

```bash
# Método 1 - Reinicio completo
make down && make up

# Método 2 - Reinicio rápido
docker compose restart

# Método 3 - Reinicio solo de servicios LLM
docker compose restart graph-rag doc-embeddings
```

### Verificar Configuración Actual

```bash
# Ver proveedor actual
make provider

# O directamente
grep LLM_PROVIDER .env
```

## 🛠️ Troubleshooting

### Error: "API key no válida"

1. Verifica que la API key esté en el formato correcto
2. Asegúrate de que la key no haya expirado
3. Confirma que tienes saldo/créditos en la plataforma

### Error: "No se puede conectar al endpoint"

1. Verifica tu conexión a internet
2. Si usas endpoint de China (Z.AI, Kimi, MiniMax), puede requerir VPN desde ciertos países
3. Verifica que el BASE_URL sea correcto

### Error: "Modelo no encontrado"

1. Verifica que el nombre del modelo sea exacto
2. Algunos modelos pueden tener diferentes nombres en la API vs la documentación

### Problemas con Ollama

1. Asegúrate de que Ollama esté ejecutándose: `ollama serve`
2. Verifica que el modelo esté descargado: `ollama pull llama3.1`
3. En Docker Desktop, usa `host.docker.internal` para conectar al host

## 💡 Mejores Prácticas

1. **Primera vez:** Usa `make makeenv` para configurar fácilmente
2. **Pruebas:** Comienza con proveedores que tengan free tier (Kimi, Z.AI)
3. **Producción:** Considera usar múltiples proveedores como fallback
4. **Costos:** Monitorea el uso en los dashboards de cada proveedor

## 📊 Comparación de Proveedores

| Proveedor | Latencia | Calidad | Precio | Contexto |
|-----------|----------|---------|--------|----------|
| OpenAI GPT-4o | Media | Alta | $$$ | 128K |
| Claude 3.5 | Media | Alta | $$$ | 200K |
| GLM-5 | Baja | Alta | $ | 128K |
| Kimi K2 | Baja | Alta | $ | 200K |
| MiniMax | Baja | Media | $ | 200K |
| Ollama | Muy baja | Variable | Gratis | Variable |

---

**¿Necesitas ayuda?** Usa `make provider` para ver el menú interactivo o consulta la documentación en `CLAUDE.md`.
