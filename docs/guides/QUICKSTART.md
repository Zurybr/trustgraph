# 🚀 Guía de Inicio Rápido

## trustgraph en 5 minutos

### 1. Instalación

```bash
# Clonar o navegar al directorio
cd trustgraph

# Ejecutar setup interactivo
./setup.sh
```

### 2. Configuración Inicial

```bash
# Configurar proveedor LLM (global)
trus agentes config-global -p openai -k sk-tu-api-key

# O interactivo
trus agentes config-global
```

### 3. Iniciar Servicios

```bash
trus infra start
```

### 4. Indexar Contenido

```bash
# Proyecto completo
trus recordar proyecto

# O archivo específico
trus recordar archivo documento.md
```

### 5. Consultar

```bash
# Una pregunta
trus query "¿Qué es TrustGraph?"

# Modo interactivo
trus query -i
```

---

## Uso de Agentes

### 📚 Callímaco (Bibliotecario)

```bash
# Indexar con Callímaco
trus agente bibliotecario indexar archivo.md
trus agente bibliotecario indexar-dir ./docs
```

### 🔍 Sócrates (Investigador)

```bash
# Investigar
trus agente investigador pregunta "¿Cómo funciona X?"

# Modo interactivo
trus agente investigador pregunta -i
```

### 🌙 Morpheo (Mantenimiento)

```bash
# Ciclo manual
trus agente nocturno ciclo --intensidad normal

# Programar automático
trus agente nocturno programar --hora 02:00 --frecuencia semanal
```

---

## Configuración Avanzada

### Múltiples Proveedores

```bash
# Bibliotecario con Z.AI
trus agentes config-agente bibliotecario -p zai -k API_KEY_ZAI

# Investigador con OpenAI
trus agentes config-agente investigador -p openai -k API_KEY_OPENAI
```

### Ver Configuración

```bash
trus agentes show
```

---

## Solución de Problemas

```bash
# Ver estado
trus status

# Health check
trus infra health

# Ver logs
trus infra logs
```

---

## Próximos Pasos

- Lee la [Guía de Agentes](./agents/README.md)
- Configura [Proveedores](./providers/PROVIDER_SETUP.md)
- Explora la [Arquitectura](./agents/ARCHITECTURE.md)
