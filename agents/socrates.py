#!/usr/bin/env python3
"""
Sócrates (Σωκράτης) - El Investigador Dialéctico

El filósofo que pregunta, divide y conquista el conocimiento.
Recibe un prompt complejo y lo descompone en sub-consultas estratégicas,
basándose en la organización que Callímaco ha creado.

Responsabilidades:
- Análisis de intención del usuario
- Descomposición de queries complejas
- Estrategia de búsqueda (vector vs grafo vs híbrida)
- Generación de punteros precisos (no contenido completo)
- Síntesis de hallazgos en respuesta coherente

Filosofía: "Solo sé que no sé nada, pero sé exactamente dónde buscar"
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional, Literal
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END


class QueryType(Enum):
    """Tipos de consulta que Sócrates puede manejar"""
    FACTUAL = "factual"           # Búsqueda de hechos específicos
    EXPLORATORIA = "exploratoria" # Descubrimiento de conexiones
    ANALITICA = "analitica"       # Análisis profundo de temas
    COMPARATIVA = "comparativa"   # Comparación de entidades
    PROCEDURAL = "procedural"     # Cómo hacer algo
    TEMPORAL = "temporal"         # Eventos en el tiempo


class SearchStrategy(Enum):
    """Estrategias de búsqueda disponibles"""
    VECTOR_PURO = "vector_puro"           # Solo similitud semántica
    GRAFO_PURO = "grafo_puro"             # Solo navegación de grafo
    GRAFO_RAG = "grafo_rag"               # GraphRAG completo
    HIBRIDO = "hibrido"                   # Vector + Grafo combinado
    ENTIDAD_PRIMERO = "entidad_primero"   # Buscar entidad luego expandir


@dataclass
class SubQuery:
    """Sub-consulta generada por descomposición"""
    id: str
    query: str
    type: QueryType
    strategy: SearchStrategy
    priority: int
    dependencies: List[str] = field(default_factory=list)
    expected_entities: List[str] = field(default_factory=list)


@dataclass
class Pointer:
    """
    Puntero a conocimiento en TrustGraph
    No contiene el contenido completo, solo referencias precisas
    """
    pointer_id: str
    pointer_type: Literal["vector", "entity", "relation", "chunk", "document"]
    source_id: str
    relevance_score: float
    access_path: str  # Cómo acceder: API endpoint o query
    metadata: Dict[str, Any] = field(default_factory=dict)
    snippet: str = ""  # Vista previa (primeros 200 chars)


@dataclass
class SearchResult:
    """Resultado de una búsqueda ejecutada"""
    subquery_id: str
    pointers: List[Pointer]
    entities_found: List[str] = field(default_factory=list)
    execution_time_ms: int = 0
    strategy_used: SearchStrategy = SearchStrategy.VECTOR_PURO


@dataclass
class SocratesState:
    """Estado del agente Sócrates"""
    # Entrada
    original_query: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    user_intent: Optional[str] = None

    # Análisis
    query_type: Optional[QueryType] = None
    complexity_score: float = 0.5  # 0-1
    requires_decomposition: bool = False

    # Descomposición
    subqueries: List[SubQuery] = field(default_factory=list)

    # Ejecución
    search_results: List[SearchResult] = field(default_factory=list)

    # Síntesis
    selected_pointers: List[Pointer] = field(default_factory=list)
    synthesized_response: str = ""

    # Salida
    final_answer: str = ""
    confidence: float = 0.0
    sources: List[Dict[str, Any]] = field(default_factory=list)

    # Control
    current_step: str = "inicio"
    errors: List[str] = field(default_factory=list)


class SocratesAgent:
    """
    Agente Sócrates - El maestro de la investigación dialéctica

    Flujo de trabajo (Método Socrático):
    1. MAIEUTICA (μαιευτική) → Extrae la intención real del usuario
    2. DIAIRESIS (διαίρεσις) → Divide la query en sub-consultas
    3. SYNAGOGÉ (συναγωγή) → Recolecta punteros de múltiples fuentes
    4. ANAKRISIS (ἀνάκρισις) → Examina y selecciona los mejores punteros
    5. SYNTHESIS (σύνθεσις) → Sintetiza respuesta coherente
    """

    def __init__(self, llm=None, api_gateway: str = "http://localhost:8080", llm_config: dict = None):
        self.llm = llm
        self.api_gateway = api_gateway

        # Configuración de LLM (provider, api_key, model)
        self.llm_config = llm_config or {}

        self.graph = self._build_graph()

        self._system_maieutica = """Eres Sócrates, el filósofo que revela la verdad mediante preguntas.
