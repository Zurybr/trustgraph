#!/usr/bin/env python3
"""
TrustGraph - Document Loader for Workspace Documentation
Carga toda la documentación del workspace en TrustGraph

Uso:
    python load_docs.py [directorio_docs]
    
Ejemplos:
    python load_docs.py                    # Carga documentation/ por defecto
    python load_docs.py ../docs            # Carga directorio específico
    python load_docs.py --reset            # Limpia y recarga todo
"""

import os
import sys
import json
import argparse
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Configuración
TRUSTGRAPH_HOST = os.getenv("TRUSTGRAPH_HOST", "localhost")
TRUSTGRAPH_PORT = int(os.getenv("TRUSTGRAPH_PORT", "8080"))
CONTEXT_CORE_ID = os.getenv("CONTEXT_CORE_ID", "documentation")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "docs")

# Extensiones soportadas
SUPPORTED_EXTENSIONS = {".md", ".txt", ".rst", ".py", ".js", ".ts", ".json", ".yaml", ".yml", ".toml"}


def get_project_root() -> Path:
    """Obtiene la raíz del proyecto (directorio padre de trustgraph/)."""
    return Path(__file__).parent.parent.parent.resolve()


def discover_documents(docs_dir: Path) -> List[Path]:
    """Descubre todos los documentos en el directorio."""
    documents = []
    
    if not docs_dir.exists():
        print(f"❌ Directorio no encontrado: {docs_dir}")
        return documents
    
    for ext in SUPPORTED_EXTENSIONS:
        files = list(docs_dir.rglob(f"*{ext}"))
        documents.extend(files)
    
    # Excluir archivos no deseados
    excluded_patterns = [
        ".git",
        "__pycache__",
        "node_modules",
        ".venv",
        "venv",
        "*.pyc",
        ".pytest_cache",
        ".mypy_cache",
        "data/",  # Datos de TrustGraph
    ]
    
    filtered = []
    for doc in documents:
        should_exclude = any(pattern in str(doc) for pattern in excluded_patterns)
        if not should_exclude:
            filtered.append(doc)
    
    return sorted(filtered)


def read_document(doc_path: Path) -> Dict[str, Any]:
    """Lee un documento y extrae metadata."""
    try:
        content = doc_path.read_text(encoding="utf-8", errors="ignore")
        
        # Calcular estadísticas
        lines = content.splitlines()
        words = len(content.split())
        
        return {
            "path": str(doc_path.relative_to(get_project_root())),
            "absolute_path": str(doc_path),
            "filename": doc_path.name,
            "extension": doc_path.suffix,
            "content": content,
            "size_bytes": len(content.encode("utf-8")),
            "line_count": len(lines),
            "word_count": words,
            "category": categorize_document(doc_path),
            "modified_time": datetime.fromtimestamp(doc_path.stat().st_mtime).isoformat(),
        }
    except Exception as e:
        print(f"  ❌ Error leyendo {doc_path}: {e}")
        return None


def categorize_document(doc_path: Path) -> str:
    """Categoriza un documento según su ubicación y contenido."""
    path_str = str(doc_path).lower()
    
    if "trustgraph" in path_str:
        return "trustgraph"
    elif "documentation" in path_str or "/docs/" in path_str:
        return "documentation"
    elif "/api/" in path_str or "api." in path_str:
        return "api"
    elif "architecture" in path_str or "arquitectura" in path_str:
        return "architecture"
    elif "guide" in path_str or "guia" in path_str:
        return "guide"
    elif "research" in path_str:
        return "research"
    elif "ecosystem" in path_str:
        return "ecosystem"
    elif ".py" in path_str:
        return "python_code"
    elif ".js" in path_str or ".ts" in path_str:
        return "javascript_code"
    elif doc_path.suffix == ".md":
        return "markdown"
    elif doc_path.suffix == ".json":
        return "config"
    else:
        return "other"


