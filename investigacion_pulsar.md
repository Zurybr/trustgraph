# Investigación: Problema de Pulsar en TrustGraph

## Resumen Ejecutivo

El problema principal es que **el namespace `tg/config` no existe** en Pulsar. Todos los servicios de TrustGraph esperan este namespace para funcionar, pero nunca fue creado durante la inicialización.

---

## Síntomas Observados

| Síntoma | Causa Raíz |
|---------|------------|
| API devuelve 404 en `/api/v1/graphrag/query` | No puede conectarse a Pulsar |
| `TopicNotFound: Namespace not found` | Namespace `tg/config` no existe |
| `Timeout` y errores de conexión | Reintentos fallidos del consumidor |
| BookKeeper ledger error -10 | Probablemente ledger corrupto por namespace faltante |

---

## Análisis de Logs

### Logs del API Gateway
```
_pulsar.TopicNotFound: Pulsar error: TopicNotFound
2026-02-16 02:18:47.583 ERROR [...] Failed partition-metadata lookup req_id: 42 error: TopicNotFound msg: Namespace not found
```

### Logs de Pulsar
```
org.apache.pulsar.broker.web.RestException: Namespace not found
Namespace tg/config not found
```

---

## Estado de los Servicios

Todos los servicios están **UP** pero Pulsar no tiene la configuración necesaria:

```
tg-api-gateway   trustgraph/trustgraph-flow:1.8.19   Up 3 minutes
tg-cassandra    cassandra:4.1.4                     Up 3 minutes (healthy)
tg-pulsar       apachepulsar/pulsar:3.2.0            Up 3 minutes
tg-qdrant       qdrant/qdrant:v1.9.0                 Up 3 minutes (healthy)
```

---

## Causa Raíz

El namespace `tg/config` debe ser creado explícitamente en Pulsar antes de que los servicios intenten usarlo. La imagen de Pulsar en modo standalone no crea namespaces automáticamente.

---

## Solución Propuesta

### Opción 1: Crear Namespace Manualmente (Inmediata)

Ejecutar dentro del contenedor de Pulsar:

```bash
# Entrar al contenedor
docker exec -it tg-pulsar bin/pulsar-admin namespaces create tg/config

# Verificar
docker exec -it tg-pulsar bin/pulsar-admin namespaces list tg
```

### Opción 2: Script de Inicialización (Recomendada)

Crear un script que se ejecute antes de que los servicios arranquen:

```python
#!/usr/bin/env python3
"""Initialize Pulsar namespaces for TrustGraph"""

from pulsar import Client, AuthenticationToken
import os

PULSAR_HOST = os.getenv("PULSAR_HOST", "pulsar://localhost:6650")

def create_namespace():
    """Create required namespaces"""
    client = Client(PULSAR_HOST)
    admin = client.admin()

    # Create namespace if not exists
    namespaces = admin.namespaces().get_namespaces("tg")
    if "tg/config" not in namespaces:
        admin.namespaces().create_namespace("tg/config")
        print("Created namespace: tg/config")

    # Configure namespace
    admin.namespaces().set_persistence("tg/config", {
        "bookkeeperEnsemble": 1,
        "bookkeeperWriteQuorum": 1,
        "bookkeeperAckQuorum": 1,
        "managedLedgerMaxEntriesPerLedger": 50000,
        "managedLedgerMinLedgerRolloverTimeMinutes": 10
    })

    print("Namespace configured successfully")

if __name__ == "__main__":
    create_namespace()
```

### Opción 3: Agregar al docker-compose.yaml

Agregar un servicio de inicialización:

```yaml
services:
  pulsar:
    # ... config existente

  init-pulsar:
    image: apachepulsar/pulsar:3.2.0
    depends_on:
      - pulsar
    command: >
      bin/pulsar-admin namespaces create tg/config
    networks:
      - trustgraph-network
```

---

## Pasos Inmediatos para Resolver

1. **Crear el namespace**:
   ```bash
   docker exec -it tg-pulsar bin/pulsar-admin namespaces create tg/config
   ```

2. **Reiniciar los servicios**:
   ```bash
   docker compose restart api-gateway graph-rag doc-embeddings llm-gateway
   ```

3. **Verificar**:
   ```bash
   curl http://localhost:8080/api/v1/health
   ```

---

## Notas Adicionales

- El error BookKeeper "-10" (BKCode) típicamente significa `LedgerNotFound` o error de lectura - esto puede ser resultado de intentar acceder a un topic que nunca fue creado correctamente
- La solución permanente debería incluir un paso de inicialización en el proceso de setup
- Verificar que los topics necesarios también sean creados (`tg/config/config`, `tg/config/query`, etc.)

---

## Referencias