Tu método maieutico extrae la intención real detrás de cada consulta.

Analiza la pregunta del usuario y determina:
1. Tipo de consulta: factual, exploratoria, analítica, comparativa, procedural, temporal
2. Complejidad (0-1): ¿Requiere múltiples pasos o fuentes?
3. Necesita descomposición: ¿Es una pregunta simple o compuesta?
4. Intención subyacente: ¿Qué realmente necesita saber el usuario?

Responde en JSON:
{
    "tipo": "factual|exploratoria|analitica|comparativa|procedural|temporal",
    "complejidad": 0.7,
    "necesita_descomposicion": true|false,
    "intencion_real": "...",
    "conceptos_clave": ["..."],
    "ambiguedades": ["..."]
}"""

        self._system_diairesis = """Eres Sócrates aplicando la diaíresis (división).
Descompón consultas complejas en sub-consultas manejables.

Cada sub-consulta debe:
- Ser atómica (una sola cosa a resolver)
- Tener una estrategia de búsqueda definida
- Tener prioridad (1 = más importante)
- Especificar entidades esperadas

Estrategias disponibles:
- vector_puro: Búsqueda semántica directa
- grafo_puro: Navegación de entidades y relaciones
- grafo_rag: GraphRAG completo con contexto
- hibrido: Vector + Grafo combinado
- entidad_primero: Buscar entidad luego expandir

Responde en JSON:
{
    "subconsultas": [
        {
            "id": "q1",
            "consulta": "...",
            "tipo": "factual",
            "estrategia": "vector_puro",
            "prioridad": 1,
            "dependencias": [],
            "entidades_esperadas": ["..."]
        }
    ],
    "razonamiento": "..."
}"""

        self._system_synagoge = """Eres Sócrates recolectando conocimiento (synagogé).
Tu tarea es generar PUNTEROS precisos, no traer contenido completo.

Un puntero es una referencia exacta a dónde encontrar la información:
- pointer_type: vector|entity|relation|chunk|document
- source_id: ID único en la base
- access_path: endpoint o query para recuperar
- relevance_score: 0-1
- snippet: vista previa (máx 200 chars)

Responde en JSON:
{
    "punteros": [
        {
            "pointer_type": "vector",
            "source_id": "doc_123_chunk_0",
            "access_path": "/api/v1/vectors/doc_123_chunk_0",
            "relevance_score": 0.95,
            "snippet": "...",
            "metadata": {"source": "...", "tags": [...]}
        }
    ]
}"""

        self._system_anakrisis = """Eres Sócrates examinando (anakrisis) la calidad de los punteros.
Evalúa cada puntero y selecciona solo los más relevantes y confiables.

Criterios de selección:
1. Relevancia directa a la pregunta original
2. Diversidad de fuentes (no todo de un solo documento)
3. Confianza del score (>0.7 ideal)
4. Completitud (cubren todos los aspectos de la pregunta)

Responde en JSON:
{
    "punteros_seleccionados": ["pointer_id_1", "pointer_id_2"],
    "descartados": ["pointer_id_3"],
    "justificacion": "...",
    "cobertura": 0.85
}"""

        self._system_synthesis = """Eres Sócrates sintetizando (synthesis) la respuesta final.
Basándote en los punteros seleccionados, crea una respuesta coherente.

IMPORTANTE:
- NO inventes información
- Indica cuando hay vacíos de conocimiento
- Cita fuentes usando los access_paths
- Estructura: respuesta directa + detalles + fuentes

