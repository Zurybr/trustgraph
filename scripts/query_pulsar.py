#!/usr/bin/env python3
"""
TrustGraph - GraphRAG Query Tool via Pulsar
Alternative client that uses Pulsar directly instead of HTTP API

Uso:
    python query_pulsar.py "tu pregunta aquí"
"""

import os
import sys
import json
import asyncio
from typing import Dict, Any, Optional
from pulsar import Client, AuthenticationToken
import time

# Configuración
PULSAR_HOST = os.getenv("PULSAR_HOST", "pulsar://localhost:6650")
PULSAR_API_KEY = os.getenv("PULSAR_API_KEY", None)
CONTEXT_CORE_ID = os.getenv("CONTEXT_CORE_ID", "documentation")
TIMEOUT = 120  # seconds


class PulsarGraphRAGClient:
    """Cliente Pulsar para GraphRAG queries."""

    def __init__(self, pulsar_host: str = PULSAR_HOST, pulsar_api_key: str = None):
        self.pulsar_host = pulsar_host

        # Crear cliente Pulsar
        if pulsar_api_key:
            self.client = Client(
                pulsar_host,
                authentication=AuthenticationToken(pulsar_api_key)
            )
        else:
            self.client = Client(pulsar_host)

        print(f"   🔗 Conectado a Pulsar: {pulsar_host}")

    def query(self, question: str, context_core: str = CONTEXT_CORE_ID) -> Dict[str, Any]:
        """Ejecuta una query GraphRAG."""
        request_id = f"req-{int(time.time() * 1000)}"

        # Crear mensaje de request
        request = {
            "query": question,
            "context_core": context_core,
            "request_id": request_id
        }

        # Productor para enviar request
        producer = self.client.create_producer(
            f"persistent://tg/request/graph-rag",
            send_timeout_millis=TIMEOUT * 1000
        )

        # Consumer para recibir respuesta
        consumer = self.client.subscribe(
            f"persistent://tg/response/{request_id}",
            subscription_name=f"query-client-{request_id}"
        )

        try:
            # Enviar request
            producer.send(json.dumps(request).encode('utf-8'))
            producer.flush()

            # Esperar respuesta
            msg = consumer.receive(timeout_millis=TIMEOUT * 1000)
            response = json.loads(msg.data().decode('utf-8'))
            consumer.acknowledge(msg)

            return response

        except Exception as e:
            return {"error": str(e), "query": question}

        finally:
            producer.close()
            consumer.close()

    def close(self):
        self.client.close()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python query_pulsar.py \"your question\"")
        sys.exit(1)

    question = " ".join(sys.argv[1:])

    print(f"\n🔍 Consultando: {question}")

    client = PulsarGraphRAGClient()

    try:
        result = client.query(question)

        if "error" in result:
            print(f"\n❌ Error: {result['error']}")
        else:
            print(f"\n✅ Respuesta:")
            print("-" * 50)
            print(result.get("result", result))
            print("-" * 50)

            if "sources" in result:
                print("\n📚 Fuentes:")
                for source in result["sources"]:
                    print(f"   - {source}")

    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(main())
