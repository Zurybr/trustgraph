# TrustGraph para Dummies 🧠

> Guía paso a paso para instalar y usar TrustGraph sin saber nada de nada.

---

## 📋 Tabla de Contenidos

1. [¿Qué es TrustGraph?](#qué-es-trustgraph)
2. [Instalar la Skill (Fácil)](#instalar-la-skill-fácil)
3. [Configurar TrustGraph](#configurar-trustgraph)
4. [Usar TrustGraph](#usar-trustgraph)
5. [Comandos Rápidos](#comandos-rápidos)
6. [Solución de Problemas](#solución-de-problemas)

---

## ¿Qué es TrustGraph?

Imagina que tienes **miles de notas, documentos y archivos** en tu computadora. Normalmente, cuando buscas algo, solo encuentras archivos que contienen las palabras exactas que escribiste.

**TrustGraph es diferente:**
- Entiende el **significado** de tus documentos
- Conecta ideas relacionadas (aunque usen palabras diferentes)
- Responde preguntas como si fuera un experto que leyó TODO

### Ejemplo:

| Búsqueda Normal | TrustGraph |
|-----------------|------------|
| Busca: "trustgraph" → Encuentra archivos con esa palabra | Pregunta: "¿Qué es TrustGraph?" → "Es un sistema de memoria que usa grafos de conocimiento para conectar documentación y mejorar la precisión de IA del 60% al 90%" |

---

## Instalar la Skill (Fácil)

### Paso 1: Buscar la Skill

```bash
# Buscar skills relacionadas con trustgraph
npx skills find trustgraph
```

Esto te mostrará una lista de skills disponibles. Busca algo como:
```
📦 trustgraph
   Sistema de memoria basado en grafos de conocimiento...
   Por: @tu-usuario
```

### Paso 2: Instalar la Skill

```bash
# Instalar la skill de TrustGraph
npx skills add tu-usuario/trustgraph
```

**Nota:** Reemplaza `tu-usuario` con el nombre de usuario donde se publique la skill (ej: `zurybr/trustgraph`).

### Paso 3: Verificar instalación

La skill se instala automáticamente en tu directorio de skills. Kimi ahora reconocerá comandos relacionados con TrustGraph.

---

## Configurar TrustGraph

### Requisitos previos

- Docker instalado ([Descargar Docker](https://www.docker.com/products/docker-desktop))
- Una API key de OpenAI ([Obtener aquí](https://platform.openai.com/api-keys))

### Paso 1: Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar el archivo .env
# Cambiar esta línea:
OPENAI_API_KEY=sk-tu-api-key-aqui
```

### Paso 2: Crear directorios necesarios

```bash
make setup
```

Esto crea carpetas donde TrustGraph guardará datos.

---

## Usar TrustGraph

### 1. Iniciar los servicios

```bash
make up
```

Verás algo como:
```
🚀 Iniciando TrustGraph...
✅ Servicios iniciados
⏳ Esperando a que estén listos...

📊 Servicios disponibles:
   Workbench: http://localhost:8888
   API:       http://localhost:8080
   Grafana:   http://localhost:3000
```

**Espera 1-2 minutos** a que todo arranque.

### 2. Cargar tus documentos

```bash
make load
```

Esto toma todos los archivos markdown de tu carpeta `documentation/` y los "aprende".

**Tip:** Puedes cargar cualquier carpeta:
```bash
python scripts/load_docs.py /ruta/a/tus/documentos
```

### 3. Hacer preguntas

#### Opción A: Modo interactivo (recomendado)

```bash
make query
```

Te abre un chat donde puedes preguntar cosas como:
- `¿Qué es TrustGraph?`
- `¿Cómo funciona el sistema de memoria?`
- `Explica la arquitectura`

#### Opción B: Una sola pregunta

```bash
make search QUERY="¿Qué es TrustGraph?"
```

#### Opción C: Interfaz web

Abre tu navegador en: **http://localhost:8888**

### 4. Detener cuando termines

```bash
make down
```

---

## Comandos Rápidos

### 🚀 Inicio rápido (una sola vez)
```bash
npx skills add tu-usuario/trustgraph   # Instalar skill
cp .env.example .env                   # Configurar
# Editar .env con tu API key
make setup                              # Preparar carpetas
```

### 📚 Uso diario
```bash
make up         # Encender
make load       # Cargar documentos
make query      # Preguntar cosas
make down       # Apagar
```

### 🔍 Solo búsquedas
```bash
make search QUERY="tema a buscar"
```

### 📊 Ver estado
```bash
make status     # ¿Qué está corriendo?
make health     # ¿Todo bien?
make logs       # Ver mensajes del sistema
```

### 🧹 Limpieza (⚠️ borra datos)
```bash
make clean      # Borrar TODO
make reset      # Reiniciar desde cero
```

---

## Solución de Problemas

### ❌ "make: command not found"

Instala Make:
```bash
# Mac
xcode-select --install

# Ubuntu/Debian
sudo apt-get install make

# Windows (Git Bash incluye make)
```

### ❌ "docker: command not found"

Instala Docker Desktop: https://www.docker.com/products/docker-desktop

### ❌ "API key error" o "Unauthorized"

1. Verifica tu API key:
```bash
cat .env | grep OPENAI
```

2. Asegúrate de que sea válida en: https://platform.openai.com/api-keys

3. Reinicia los servicios:
```bash
make down
make up
```

### ❌ "Port already in use" (Puerto ocupado)

Algun otro programa usa el puerto 8888:
```bash
# Encontrar quién lo usa
lsof -i :8888

# Matar el proceso (reemplaza <PID>)
kill -9 <PID>

# O simplemente reinicia tu computadora
```

### ❌ TrustGraph no responde

```bash
# Ver qué está pasando
make logs

# Reiniciar todo
make down
make up
```

### ❌ La búsqueda no encuentra nada

1. ¿Cargaste documentos?
```bash
make load
```

2. ¿Esperaste a que termine? (puede tardar varios minutos)

3. Verifica que hay documentos en `documentation/` o especifica otra ruta:
```bash
python scripts/load_docs.py /ruta/correcta
```

---

## 🎯 Ejemplo Completo

```bash
# 1. Instalar skill
npx skills add tu-usuario/trustgraph

# 2. Configurar
cd trustgraph
cp .env.example .env
# (editar .env con API key)

# 3. Preparar
make setup

# 4. Iniciar
make up

# 5. Cargar documentos
make load

# 6. Preguntar
make query
# > ¿Qué hace TrustGraph?

# 7. Apagar
make down
```

---

## 📚 Recursos Adicionales

- **Workbench UI**: http://localhost:8888 (interfaz web)
- **API Docs**: http://localhost:8080/api/v1/health
- **Monitoreo**: http://localhost:3000 (Grafana)

---

## 🤔 ¿Aún tienes dudas?

1. Revisa los logs: `make logs`
2. Verifica que Docker esté corriendo
3. Asegúrate de que el puerto 8888 esté libre
4. Confirma que tu API key sea válida

**¡Listo! Ahora tienes un segundo cerebro digital.** 🧠✨