Responde en JSON:
{
    "respuesta": "...",
    "confianza": 0.85,
    "fuentes": [
        {"id": "...", "tipo": "...", "relevancia": 0.9}
    ],
    "vacios": ["..."],
    "sugerencias_seguimiento": ["..."]
}"""

    def _build_graph(self) -> StateGraph:
        """Construye el grafo de estados de Sócrates"""

        workflow = StateGraph(SocratesState)

        # Nodos del método socrático
        workflow.add_node("maieutica", self._node_maieutica)
        workflow.add_node("diairesis", self._node_diairesis)
        workflow.add_node("synagoge", self._node_synagoge)
        workflow.add_node("anakrisis", self._node_anakrisis)
        workflow.add_node("synthesis", self._node_synthesis)

        # Flujo
        workflow.set_entry_point("maieutica")

        workflow.add_conditional_edges(
            "maieutica",
            self._decision_maieutica,
            {
                "simple": "synagoge",      # Query simple, buscar directo
                "complejo": "diairesis",   # Query complejo, descomponer
                "error": END
            }
        )

        workflow.add_edge("diairesis", "synagoge")

        workflow.add_conditional_edges(
            "synagoge",
            self._decision_synagoge,
            {
                "suficiente": "anakrisis",
                "insuficiente": "synagoge",  # Reintentar con otra estrategia
                "error": END
            }
        )

        workflow.add_edge("anakrisis", "synthesis")
        workflow.add_edge("synthesis", END)

        return workflow.compile()

    # ═══════════════════════════════════════════════════════════════
    # NODOS DEL MÉTODO SOCRÁTICO
    # ═══════════════════════════════════════════════════════════════

    def _node_maieutica(self, state: SocratesState) -> SocratesState:
        """Extrae la intención real del usuario"""
        state.current_step = "maieutica"

        if not self.llm:
            # Análisis heurístico
            state = self._maieutica_heuristica(state)
            return state

        try:
            messages = [
                SystemMessage(content=self._system_maieutica),
                HumanMessage(content=f"""
Consulta del usuario: "{state.original_query}"

Contexto disponible: {json.dumps(state.context, indent=2)[:500]}

Analiza qué realmente necesita saber el usuario.
                """)
            ]

            response = self.llm.invoke(messages)
            resultado = json.loads(response.content)

            state.query_type = QueryType(resultado.get("tipo", "factual"))
            state.complexity_score = resultado.get("complejidad", 0.5)
            state.requires_decomposition = resultado.get("necesita_descomposicion", False)
            state.user_intent = resultado.get("intencion_real", state.original_query)

        except Exception as e:
            state.errors.append(f"Error en maieutica: {str(e)}")
            # Fallback heurístico
            state = self._maieutica_heuristica(state)

        return state

    def _node_diairesis(self, state: SocratesState) -> SocratesState:
        """Divide la consulta en sub-consultas"""
        state.current_step = "diairesis"

        if not self.llm:
            state.subqueries = self._diairesis_heuristica(state)
            return state

        try:
            messages = [
                SystemMessage(content=self._system_diairesis),
                HumanMessage(content=f"""
Consulta original: "{state.original_query}"
Intención detectada: {state.user_intent}
Tipo: {state.query_type.value if state.query_type else "factual"}

Descompón en sub-consultas atómicas.
                """)
            ]

            response = self.llm.invoke(messages)
            resultado = json.loads(response.content)

            for i, sq in enumerate(resultado.get("subconsultas", [])):
                state.subqueries.append(SubQuery(
                    id=sq.get("id", f"q{i}"),
                    query=sq["consulta"],
                    type=QueryType(sq.get("tipo", "factual")),
                    strategy=SearchStrategy(sq.get("estrategia", "vector_puro")),
                    priority=sq.get("prioridad", 1),
                    dependencies=sq.get("dependencias", []),
                    expected_entities=sq.get("entidades_esperadas", [])
                ))

        except Exception as e:
            state.errors.append(f"Error en diairesis: {str(e)}")
            state.subqueries = self._diairesis_heuristica(state)

        return state

    def _node_synagoge(self, state: SocratesState) -> SocratesState:
        """Recolecta punteros de múltiples fuentes"""
        state.current_step = "synagoge"

        # Si no hay subconsultas, crear una default
        if not state.subqueries:
            state.subqueries = [SubQuery(
                id="q0",
                query=state.original_query,
                type=QueryType.FACTUAL,
                strategy=SearchStrategy.GRAFO_RAG,
                priority=1
            )]

        # Ejecutar cada subconsulta
        for subq in state.subqueries:
            pointers = self._ejecutar_busqueda(subq)

            state.search_results.append(SearchResult(
                subquery_id=subq.id,
                pointers=pointers,
                strategy_used=subq.strategy
            ))

        return state

    def _node_anakrisis(self, state: SocratesState) -> SocratesState:
        """Examina y selecciona los mejores punteros"""
        state.current_step = "anakrisis"

        # Recolectar todos los punteros
        todos_punteros: List[Pointer] = []
        for result in state.search_results:
            todos_punteros.extend(result.pointers)

        # Ordenar por relevancia
        todos_punteros.sort(key=lambda p: p.relevance_score, reverse=True)

        # Seleccionar top N con diversidad
        seleccionados = []
        sources_seen = set()

        for ptr in todos_punteros:
            source = ptr.metadata.get("source", "unknown")
            if len(seleccionados) < 10:
                # Permitir hasta 2 punteros del mismo source
                if list(sources_seen).count(source) < 2:
                    seleccionados.append(ptr)
                    sources_seen.add(source)

        state.selected_pointers = seleccionados
        return state

    def _node_synthesis(self, state: SocratesState) -> SocratesState:
        """Sintetiza la respuesta final"""
        state.current_step = "synthesis"

        if not self.llm:
            state = self._synthesis_heuristica(state)
            return state

        try:
            # Preparar contexto de punteros
            pointers_context = []
            for ptr in state.selected_pointers[:5]:
                pointers_context.append({
                    "id": ptr.pointer_id,
                    "tipo": ptr.pointer_type,
                    "snippet": ptr.snippet,
                    "relevancia": ptr.relevance_score
                })

            messages = [
                SystemMessage(content=self._system_synthesis),
                HumanMessage(content=f"""