class TrustGraphClient:
    """Cliente simple para la API de TrustGraph."""
    
    def __init__(self, host: str = TRUSTGRAPH_HOST, port: int = TRUSTGRAPH_PORT):
        self.base_url = f"http://{host}:{port}/api/v1"
        self.headers = {"Content-Type": "application/json"}
        
        # Intentar importar httpx o requests
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
            print(f"  ⚠️ Health check falló: {e}")
            return False
    
    async def create_context_core(self, core_id: str, name: str) -> bool:
        """Crea un context core si no existe."""
        try:
            data = {
                "id": core_id,
                "name": name,
                "description": f"Knowledge base for {name}",
            }
            
            if self.use_httpx:
                response = await self.client.post(
                    f"{self.base_url}/cores",
                    json=data,
                    headers=self.headers
                )
            else:
                response = self.client.post(
                    f"{self.base_url}/cores",
                    json=data,
                    headers=self.headers
                )
            
            if response.status_code in [200, 201]:
                print(f"  ✅ Context Core '{core_id}' creado")
                return True
            elif response.status_code == 409:
                print(f"  ℹ️ Context Core '{core_id}' ya existe")
                return True
            else:
                print(f"  ❌ Error creando core: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
    
    async def create_collection(self, name: str, description: str = "") -> bool:
        """Crea una colección para documentos."""
        try:
            data = {
                "name": name,
                "description": description or f"Collection {name}",
            }
            
            if self.use_httpx:
                response = await self.client.post(
                    f"{self.base_url}/collections",
                    json=data,
                    headers=self.headers
                )
            else:
                response = self.client.post(
                    f"{self.base_url}/collections",
                    json=data,
                    headers=self.headers
                )
            
            if response.status_code in [200, 201]:
                print(f"  ✅ Colección '{name}' creada")
                return True
            elif response.status_code == 409:
                print(f"  ℹ️ Colección '{name}' ya existe")
                return True
            else:
                print(f"  ⚠️ Error creando colección: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ⚠️ Error: {e}")
            return False
    
    async def ingest_document(self, document: Dict[str, Any]) -> bool:
        """Ingesta un documento en TrustGraph."""
        try:
            # Preparar datos para ingestión
            data = {
                "content": document["content"],
                "metadata": {
                    "source": document["path"],
                    "filename": document["filename"],
                    "category": document["category"],
                    "extension": document["extension"],
                    "line_count": document["line_count"],
                    "word_count": document["word_count"],
                    "modified_time": document["modified_time"],
                },
                "collection": COLLECTION_NAME,
                "context_core": CONTEXT_CORE_ID,
            }
            
            if self.use_httpx:
                response = await self.client.post(
                    f"{self.base_url}/documents/ingest",
                    json=data,
                    headers=self.headers,
                    timeout=120.0
                )
            else:
                response = self.client.post(
                    f"{self.base_url}/documents/ingest",
                    json=data,
                    headers=self.headers,
                    timeout=120.0
                )
            
            return response.status_code in [200, 201, 202]
            
        except Exception as e:
            print(f"  ❌ Error ingestando documento: {e}")
            return False
    
    async def close(self):
        """Cierra la conexión."""
        if self.use_httpx:
            await self.client.aclose()


async def main():
    parser = argparse.ArgumentParser(
        description="Carga documentación del workspace en TrustGraph"
    )
    parser.add_argument(
        "docs_dir",
        nargs="?",
        default="documentation",
        help="Directorio con documentación (default: documentation)"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Limpia el context core existente antes de cargar"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simula la carga sin enviar a TrustGraph"
    )
    parser.add_argument(
        "--category",
        help="Filtra por categoría específica"
    )
    
    args = parser.parse_args()
    
    # Resolver ruta
    project_root = get_project_root()
    docs_dir = project_root / args.docs_dir
    
    print("=" * 70)
    print("📚 TrustGraph Document Loader")
    print("=" * 70)
    print(f"📁 Proyecto: {project_root}")
    print(f"📂 Directorio: {docs_dir}")
    print(f"🎯 Context Core: {CONTEXT_CORE_ID}")
    print(f"📦 Colección: {COLLECTION_NAME}")
    print(f"🔗 API: http://{TRUSTGRAPH_HOST}:{TRUSTGRAPH_PORT}")
    print("=" * 70)
    
    # Descubrir documentos
    print("\n🔍 Descubriendo documentos...")
    documents = discover_documents(docs_dir)
    
    if args.category:
        documents = [d for d in documents if categorize_document(d) == args.category]
        print(f"   Filtrando por categoría: {args.category}")
    
    print(f"   Encontrados: {len(documents)} documentos")
    
    if not documents:
        print("❌ No se encontraron documentos")
        return
    
    # Leer documentos
    print("\n📖 Leyendo documentos...")
    docs_data = []
    for doc_path in documents:
        doc_data = read_document(doc_path)
        if doc_data:
            docs_data.append(doc_data)
    
    print(f"   Leídos: {len(docs_data)} documentos")
    
    # Mostrar resumen por categoría
    categories = {}
    for doc in docs_data:
        cat = doc["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\n📊 Distribución por categoría:")
    for cat, count in sorted(categories.items()):
        print(f"   - {cat}: {count}")
    
    # Modo dry-run
    if args.dry_run:
        print("\n🔍 MODO DRY-RUN - No se enviarán datos a TrustGraph")
        print("\n   Primeros 3 documentos:")
        for doc in docs_data[:3]:
            print(f"   - {doc['path']} ({doc['word_count']} palabras)")
        return
    
    # Conectar a TrustGraph
    print("\n🔗 Conectando a TrustGraph...")
    client = TrustGraphClient()
    
    # Verificar salud
    healthy = await client.health_check()
    if not healthy:
        print("❌ TrustGraph no responde")
        print("   Asegúrate de que esté corriendo: docker compose up -d")
        return
    
    print("   ✅ TrustGraph responde correctamente")
    
    # Crear context core
    print("\n🏗️ Configurando Context Core...")
    await client.create_context_core(
        CONTEXT_CORE_ID,
        "Workspace Documentation"
    )
    
    # Crear colección
    await client.create_collection(
        COLLECTION_NAME,
        "Documentos del workspace"
    )
    
    # Cargar documentos
    print(f"\n⬆️ Cargando {len(docs_data)} documentos...")
    successful = 0
    failed = 0
    
    for i, doc in enumerate(docs_data, 1):
        print(f"\n[{i}/{len(docs_data)}] {doc['path']}")
        print(f"   Categoría: {doc['category']} | Palabras: {doc['word_count']}")
        
        success = await client.ingest_document(doc)
        if success:
            successful += 1
            print("   ✅ Cargado")
        else:
            failed += 1
            print("   ❌ Falló")
    
    # Cerrar conexión
    await client.close()
    
    # Resumen final
    print("\n" + "=" * 70)
    print("📊 RESUMEN FINAL")
    print("=" * 70)
    print(f"   Total documentos: {len(docs_data)}")
    print(f"   Exitosos: {successful}")
    print(f"   Fallidos: {failed}")
    print(f"   Total palabras: {sum(d['word_count'] for d in docs_data)}")
    print("=" * 70)
    
    if successful > 0:
        print("\n✨ Documentación cargada exitosamente!")
        print(f"   Accede al Workbench: http://localhost:8888")
        print(f"   Realiza queries: http://localhost:8080/api/v1/graphrag/query")


if __name__ == "__main__":
    asyncio.run(main())
