#!/usr/bin/env python3
"""
TrustGraph - MCP Server for Claude Code Integration
Expone TrustGraph como herramienta MCP para Claude Code

Uso:
    python mcp_server.py
    
Configuración en Claude Code:
    {
      "mcpServers": {
        "trustgraph": {
          "command": "python",
          "args": ["/path/to/trustgraph/scripts/mcp_server.py"]
        }
      }
    }
"""

import os
import sys
import json
import asyncio
from typing import Any, Dict, List, Optional
from pathlib import Path

# Agregar directorio padre al path para imports
sys.path.insert(0, str(Path(__file__).parent))

# Intentar importar SDK MCP
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Resource,
        Tool,
        TextContent,
        CallToolResult,
        ListToolsResult,
    )
    HAS_MCP = True
except ImportError:
    HAS_MCP = False
    print("⚠️  MCP SDK no instalado. Ejecuta: pip install mcp", file=sys.stderr)

# Configuración
TRUSTGRAPH_HOST = os.getenv("TRUSTGRAPH_HOST", "localhost")
TRUSTGRAPH_PORT = int(os.getenv("TRUSTGRAPH_PORT", "8080"))
CONTEXT_CORE_ID = os.getenv("CONTEXT_CORE_ID", "documentation")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "docs")


class TrustGraphMCPClient:
    """Cliente MCP para TrustGraph."""
    
    def __init__(self, host: str = TRUSTGRAPH_HOST, port: int = TRUSTGRAPH_PORT):
        self.base_url = f"http://{host}:{port}/api/v1"
        
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
                raise ImportError("Instala httpx o requests")
    
    async def health_check(self) -> bool:
        try:
            if self.use_httpx:
                response = await self.client.get(f"{self.base_url}/health", timeout=5.0)
            else:
                response = self.client.get(f"{self.base_url}/health", timeout=5.0)
            return response.status_code == 200
        except:
            return False
    
    async def graphrag_query(self, query: str, include_sources: bool = True) -> Dict[str, Any]:
        try:
            data = {
                "query": query,
                "context_core": CONTEXT_CORE_ID,
                "include_sources": include_sources,
            }
            
            if self.use_httpx:
                response = await self.client.post(
                    f"{self.base_url}/graphrag/query",
                    json=data,
                    timeout=60.0
                )
            else:
                response = self.client.post(
                    f"{self.base_url}/graphrag/query",
                    json=data,
                    timeout=60.0
                )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}", "answer": "Error en la consulta"}
        except Exception as e:
            return {"error": str(e), "answer": f"Error: {str(e)}"}
    
    async def vector_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        try:
            data = {
                "query": query,
                "collection": COLLECTION_NAME,
                "limit": limit,
            }
            
            if self.use_httpx:
                response = await self.client.post(
                    f"{self.base_url}/search/vector",
                    json=data,
                    timeout=30.0
                )
            else:
                response = self.client.post(
                    f"{self.base_url}/search/vector",
                    json=data,
                    timeout=30.0
                )
            
            if response.status_code == 200:
                return response.json().get("results", [])
            return []
        except Exception as e:
            return [{"error": str(e)}]
    
    async def get_context_graph(self, entity_id: Optional[str] = None, depth: int = 2) -> Dict[str, Any]:
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
            return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def close(self):
        if self.use_httpx:
            await self.client.aclose()