Pregunta original: "{state.original_query}"

Punteros seleccionados:
{json.dumps(pointers_context, indent=2)}

Sintetiza una respuesta coherente basada en estos punteros.
                """)
            ]

            response = self.llm.invoke(messages)
            resultado = json.loads(response.content)

            state.final_answer = resultado.get("respuesta", "")
            state.confidence = resultado.get("confianza", 0.5)
            state.sources = resultado.get("fuentes", [])

        except Exception as e:
            state.errors.append(f"Error en synthesis: {str(e)}")
            state = self._synthesis_heuristica(state)

        return state

    # ═══════════════════════════════════════════════════════════════
    # DECISIONES CONDICIONALES
    # ═══════════════════════════════════════════════════════════════

    def _decision_maieutica(self, state: SocratesState) -> str:
        if state.errors:
            return "error"
        if state.requires_decomposition or state.complexity_score > 0.6:
            return "complejo"
        return "simple"

    def _decision_synagoge(self, state: SocratesState) -> str:
        total_pointers = sum(len(r.pointers) for r in state.search_results)
        if total_pointers >= 3:
            return "suficiente"
        return "insuficiente"

    # ═══════════════════════════════════════════════════════════════
    # MÉTODOS DE BÚSQUEDA
    # ═══════════════════════════════════════════════════════════════

    def _ejecutar_busqueda(self, subquery: SubQuery) -> List[Pointer]:
        """Ejecuta una búsqueda según la estrategia"""

        # Por ahora, simulamos las búsquedas
        # En implementación real, se conectaría a la API de TrustGraph

        if subquery.strategy == SearchStrategy.VECTOR_PURO:
            return self._busqueda_vector(subquery)
        elif subquery.strategy == SearchStrategy.GRAFO_PURO:
            return self._busqueda_grafo(subquery)
        elif subquery.strategy == SearchStrategy.GRAFO_RAG:
            return self._busqueda_grafo_rag(subquery)
        else:
            return self._busqueda_hibrida(subquery)

    def _busqueda_vector(self, subquery: SubQuery) -> List[Pointer]:
        """Búsqueda vectorial simulada"""
        # Simulación - en realidad llamaría a Qdrant
        return [
            Pointer(
                pointer_id=f"vec_{i}",
                pointer_type="vector",
                source_id=f"doc_{i}",
                relevance_score=0.9 - (i * 0.1),
                access_path=f"/api/v1/search/vector?q={subquery.query}",
                snippet=f"Resultado {i} para: {subquery.query[:50]}...",
                metadata={"strategy": "vector"}
            )
            for i in range(3)
        ]

    def _busqueda_grafo(self, subquery: SubQuery) -> List[Pointer]:
        """Búsqueda de grafo simulada"""
        return [
            Pointer(
                pointer_id=f"ent_{entity}",
                pointer_type="entity",
                source_id=entity,
                relevance_score=0.95,
                access_path=f"/api/v1/graph/entity/{entity}",
                snippet=f"Entidad: {entity}",
                metadata={"strategy": "graph"}
            )
            for entity in subquery.expected_entities[:3]
        ] if subquery.expected_entities else []

    def _busqueda_grafo_rag(self, subquery: SubQuery) -> List[Pointer]:
        """GraphRAG completo"""
        vectors = self._busqueda_vector(subquery)
        entities = self._busqueda_grafo(subquery)
        return vectors + entities

    def _busqueda_hibrida(self, subquery: SubQuery) -> List[Pointer]:
        """Búsqueda híbrida"""
        return self._busqueda_grafo_rag(subquery)

    # ═══════════════════════════════════════════════════════════════
    # MÉTODOS HEURÍSTICOS (Fallback sin LLM)
    # ═══════════════════════════════════════════════════════════════

    def _maieutica_heuristica(self, state: SocratesState) -> SocratesState:
        """Análisis de intención sin LLM"""
        query_lower = state.original_query.lower()

        # Detectar tipo
        if any(w in query_lower for w in ["cómo", "pasos", "proceso", "guía"]):
            state.query_type = QueryType.PROCEDURAL
        elif any(w in query_lower for w in ["comparar", "diferencia", "versus", "vs"]):
            state.query_type = QueryType.COMPARATIVA
        elif any(w in query_lower for w in ["por qué", "explica", "análisis"]):
            state.query_type = QueryType.ANALITICA
        elif any(w in query_lower for w in ["cuándo", "histórico", "evolución"]):
            state.query_type = QueryType.TEMPORAL
        else:
            state.query_type = QueryType.FACTUAL

        # Complejidad basada en longitud y conectores
        palabras = len(state.original_query.split())
        conectores = sum(1 for w in ["y", "o", "pero", "además", "sin embargo"] if w in query_lower)
        state.complexity_score = min(1.0, (palabras / 20) + (conectores * 0.1))
        state.requires_decomposition = state.complexity_score > 0.6
        state.user_intent = state.original_query

        return state

    def _diairesis_heuristica(self, state: SocratesState) -> List[SubQuery]:
        """Descomposición sin LLM"""
        # Dividir por conectores
        query = state.original_query
        partes = []

        for sep in [" y ", " además ", ", ", "; "]:
            if sep in query:
                partes = query.split(sep)
                break

        if not partes or len(partes) == 1:
            partes = [query]

        return [
            SubQuery(
                id=f"q{i}",
                query=p.strip(),
                type=state.query_type or QueryType.FACTUAL,
                strategy=SearchStrategy.GRAFO_RAG,
                priority=len(partes) - i
            )
            for i, p in enumerate(partes) if p.strip()
        ]

    def _synthesis_heuristica(self, state: SocratesState) -> SocratesState:
        """Síntesis sin LLM"""
        snippets = [p.snippet for p in state.selected_pointers[:3]]

        state.final_answer = f"""Basándome en la información disponible:

