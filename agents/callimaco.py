#!/usr/bin/env python3
"""
Callímaco (Καλλίμαχος) - El Bibliotecario de Alejandría Digital

El bibliotecario griego que organiza, estructura y cataloga el conocimiento.
Sabe exactamente qué información va a qué base de datos (Cassandra vs Qdrant),
cómo etiquetarla y cómo mantener la integridad del grafo de conocimiento.

Responsabilidades:
- Clasificación semántica de contenido
- Extracción de entidades y relaciones
- Decisión de almacenamiento (Grafo vs Vector)
- Etiquetado jerárquico y semántico
- Validación de calidad del conocimiento
"""

import os
import json
import hashlib
from typing import Dict, List, Any, Optional, Literal
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, END


class ContentType(Enum):
    """Tipos de contenido que Callímaco puede procesar"""
    DOCUMENTO = "documento"
    CONVERSACION = "conversacion"
    CODIGO = "codigo"
    IMAGEN = "imagen"
    VIDEO = "video"
    AUDIO = "audio"
    NOTA_RAPIDA = "nota_rapida"
    REFERENCIA = "referencia"


class StorageDestination(Enum):
    """Destinos de almacenamiento posibles"""
    GRAFO_Y_VECTOR = "grafo_y_vector"  # Ambos: tiene entidades + contenido semántico
    SOLO_VECTOR = "solo_vector"        # Solo Qdrant: contenido semántico puro
    SOLO_GRAFO = "solo_grafo"          # Solo Cassandra: relaciones puras
    METADATA = "metadata"              # Solo metadatos índice


@dataclass
class Entity:
    """Entidad extraída del contenido"""
    id: str
    name: str
    type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0


@dataclass
class Relation:
    """Relación entre entidades"""
    source: str
    target: str
    type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0


@dataclass
class SemanticTags:
    """Etiquetas semánticas jerárquicas"""
    categoria_primaria: str
    subcategorias: List[str] = field(default_factory=list)
    temas: List[str] = field(default_factory=list)
    entidades_clave: List[str] = field(default_factory=list)
    temporalidad: Optional[str] = None
    complejidad: Literal["baja", "media", "alta", "experta"] = "media"
    audiencia: Literal["general", "tecnica", "especializada", "ejecutiva"] = "general"


@dataclass
class StoragePlan:
    """Plan de almacenamiento generado por Callímaco"""
    destination: StorageDestination
    cassandra_ops: List[Dict[str, Any]] = field(default_factory=list)
    qdrant_ops: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""


@dataclass
class CallimacoState:
    """Estado del agente Callímaco"""
    # Entrada
    content: str = ""
    content_type: ContentType = ContentType.DOCUMENTO
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Procesamiento
    content_hash: str = ""
    entities: List[Entity] = field(default_factory=list)
    relations: List[Relation] = field(default_factory=list)
    semantic_tags: Optional[SemanticTags] = None
    summary: str = ""

    # Salida
    storage_plan: Optional[StoragePlan] = None
    execution_result: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    # Control
    current_step: str = "inicio"
    retry_count: int = 0
    max_retries: int = 3