- [Pulsar Admin API - Namespaces](https://pulsar.apache.org/docs/admin-api-namespaces/)
- [Pulsar Python Client](https://pulsar.apache.org/docs/client-libraries-python/)

---

# Actualización: Investigación de Endpoints API

## Estado Actual (16 Feb 2026)

### Servicios Activos
```
tg-api-gateway      trustgraph/trustgraph-flow:1.8.19   Up
tg-cassandra       cassandra:4.1.4                      healthy
tg-pulsar          apachepulsar/pulsar:2.11.0           Up
tg-qdrant          qdrant/qdrant:v1.9.0                  healthy
tg-workbench       trustgraph/workbench-ui:latest        Up
tg-graph-rag       trustgraph/trustgraph-flow:1.8.19    Up
tg-doc-embeddings  trustgraph/trustgraph-flow:1.8.19    Up
tg-init            trustgraph/trustgraph-flow:1.8.19    Up
```

### Problema: Endpoints API Devuelven 404

**Endpoints probados:**
| Endpoint | Método | Resultado |
|----------|--------|-----------|
| `/api/v1/health` | GET | 405 Method Not Allowed |
| `/api/v1/health` | POST | 200 (pero con error de parsing) |
| `/api/v1/graphrag/query` | POST | 404 Not Found |
| `/graphrag/query` | POST | 404 Not Found |
| `/` | GET | 404 Not Found |
| `/docs` | GET | 404 Not Found |

### Análisis de Logs

El API Gateway se conecta correctamente a Pulsar ahora:
```
2026-02-16 02:42:00,507+0000 [pulsar-io-28-9] INFO  org.apache.pulsar.broker.service.ServerCnx - [/172.19.0.13:39416] Subscribing on topic persistent://tg/config/config
2026-02-16 02:42:00,508+0000 [pulsar-io-28-9] INFO  org.apache.bookkeeper.mledger.impl.ManagedCursorImpl - [tg/config/persistent/config] Cursor 0bdb9842-c00c-4cd0-8f11-4ace6c89ec5d recovered to position 67:-1
2026-02-16 02:42:00,515+0000 [bookkeeper-ml-scheduler-OrderedScheduler-0-0] INFO  org.apache.pulsar.broker.service.ServerCnx - [/172.19.0.13:39416] Created subscription on topic persistent://tg/config/config
```

** namespaces creados:**
```
tg/config
tg/default
tg/flow
tg/request
tg/response
```

### Hipótesis

1. **El API Gateway funciona pero los endpoints no están registrados correctamente** - Possible bug en trustgraph-flow:1.8.19
2. **Falta un paso de inicialización** - El servicio `tg-init` debería configurar los endpoints
3. **La ruta cambió** - Los endpoints pueden haber cambiado de `/api/v1/` a otro prefijo

### Pruebas Realizadas

```bash
# CLI trus
trus query "¿Qué es TrustGraph?"
# Error 404: Endpoint no encontrado

# Direct API
curl -X POST http://localhost:8080/api/v1/graphrag/query -d '{"query":"test"}'
# 404: Not Found
```

### Recomendaciones

1. **Verificar logs del servicio `tg-init`** - Puede tener información sobre la configuración de endpoints
2. **Revisar documentación de trustgraph-flow 1.8.19** - Buscar cambios en API
3. **Probar versiones anteriores** - Puede ser un bug conocido en esta versión
4. **Contactar soporte** - Si el problema persiste, reportar bug en el repo

---

# Estado Final: 16 Feb 2026

## ✅ Lo que Funciona

1. **Google Embeddings configurado:**
   - EMBEDDING_PROVIDER=google
   - GOOGLE_API_KEY configurado
   - EMBEDDING_MODEL=text-embedding-004

2. **Todos los servicios Docker corriendo:**
   - api-gateway, graph-rag, doc-embeddings, cassandra, pulsar, qdrant, etc.

3. **CLI corregida:**
   - check_connection ahora usa POST
   - Muestra estado de agentes

## ❌ Problema Remaining: API REST

**Causa raíz FINAL (confirmada):**
El endpoint `/api/v1/{kind}` en trustgraph-flow SOLO conecta con `global_dispatchers`:
- config, flow, librarian, knowledge, collection-management

Los `request_response_dispatchers` (graph-rag, document-rag, embeddings, etc.) **NO están expuestos via HTTP**.

**Código prueba (gateway/endpoint/manager.py):**
```python
self.endpoints = [
    VariableEndpoint(
        endpoint_path="/api/v1/{kind}",
        dispatcher=dispatcher_manager.dispatch_global_service(),  # SOLO global!
    ),
]
```

**Solución requerida:**
Para usar graph-rag via API REST, se necesita:
1. Crear un Flow que incluya graph-rag
2. Acceder via `/api/v1/flow/{flow}/service/{kind}`

## Workarounds Disponibles

1. **Workbench UI**: http://localhost:8888
2. **WebSocket**: ws://localhost:8080/api/v1/socket
3. **Directo a Pulsar**: Enviar a `persistent://tg/request/graph-rag`