{chr(10).join(f"• {s}" for s in snippets)}

Para más detalles, consulta las fuentes referenciadas.
"""
        state.confidence = sum(p.relevance_score for p in state.selected_pointers) / max(len(state.selected_pointers), 1)
        state.sources = [{"id": p.pointer_id, "tipo": p.pointer_type} for p in state.selected_pointers]

        return state

    # ═══════════════════════════════════════════════════════════════
    # API PÚBLICA
    # ═══════════════════════════════════════════════════════════════

    async def investigar(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Realiza una investigación completa usando el método socrático

        Args:
            query: Pregunta o consulta del usuario
            context: Contexto adicional (historial, preferencias, etc.)

        Returns:
            Respuesta estructurada con punteros y síntesis
        """
        initial_state = SocratesState(
            original_query=query,
            context=context or {}
        )

        result = await self.graph.ainvoke(initial_state)

        return {
            "respuesta": result.final_answer,
            "confianza": result.confidence,
            "punteros": [
                {
                    "id": p.pointer_id,
                    "tipo": p.pointer_type,
                    "source": p.source_id,
                    "relevancia": p.relevance_score,
                    "acceso": p.access_path,
                    "snippet": p.snippet
                }
                for p in result.selected_pointers
            ],
            "estrategia": {
                "tipo_query": result.query_type.value if result.query_type else None,
                "complejidad": result.complexity_score,
                "subconsultas": len(result.subqueries)
            },
            "fuentes": result.sources,
            "errores": result.errors
        }

    def investigar_sync(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Versión síncrona de investigar"""
        return asyncio.run(self.investigar(query, context))


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python socrates.py 'tu pregunta aquí'")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    agent = SocratesAgent()
    result = agent.investigar_sync(query)

    print(json.dumps(result, indent=2, default=str))