class CallimacoAgent:
    """
    Agente Callímaco - El maestro bibliotecario digital

    Flujo de trabajo:
    1. CLASIFICAR → Determina tipo de contenido y complejidad
    2. EXTRAER → Identifica entidades y relaciones
    3. ETIQUETAR → Genera etiquetas semánticas jerárquicas
    4. PLANIFICAR → Decide estrategia de almacenamiento
    5. VALIDAR → Verifica calidad e integridad
    6. ALMACENAR → Ejecuta operaciones de persistencia
    """

    def __init__(self, llm=None, api_gateway: str = "http://localhost:8080", llm_config: dict = None):
        self.llm = llm
        self.api_gateway = api_gateway

        # Configuración de LLM (provider, api_key, model)
        self.llm_config = llm_config or {}

        self.graph = self._build_graph()

        # Prompts del sistema
        self._system_clasificador = """Eres Callímaco de Alejandría, el bibliotecario supremo.
Tu misión es clasificar contenido con precisión enciclopédica.

Analiza el contenido y determina:
1. Tipo de contenido (documento, conversación, código, etc.)
2. Complejidad (baja, media, alta, experta)
3. Audiencia objetivo (general, técnica, especializada, ejecutiva)
4. Temas principales (máximo 5)

Responde en JSON:
{
    "tipo_contenido": "...",
    "complejidad": "...",
    "audiencia": "...",
    "temas_principales": ["..."],
    "resumen_ejecutivo": "...",
    "palabras_clave": ["..."]
}"""

        self._system_extractor = """Eres Callímaco, maestro en extracción de conocimiento.
Extrae entidades y relaciones del contenido como si catalogaras los pergaminos de Alejandría.

Para ENTIDADES, identifica:
- Personas, organizaciones, lugares, conceptos, tecnologías, productos
- Propiedades relevantes de cada entidad

Para RELACIONES, identifica:
- Conexiones entre entidades (usa, crea, pertenece, etc.)
- Direccionalidad y propiedades

Responde en JSON:
{
    "entidades": [
        {"nombre": "...", "tipo": "...", "propiedades": {...}}
    ],
    "relaciones": [
        {"origen": "...", "destino": "...", "tipo": "...", "propiedades": {...}}
    ],
    "razonamiento": "..."
}"""

        self._system_etiquetador = """Eres Callímaco, creador del sistema de catalogación perfecto.
Genera etiquetas semánticas jerárquicas para máxima recuperabilidad.

Estructura jerárquica:
- Categoría primaria: el dominio fundamental
- Subcategorías: especializaciones (2-4)
- Temas: conceptos específicos (3-7)
- Entidades clave: nombres propios mencionados
- Temporalidad: época/relevancia temporal si aplica

Responde en JSON:
{
    "categoria_primaria": "...",
    "subcategorias": ["..."],
    "temas": ["..."],
    "entidades_clave": ["..."],
    "temporalidad": "...",
    "tags_tecnicos": ["..."],
    "tags_domain": ["..."]
}"""

        self._system_planificador = """Eres Callímaco, arquitecto del almacenamiento del conocimiento.
Decide la estrategia óptima de persistencia.

Bases disponibles:
- Cassandra (Grafo): Para entidades, relaciones, estructura
- Qdrant (Vector): Para contenido semántico, búsqueda por similitud

Decisiones:
- GRAFO_Y_VECTOR: Contenido rico en entidades y contexto
- SOLO_VECTOR: Texto semántico sin estructura compleja
- SOLO_GRAFO: Relaciones puras, metadatos de conexión
- METADATA: Solo índice, referencias externas

Responde en JSON:
{
    "destino": "grafo_y_vector|solo_vector|solo_grafo|metadata",
    "razonamiento": "...",
    "operaciones_cassandra": [...],
    "operaciones_qdrant": [...],
    "prioridad": "alta|media|baja"
}"""

    def _build_graph(self) -> StateGraph:
        """Construye el grafo de estados de Callímaco"""

        workflow = StateGraph(CallimacoState)

        # Nodos del flujo
        workflow.add_node("clasificar", self._node_clasificar)
        workflow.add_node("extraer", self._node_extraer)
        workflow.add_node("etiquetar", self._node_etiquetar)
        workflow.add_node("planificar", self._node_planificar)
        workflow.add_node("validar", self._node_validar)
        workflow.add_node("almacenar", self._node_almacenar)
        workflow.add_node("manejar_error", self._node_manejar_error)

        # Flujo condicional
        workflow.set_entry_point("clasificar")

        workflow.add_conditional_edges(
            "clasificar",
            self._decision_clasificacion,
            {
                "continuar": "extraer",
                "error": "manejar_error"
            }
        )

        workflow.add_conditional_edges(
            "extraer",
            self._decision_extraccion,
            {
                "continuar": "etiquetar",
                "saltar": "planificar",  # Para contenido sin entidades
                "error": "manejar_error"
            }
        )

        workflow.add_edge("etiquetar", "planificar")

        workflow.add_conditional_edges(
            "planificar",
            self._decision_planificacion,
            {
                "validar": "validar",
                "error": "manejar_error"
            }
        )

        workflow.add_conditional_edges(
            "validar",
            self._decision_validacion,
            {
                "almacenar": "almacenar",
                "reintentar": "extraer",
                "error": "manejar_error"
            }
        )

        workflow.add_conditional_edges(
            "almacenar",
            self._decision_final,
            {
                "completado": END,
                "error": "manejar_error"
            }
        )

        workflow.add_conditional_edges(
            "manejar_error",
            self._decision_reintento,
            {
                "reintentar": "clasificar",
                "abortar": END
            }
        )

        return workflow.compile()

    # ═══════════════════════════════════════════════════════════════
    # NODOS DEL GRAFO
    # ═══════════════════════════════════════════════════════════════

    def _node_clasificar(self, state: CallimacoState) -> CallimacoState:
        """Clasifica el contenido y genera metadatos iniciales"""
        state.current_step = "clasificar"

        # Generar hash único del contenido
        state.content_hash = hashlib.sha256(
            state.content.encode('utf-8')
        ).hexdigest()[:16]

        if not self.llm:
            # Clasificación heurística si no hay LLM
            state.semantic_tags = self._clasificacion_heuristica(state)
            return state

        try:
            messages = [
                SystemMessage(content=self._system_clasificador),
                HumanMessage(content=f"""
Contenido a clasificar:
---
Tipo declarado: {state.content_type.value}
Fuente: {state.source}
---
{state.content[:4000]}
---
                """)
            ]

            response = self.llm.invoke(messages)
            resultado = json.loads(response.content)

            state.semantic_tags = SemanticTags(
                categoria_primaria=resultado.get("temas_principales", ["general"])[0],
                temas=resultado.get("temas_principales", []),
                complejidad=resultado.get("complejidad", "media"),
                audiencia=resultado.get("audiencia", "general")
            )
            state.summary = resultado.get("resumen_ejecutivo", "")

        except Exception as e:
            state.errors.append(f"Error en clasificación: {str(e)}")

        return state

    def _node_extraer(self, state: CallimacoState) -> CallimacoState:
        """Extrae entidades y relaciones del contenido"""
        state.current_step = "extraer"

        # Contenido muy corto o sin estructura: saltar extracción
        if len(state.content) < 100:
            return state

        if not self.llm:
            state.entities, state.relations = self._extraccion_heuristica(state)
            return state

        try:
            messages = [
                SystemMessage(content=self._system_extractor),
                HumanMessage(content=f"""
Extrae entidades y relaciones del siguiente contenido:

{state.content[:6000]}

Instrucciones:
1. Identifica todas las entidades nombradas (personas, organizaciones, lugares, conceptos técnicos)
2. Establece relaciones entre ellas usando verbos descriptivos
3. Asigna confianza basada en claridad del contexto
                """)
            ]

            response = self.llm.invoke(messages)
            resultado = json.loads(response.content)

            # Convertir a objetos Entity
            for e in resultado.get("entidades", []):
                entity_id = hashlib.md5(
                    f"{e['nombre']}:{e['tipo']}".encode()
                ).hexdigest()[:12]

                state.entities.append(Entity(
                    id=entity_id,
                    name=e["nombre"],
                    type=e["tipo"],
                    properties=e.get("propiedades", {}),
                    confidence=e.get("confianza", 0.8)
                ))

            # Convertir a objetos Relation
            for r in resultado.get("relaciones", []):
                state.relations.append(Relation(
                    source=r["origen"],
                    target=r["destino"],
                    type=r["tipo"],
                    properties=r.get("propiedades", {}),
                    confidence=r.get("confianza", 0.8)
                ))

        except Exception as e:
            state.errors.append(f"Error en extracción: {str(e)}")

        return state

    def _node_etiquetar(self, state: CallimacoState) -> CallimacoState:
        """Genera etiquetas semánticas jerárquicas"""
        state.current_step = "etiquetar"

        if not self.llm:
            state.semantic_tags = self._etiquetado_heuristico(state)
            return state

        try:
            messages = [
                SystemMessage(content=self._system_etiquetador),
                HumanMessage(content=f"""
Genera etiquetas para:

Resumen: {state.summary}
Entidades detectadas: {[e.name for e in state.entities[:10]]}
Tipo: {state.content_type.value}

Contenido (primeros 3000 chars):
{state.content[:3000]}
                """)
            ]

            response = self.llm.invoke(messages)
            resultado = json.loads(response.content)

            state.semantic_tags = SemanticTags(
                categoria_primaria=resultado.get("categoria_primaria", "general"),
                subcategorias=resultado.get("subcategorias", []),
                temas=resultado.get("temas", []),
                entidades_clave=resultado.get("entidades_clave", []),
                temporalidad=resultado.get("temporalidad"),
                complejidad=state.semantic_tags.complejidad if state.semantic_tags else "media",
                audiencia=state.semantic_tags.audiencia if state.semantic_tags else "general"
            )

        except Exception as e:
            state.errors.append(f"Error en etiquetado: {str(e)}")

        return state

    def _node_planificar(self, state: CallimacoState) -> CallimacoState:
        """Genera plan de almacenamiento"""
        state.current_step = "planificar"

        # Decisión basada en contenido
        tiene_entidades = len(state.entities) > 0
        es_largo = len(state.content) > 200
        tiene_estructura = state.content_type in [
            ContentType.DOCUMENTO, ContentType.CONVERSACION, ContentType.CODIGO
        ]

        # Determinar destino
        if tiene_entidades and es_largo:
            destino = StorageDestination.GRAFO_Y_VECTOR
        elif tiene_entidades and not es_largo:
            destino = StorageDestination.SOLO_GRAFO
        elif es_largo and tiene_estructura:
            destino = StorageDestination.SOLO_VECTOR
        else:
            destino = StorageDestination.METADATA

        # Generar operaciones
        cassandra_ops = []
        qdrant_ops = []

        if destino in [StorageDestination.GRAFO_Y_VECTOR, StorageDestination.SOLO_GRAFO]:
            # Operaciones para Cassandra
            for entity in state.entities:
                cassandra_ops.append({
                    "operation": "upsert_entity",
                    "entity_id": entity.id,
                    "name": entity.name,
                    "type": entity.type,
                    "properties": entity.properties
                })

            for relation in state.relations:
                cassandra_ops.append({
                    "operation": "create_relation",
                    "source": relation.source,
                    "target": relation.target,
                    "relation_type": relation.type,
                    "properties": relation.properties
                })

        if destino in [StorageDestination.GRAFO_Y_VECTOR, StorageDestination.SOLO_VECTOR]:
            # Operaciones para Qdrant
            chunks = self._chunk_content(state.content)
            for i, chunk in enumerate(chunks):
                qdrant_ops.append({
                    "operation": "upsert_vector",
                    "id": f"{state.content_hash}_{i}",
                    "content": chunk,
                    "metadata": {
                        "source": state.source,
                        "content_type": state.content_type.value,
                        "tags": state.semantic_tags.__dict__ if state.semantic_tags else {},
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    }
                })

        state.storage_plan = StoragePlan(
            destination=destino,
            cassandra_ops=cassandra_ops,
            qdrant_ops=qdrant_ops,
            metadata={
                "content_hash": state.content_hash,
                "timestamp": datetime.now().isoformat(),
                "entity_count": len(state.entities),
                "relation_count": len(state.relations),
                "tags": state.semantic_tags.__dict__ if state.semantic_tags else {}
            },
            reasoning=f"Contenido tipo {state.content_type.value} con {len(state.entities)} entidades y {len(state.content)} caracteres"
        )

        return state

    def _node_validar(self, state: CallimacoState) -> CallimacoState:
        """Valida la calidad del plan de almacenamiento"""
        state.current_step = "validar"

        plan = state.storage_plan
        errores = []

        # Validaciones
        if not plan:
            errores.append("No hay plan de almacenamiento")
        else:
            if plan.destination == StorageDestination.GRAFO_Y_VECTOR:
                if len(plan.cassandra_ops) == 0:
                    errores.append("Destino grafo+vector pero no hay ops de Cassandra")
                if len(plan.qdrant_ops) == 0:
                    errores.append("Destino grafo+vector pero no hay ops de Qdrant")

            # Validar duplicados potenciales
            entity_names = [e.name for e in state.entities]
            if len(entity_names) != len(set(entity_names)):
                errores.append("Posibles entidades duplicadas")

        state.errors.extend(errores)
        return state

    def _node_almacenar(self, state: CallimacoState) -> CallimacoState:
        """Ejecuta operaciones de almacenamiento"""
        state.current_step = "almacenar"

        if not state.storage_plan:
            state.errors.append("No hay plan para ejecutar")
            return state

        # Aquí se conectaría con la API de TrustGraph
        # Por ahora simulamos el resultado
        resultado = {
            "success": True,
            "cassandra": {
                "entities_written": len(state.storage_plan.cassandra_ops),
                "relations_written": len([op for op in state.storage_plan.cassandra_ops if op["operation"] == "create_relation"])
            },
            "qdrant": {
                "vectors_written": len(state.storage_plan.qdrant_ops),
                "chunks_created": len(state.storage_plan.qdrant_ops)
            },
            "metadata": state.storage_plan.metadata
        }

        state.execution_result = resultado
        return state

    def _node_manejar_error(self, state: CallimacoState) -> CallimacoState:
        """Maneja errores y decide si reintentar"""
        state.current_step = "error"
        state.retry_count += 1
        return state

    # ═══════════════════════════════════════════════════════════════
    # DECISIONES CONDICIONALES
    # ═══════════════════════════════════════════════════════════════

    def _decision_clasificacion(self, state: CallimacoState) -> str:
        if state.errors and state.retry_count < state.max_retries:
            return "error"
        return "continuar"

    def _decision_extraccion(self, state: CallimacoState) -> str:
        if state.errors and state.retry_count >= state.max_retries:
            return "error"
        # Saltar si no hay suficiente contenido para entidades
        if len(state.content) < 50:
            return "saltar"
        return "continuar"

    def _decision_planificacion(self, state: CallimacoState) -> str:
        if state.errors:
            return "error"
        return "validar"

    def _decision_validacion(self, state: CallimacoState) -> str:
        if not state.errors:
            return "almacenar"
        if state.retry_count < state.max_retries:
            return "reintentar"
        return "error"

    def _decision_final(self, state: CallimacoState) -> str:
        if state.execution_result.get("success"):
            return "completado"
        return "error"

    def _decision_reintento(self, state: CallimacoState) -> str:
        if state.retry_count < state.max_retries:
            return "reintentar"
        return "abortar"

    # ═══════════════════════════════════════════════════════════════
    # MÉTODOS AUXILIARES
    # ═══════════════════════════════════════════════════════════════

    def _clasificacion_heuristica(self, state: CallimacoState) -> SemanticTags:
        """Clasificación sin LLM basada en reglas"""
        content_lower = state.content.lower()

        # Detectar temas por palabras clave
        temas = []
        if any(w in content_lower for w in ["código", "function", "class", "def", "import"]):
            temas.append("programación")
        if any(w in content_lower for w in ["docker", "kubernetes", "deploy", "infra"]):
            temas.append("devops")
        if any(w in content_lower for w in ["modelo", "ai", "ml", "neural", "training"]):
            temas.append("inteligencia_artificial")

        if not temas:
            temas = ["documentación_general"]

        return SemanticTags(
            categoria_primaria=temas[0],
            temas=temas,
            complejidad="media",
            audiencia="general"
        )

    def _extraccion_heuristica(self, state: CallimacoState) -> tuple:
        """Extracción de entidades sin LLM"""
        import re

        entities = []
        relations = []

        # Extraer posibles nombres propios (simplificado)
        palabras_caps = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', state.content)

        for i, nombre in enumerate(set(palabras_caps[:10])):
            entities.append(Entity(
                id=f"heur_{i}",
                name=nombre,
                type="concepto",
                confidence=0.5
            ))

        return entities, relations

    def _etiquetado_heuristico(self, state: CallimacoState) -> SemanticTags:
        """Etiquetado sin LLM"""
        return self._clasificacion_heuristica(state)

    def _chunk_content(self, content: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Divide contenido en chunks para vectores"""
        if len(content) <= chunk_size:
            return [content]

        chunks = []
        start = 0
        while start < len(content):
            end = start + chunk_size
            chunk = content[start:end]

            # Intentar cortar en final de oración
            if end < len(content):
                last_period = chunk.rfind('. ')
                if last_period > chunk_size * 0.5:
                    end = start + last_period + 1
                    chunk = content[start:end]

            chunks.append(chunk)
            start = end - overlap

        return chunks

    # ═══════════════════════════════════════════════════════════════
    # API PÚBLICA
    # ═══════════════════════════════════════════════════════════════

    async def indexar(
        self,
        content: str,
        content_type: ContentType = ContentType.DOCUMENTO,
        source: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Indexa contenido en TrustGraph usando el flujo completo de Callímaco

        Args:
            content: Contenido a indexar
            content_type: Tipo de contenido
            source: Fuente/original del contenido
            metadata: Metadatos adicionales

        Returns:
            Resultado de la indexación con plan y estadísticas
        """
        initial_state = CallimacoState(
            content=content,
            content_type=content_type,
            source=source,
            metadata=metadata or {}
        )

        # Ejecutar grafo
        result = await self.graph.ainvoke(initial_state)

        return {
            "success": len(result.errors) == 0,
            "content_hash": result.content_hash,
            "entities_extracted": len(result.entities),
            "relations_extracted": len(result.relations),
            "storage_plan": {
                "destination": result.storage_plan.destination.value if result.storage_plan else None,
                "cassandra_ops": len(result.storage_plan.cassandra_ops) if result.storage_plan else 0,
                "qdrant_ops": len(result.storage_plan.qdrant_ops) if result.storage_plan else 0,
            },
            "semantic_tags": result.semantic_tags.__dict__ if result.semantic_tags else {},
            "execution_result": result.execution_result,
            "errors": result.errors
        }

    def indexar_sync(
        self,
        content: str,
        content_type: ContentType = ContentType.DOCUMENTO,
        source: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Versión síncrona de indexar"""
        return asyncio.run(self.indexar(content, content_type, source, metadata))


# ═══════════════════════════════════════════════════════════════
# CLI INTERFAZ
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python callimaco.py <archivo> [tipo]")
        sys.exit(1)

    file_path = sys.argv[1]
    content_type = sys.argv[2] if len(sys.argv) > 2 else "documento"

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    agent = CallimacoAgent()
    result = agent.indexar_sync(
        content=content,
        content_type=ContentType(content_type),
        source=file_path
    )

    print(json.dumps(result, indent=2, default=str))