# Crear servidor MCP
if HAS_MCP:
    app = Server("trustgraph-memory")
    client = TrustGraphMCPClient()


    @app.list_resources()
    async def list_resources() -> List[Resource]:
        """Lista recursos disponibles."""
        return [
            Resource(
                uri="memory://documentation",
                name="Workspace Documentation",
                description="Documentación completa del workspace",
                mimeType="application/json",
            ),
            Resource(
                uri="memory://graph",
                name="Knowledge Graph",
                description="Grafo de conocimiento del workspace",
                mimeType="application/json",
            ),
            Resource(
                uri="memory://status",
                name="TrustGraph Status",
                description="Estado del servicio TrustGraph",
                mimeType="application/json",
            ),
        ]


    @app.read_resource()
    async def read_resource(uri: str) -> str:
        """Lee un recurso."""
        if uri == "memory://status":
            healthy = await client.health_check()
            return json.dumps({
                "status": "healthy" if healthy else "unhealthy",
                "host": TRUSTGRAPH_HOST,
                "port": TRUSTGRAPH_PORT,
                "context_core": CONTEXT_CORE_ID,
            }, indent=2)
        
        elif uri == "memory://graph":
            graph_data = await client.get_context_graph()
            return json.dumps(graph_data, indent=2)
        
        elif uri == "memory://documentation":
            return json.dumps({
                "description": "Workspace documentation knowledge base",
                "context_core": CONTEXT_CORE_ID,
                "collection": COLLECTION_NAME,
                "endpoints": {
                    "query": "/api/v1/graphrag/query",
                    "search": "/api/v1/search/vector",
                    "graph": f"/api/v1/cores/{CONTEXT_CORE_ID}/graph",
                }
            }, indent=2)
        
        else:
            raise ValueError(f"Recurso desconocido: {uri}")


    @app.list_tools()
    async def list_tools() -> List[Tool]:
        """Lista herramientas disponibles."""
        return [
            Tool(
                name="query_memory",
                description="Consulta la memoria usando GraphRAG. Pregunta sobre la documentación del workspace.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Pregunta o consulta en lenguaje natural",
                        },
                        "include_sources": {
                            "type": "boolean",
                            "description": "Incluir fuentes en la respuesta",
                            "default": True,
                        },
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="search_documents",
                description="Búsqueda vectorial semántica en documentos.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Términos de búsqueda",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Número máximo de resultados",
                            "default": 5,
                        },
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="get_context_graph",
                description="Obtiene el grafo de contexto para una entidad o todo el grafo.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "entity_id": {
                            "type": "string",
                            "description": "ID de la entidad (opcional)",
                        },
                        "depth": {
                            "type": "integer",
                            "description": "Profundidad de exploración",
                            "default": 2,
                        },
                    },
                },
            ),
            Tool(
                name="check_status",
                description="Verifica el estado de TrustGraph.",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
        ]


    @app.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Ejecuta una herramienta."""
        
        if name == "query_memory":
            query = arguments.get("query", "")
            include_sources = arguments.get("include_sources", True)
            
            result = await client.graphrag_query(query, include_sources)
            
            response_text = result.get("answer", "No se obtuvo respuesta")
            
            if include_sources and "sources" in result:
                sources = result["sources"]
                if sources:
                    response_text += "\n\n📚 Fuentes:\n"
                    for i, src in enumerate(sources[:5], 1):
                        response_text += f"{i}. {src.get('document', 'N/A')}\n"
            
            if "confidence" in result:
                response_text += f"\n📊 Confianza: {result['confidence']:.1%}"
            
            return [TextContent(type="text", text=response_text)]
        
        elif name == "search_documents":
            query = arguments.get("query", "")
            limit = arguments.get("limit", 5)
            
            results = await client.vector_search(query, limit)
            
            if not results:
                return [TextContent(type="text", text="No se encontraron resultados.")]
            
            response_text = f"🔍 Resultados ({len(results)}):\n\n"
            
            for i, r in enumerate(results, 1):
                score = r.get("score", 0)
                content = r.get("content", "")[:200]
                metadata = r.get("metadata", {})
                source = metadata.get("source", "Unknown")
                
                response_text += f"{i}. [{score:.0%}] {source}\n"
                response_text += f"   {content}...\n\n"
            
            return [TextContent(type="text", text=response_text)]
        
        elif name == "get_context_graph":
            entity_id = arguments.get("entity_id")
            depth = arguments.get("depth", 2)
            
            result = await client.get_context_graph(entity_id, depth)
            
            if "error" in result:
                return [TextContent(type="text", text=f"Error: {result['error']}")]
            
            entities = result.get("entities", [])
            relations = result.get("relations", [])
            
            response_text = f"🕸️ Grafo de Contexto\n\n"
            response_text += f"Entidades: {len(entities)}\n"
            response_text += f"Relaciones: {len(relations)}\n\n"
            
            if entities:
                response_text += "🏷️ Entidades principales:\n"
                for e in entities[:10]:
                    response_text += f"  - {e.get('id', 'N/A')} ({e.get('type', 'Unknown')})\n"
            
            return [TextContent(type="text", text=response_text)]
        
        elif name == "check_status":
            healthy = await client.health_check()
            
            status_text = "✅ TrustGraph está funcionando" if healthy else "❌ TrustGraph no responde"
            
            details = f"""
{status_text}

Configuración:
  Host: {TRUSTGRAPH_HOST}
  Port: {TRUSTGRAPH_PORT}
  Context Core: {CONTEXT_CORE_ID}
  Collection: {COLLECTION_NAME}

Endpoints:
  Workbench: http://localhost:8888
  API: http://localhost:8080
  Grafana: http://localhost:3000
"""
            return [TextContent(type="text", text=details)]
        
        else:
            raise ValueError(f"Herramienta desconocida: {name}")


    async def main():
        """Ejecuta el servidor MCP."""
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options(),
            )


    if __name__ == "__main__":
        if not HAS_MCP:
            print("❌ MCP SDK no está instalado")
            print("   Instala con: pip install mcp")
            sys.exit(1)
        
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("\n👋 Servidor detenido")
        finally:
            asyncio.run(client.close())

else:
    # Modo standalone sin MCP
    print("TrustGraph MCP Server")
    print("=====================")
    print("Este script requiere el SDK de MCP para funcionar como servidor.")
    print("")
    print("Instalación:")
    print("  pip install mcp")
    print("")
    print("Uso:")
    print("  python mcp_server.py")
    print("")
    print("Para probar la conexión, usa query_graphrag.py:")
    print("  python query_graphrag.py --interactive")
