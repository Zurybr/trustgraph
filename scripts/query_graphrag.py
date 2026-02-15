#!/usr/bin/env python3
"""
TrustGraph - GraphRAG Query Tool
Realiza consultas GraphRAG sobre la documentación del workspace

Uso:
    python query_graphrag.py "tu pregunta aquí"
    
Ejemplos:
    python query_graphrag.py "¿Qué es TrustGraph?"
    python query_graphrag.py "Explícame la arquitectura del sistema"
    python query_graphrag.py --search "cómo instalar"
"""

import os
import sys
import json
import argparse
import asyncio
from typing import List, Dict, Any, Optional

# Configuración
TRUSTGRAPH_HOST = os.getenv("TRUSTGRAPH_HOST", "localhost")
TRUSTGRAPH_PORT = int(os.getenv("TRUSTGRAPH_PORT", "8080"))
CONTEXT_CORE_ID = os.getenv("CONTEXT_CORE_ID", "documentation")


class GraphRAGQueryClient:
    """Cliente para consultas GraphRAG."""
    
    def __init__(self, host: str = TRUSTGRAPH_HOST, port: int = TRUSTGRAPH_PORT):
        self.base_url = f"http://{host}:{port}/api/v1"
        self.headers = {"Content-Type": "application/json"}
        
        try:
            import httpx
            self.client = httpx.AsyncClient(timeout=60.0)
            self.use_httpx = True
        except ImportError:
            try:
                import requests
                self.client = requests.Session()
                self.use_httpx = False
            except ImportError:
                print("❌ Instala httpx o requests: pip install httpx")
                sys.exit(1)
    
    async def health_check(self) -> bool:
        """Verifica que TrustGraph está funcionando."""
        try:
            if self.use_httpx:
                response = await self.client.get(
                    f"{self.base_url}/health",
                    timeout=5.0
                )
            else:
                response = self.client.get(
                    f"{self.base_url}/health",
                    timeout=5.0
                )
            return response.status_code == 200
        except Exception as e:
            return False
    
    async def graphrag_query(
        self,
        query: str,
        include_sources: bool = True,
        include_traces: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Realiza una consulta GraphRAG."""
        try:
            data = {
                "query": query,
                "context_core": CONTEXT_CORE_ID,
                "include_sources": include_sources,
                "include_traces": include_traces,
            }
            
            if self.use_httpx:
                response = await self.client.post(
                    f"{self.base_url}/graphrag/query",
                    json=data,
                    headers=self.headers,
                    timeout=60.0
                )
            else:
                response = self.client.post(
                    f"{self.base_url}/graphrag/query",
                    json=data,
                    headers=self.headers,
                    timeout=60.0
                )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error en consulta: {e}")
            return None
    
    async def vector_search(
        self,
        query: str,
        limit: int = 5,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Realiza búsqueda vectorial."""
        try:
            data = {
                "query": query,
                "collection": "docs",
                "limit": limit,
                "threshold": threshold,
            }
            
            if self.use_httpx:
                response = await self.client.post(
                    f"{self.base_url}/search/vector",
                    json=data,
                    headers=self.headers,
                    timeout=30.0
                )
            else:
                response = self.client.post(
                    f"{self.base_url}/search/vector",
                    json=data,
                    headers=self.headers,
                    timeout=30.0
                )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("results", [])
            else:
                return []
                
        except Exception as e:
            print(f"❌ Error en búsqueda: {e}")
            return []
    
    async def get_graph_data(
        self,
        entity_id: Optional[str] = None,
        depth: int = 2
    ) -> Optional[Dict[str, Any]]:
        """Obtiene datos del grafo de conocimiento."""
        try:
            params = {"depth": depth}
            if entity_id:
                params["entity_id"] = entity_id
            
            url = f"{self.base_url}/cores/{CONTEXT_CORE_ID}/graph"
            
            if self.use_httpx:
                response = await self.client.get(url, params=params, timeout=30.0)
            else:
                response = self.client.get(url, params=params, timeout=30.0)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error obteniendo grafo: {e}")
            return None
    
    async def list_cores(self) -> List[Dict[str, Any]]:
        """Lista los context cores disponibles."""
        try:
            if self.use_httpx:
                response = await self.client.get(f"{self.base_url}/cores", timeout=10.0)
            else:
                response = self.client.get(f"{self.base_url}/cores", timeout=10.0)
            
            if response.status_code == 200:
                return response.json().get("cores", [])
            else:
                return []
                
        except Exception as e:
            print(f"❌ Error listando cores: {e}")
            return []
    
    async def close(self):
        """Cierra la conexión."""
        if self.use_httpx:
            await self.client.aclose()


def format_response(response: Dict[str, Any], verbose: bool = False):
    """Formatea la respuesta para mostrar."""
    print("\n" + "=" * 70)
    print("🤖 RESPUESTA")
    print("=" * 70)
    
    if "answer" in response:
        print(f"\n{response['answer']}")
    
    if "confidence" in response:
        confidence = response["confidence"]
        bar_length = 20
        filled = int(confidence * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"\n📊 Confianza: [{bar}] {confidence:.1%}")
    
    if verbose and "sources" in response and response["sources"]:
        print("\n📚 Fuentes:")
        for i, source in enumerate(response["sources"][:5], 1):
            print(f"   {i}. {source.get('document', 'N/A')}")
            if "page" in source:
                print(f"      Página: {source['page']}")
            if "score" in source:
                print(f"      Score: {source['score']:.2%}")
    
    if verbose and "traces" in response and response["traces"]:
        print("\n🔍 Decision Traces:")
        for trace in response["traces"][:3]:
            print(f"   → {trace.get('step', 'N/A')}: {trace.get('description', 'N/A')}")
    
    print("\n" + "=" * 70)


def format_search_results(results: List[Dict[str, Any]]):
    """Formatea resultados de búsqueda."""
    print("\n" + "=" * 70)
    print(f"🔍 RESULTADOS DE BÚSQUEDA ({len(results)})")
    print("=" * 70)
    
    for i, result in enumerate(results, 1):
        score = result.get("score", 0)
        content = result.get("content", "")
        metadata = result.get("metadata", {})
        
        print(f"\n{i}. [{score:.1%}] {metadata.get('source', 'Unknown')}")
        print(f"   Categoría: {metadata.get('category', 'N/A')}")
        print(f"   {content[:200]}...")


def format_graph_data(data: Dict[str, Any]):
    """Formatea datos del grafo."""
    print("\n" + "=" * 70)
    print("🕸️ DATOS DEL GRAFO")
    print("=" * 70)
    
    entities = data.get("entities", [])
    relations = data.get("relations", [])
    
    print(f"\n📊 Estadísticas:")
    print(f"   Entidades: {len(entities)}")
    print(f"   Relaciones: {len(relations)}")
    
    if entities:
        print(f"\n🏷️ Tipos de entidades:")
        types = {}
        for e in entities:
            t = e.get("type", "Unknown")
            types[t] = types.get(t, 0) + 1
        for t, count in sorted(types.items(), key=lambda x: -x[1])[:10]:
            print(f"   - {t}: {count}")


async def interactive_mode(client: GraphRAGQueryClient):
    """Modo interactivo de consultas."""
    print("\n" + "=" * 70)
    print("💬 MODO INTERACTIVO")
    print("=" * 70)
    print("Escribe tus preguntas (o 'quit' para salir, 'help' para ayuda)\n")
    
    while True:
        try:
            query = input("❓ Pregunta: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ["quit", "exit", "q"]:
                print("👋 ¡Hasta luego!")
                break
            
            if query.lower() == "help":
                print("\nComandos disponibles:")
                print("  quit, exit, q  - Salir")
                print("  help           - Mostrar esta ayuda")
                print("  status         - Verificar estado de TrustGraph")
                print("  cores          - Listar context cores")
                print("\nO escribe cualquier pregunta sobre la documentación.\n")
                continue
            
            if query.lower() == "status":
                healthy = await client.health_check()
                print(f"\n{'✅' if healthy else '❌'} TrustGraph {'OK' if healthy else 'no responde'}\n")
                continue
            
            if query.lower() == "cores":
                cores = await client.list_cores()
                print(f"\n📦 Context Cores ({len(cores)}):")
                for core in cores:
                    print(f"   - {core.get('id', 'N/A')}: {core.get('name', 'N/A')}")
                print()
                continue
            
            # Realizar consulta GraphRAG
            print("\n⏳ Procesando...")
            response = await client.graphrag_query(query, include_sources=True)
            
            if response:
                format_response(response, verbose=True)
            else:
                print("\n❌ No se pudo obtener respuesta")
                
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except EOFError:
            break


async def main():
    parser = argparse.ArgumentParser(
        description="Consulta GraphRAG sobre la documentación del workspace",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s "¿Qué es TrustGraph?"
  %(prog)s --search "instalación"
  %(prog)s --graph --depth 3
  %(prog)s --interactive
        """
    )
    
    parser.add_argument(
        "query",
        nargs="?",
        help="Pregunta a realizar"
    )
    parser.add_argument(
        "--search",
        action="store_true",
        help="Usar búsqueda vectorial en lugar de GraphRAG"
    )
    parser.add_argument(
        "--graph",
        action="store_true",
        help="Obtener datos del grafo de conocimiento"
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=2,
        help="Profundidad para exploración del grafo (default: 2)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Límite de resultados (default: 5)"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Modo interactivo"
    )
    parser.add_argument(
        "--cores",
        action="store_true",
        help="Listar context cores disponibles"
    )
    
    args = parser.parse_args()
    
    # Verificar que hay algo que hacer
    if not any([args.query, args.graph, args.interactive, args.cores]):
        parser.print_help()
        return
    
    print("=" * 70)
    print("🔍 TrustGraph GraphRAG Query Tool")
    print("=" * 70)
    print(f"🔗 API: http://{TRUSTGRAPH_HOST}:{TRUSTGRAPH_PORT}")
    print(f"📦 Context Core: {CONTEXT_CORE_ID}")
    print("=" * 70)
    
    # Crear cliente
    client = GraphRAGQueryClient()
    
    # Verificar salud
    print("\n🔗 Verificando conexión...")
    healthy = await client.health_check()
    
    if not healthy:
        print("❌ TrustGraph no responde")
        print("   Asegúrate de que esté corriendo: docker compose up -d")
        return
    
    print("   ✅ TrustGraph OK")
    
    try:
        # Modo interactivo
        if args.interactive:
            await interactive_mode(client)
            return
        
        # Listar cores
        if args.cores:
            cores = await client.list_cores()
            print(f"\n📦 Context Cores disponibles ({len(cores)}):")
            for core in cores:
                print(f"   - {core.get('id', 'N/A')}: {core.get('name', 'N/A')}")
            return
        
        # Obtener datos del grafo
        if args.graph:
            data = await client.get_graph_data(depth=args.depth)
            if data:
                format_graph_data(data)
            else:
                print("\n❌ No se pudieron obtener datos del grafo")
            return
        
        # Búsqueda vectorial
        if args.search:
            print(f"\n🔍 Buscando: '{args.query}'")
            results = await client.vector_search(
                args.query,
                limit=args.limit
            )
            if results:
                format_search_results(results)
            else:
                print("\n❌ No se encontraron resultados")
            return
        
        # Consulta GraphRAG
        if args.query:
            print(f"\n❓ Pregunta: {args.query}")
            print("\n⏳ Procesando con GraphRAG...")
            
            response = await client.graphrag_query(
                args.query,
                include_sources=True,
                include_traces=True
            )
            
            if response:
                format_response(response, verbose=True)
            else:
                print("\n❌ No se pudo obtener respuesta")
    
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
