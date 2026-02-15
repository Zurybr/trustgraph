# TrustGraph CLI - `trus`

Interfaz de línea de comandos para TrustGraph - gestiona tu memoria de conocimiento desde cualquier terminal.

## 🚀 Instalación

### Desde el repositorio (recomendado):
```bash
./install/install-cli.sh
```

### Descarga directa (para agentes remotos):
```bash
curl -fsSL https://tu-dominio.com/install-cli.sh | bash
```

### Requisitos:
- Python 3.8+
- pip3
- (Opcional) TrustGraph server local o remoto

## 🔐 Primer Uso

### Configurar conexión:
```bash
# Instalación local (detecta automáticamente)
trus login

# Conectar a servidor remoto
trus login --host 192.168.1.100 --port 8080
```

### Verificar conexión:
```bash
trus status
```

## 📚 Comandos Principales

### `trus recordar` - Guardar e Indexar

```bash
# Indexar un archivo
trus recordar archivo documento.txt
trus recordar archivo codigo.py --categoria desarrollo

# Indexar un directorio
trus recordar directorio ./docs/
trus recordar directorio ./src/ --extensiones .py,.js

# Indexar proyecto completo
trus recordar proyecto
```

### `trus query` - Consultar Memoria

```bash
# Pregunta simple
trus query "¿Qué es TrustGraph?"
trus query "arquitectura del sistema" --fuentes

# Modo interactivo
trus query -i
```

### `trus config` - Configuración

```bash
# Ver configuración actual
trus config show

# Cambiar proveedor LLM
trus config provider zai
trus config provider kimi
trus config provider minimax

# Configurar API key
trus config apikey

# Cambiar modelo
trus config model glm-5
```

### `trus servicios` - Gestión Local

```bash
# Solo disponible en modo local
trus servicios start
trus servicios stop
trus servicios restart
trus servicios logs --seguir
```

## 🌐 Uso Remoto

### En el servidor (máquina con TrustGraph):
```bash
# Configurar acceso remoto
./install/setup-server.sh
```

### En el agente cliente (otra máquina):
```bash
# Instalar solo CLI
./install/install-cli.sh

# Configurar conexión al servidor
trus login --host IP_DEL_SERVIDOR --port 8080

# Verificar
trus status
```

## 🔧 Configuración Avanzada

El archivo de configuración se encuentra en:
- Linux/Mac: `~/.trustgraph/config.json`
- Windows: `%USERPROFILE%\.trustgraph\config.json`

Estructura:
```json
{
  "host": "localhost",
  "port": 8080,
  "api_gateway": "http://localhost:8080",
  "provider": "zai",
  "api_key": "sk-...",
  "model": "glm-5",
  "is_local": true,
  "auth_token": ""
}
```

## 📝 Ejemplos de Flujo de Trabajo

### Flujo 1: Desarrollo Local
```bash
# 1. Iniciar servidor
make up

# 2. Indexar código
make recordar RUTA=./src/

# 3. Consultar
make ask Q="¿cómo funciona el módulo X?"
```

### Flujo 2: Agente Remoto
```bash
# 1. Conectar a servidor
make login HOST=192.168.1.100

# 2. Indexar documentación local
trus recordar directorio ./docs/

# 3. Consultar memoria compartida
trus query "documentación del API"
```

### Flujo 3: Cambio de Proveedor
```bash
# Cambiar a Z.AI
trus config provider zai
trus config apikey
make down && make up
```

## 🛠️ Troubleshooting

### Error: "No hay conexión con TrustGraph"
- Verifica que TrustGraph esté ejecutándose: `make status`
- Verifica la configuración: `trus config show`
- Reconfigura: `trus login`

### Error: "API key inválida"
- Configura la API key: `trus config apikey`
- Verifica el proveedor: `trus config show`

### Error: "Comando no encontrado"
- Verifica instalación: `which trus`
- Reinstala si es necesario: `./install/install-cli.sh`

## 📖 Documentación Adicional

- [Guía de Proveedores](../docs/PROVIDER_SETUP.md)
- [README Principal](../README.md)
- [TrustGraph Skill](../trustgraph/SKILL.md)

## 🔗 Comandos Equivalentes

| Makefile | CLI | Script Python |
|----------|-----|---------------|
| `make up` | `trus servicios start` | `docker compose up -d` |
| `make down` | `trus servicios stop` | `docker compose down` |
| `make load` | `trus recordar directorio .` | `python scripts/load_docs.py` |
| `make query` | `trus query -i` | `python scripts/query_graphrag.py -i` |
| `make provider USE=zai` | `trus config provider zai` | - |

---

**Nota:** La CLI está diseñada para funcionar tanto con instalaciones locales como remotas de TrustGraph.
