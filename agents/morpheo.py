#!/usr/bin/env python3
"""
Morpheo (Μορφεύς) - El Guardián del Sueño y Remodelador de Recuerdos

El dios de los sueños que vigila mientras el sistema descansa.
Se ejecuta durante horas de baja actividad para:
- Reparar recuerdos corruptos o incompletos
- Reindexar contenido para mejor recuperación
- Optimizar embeddings y relaciones
- Consolidar fragmentos dispersos
- Detectar y eliminar duplicados
- Actualizar metadatos obsoletos

El Ciclo de Sueño es el contenedor temporal (el cuándo)
La Optimización/Reindexación es la tarea técnica (el qué)
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional, Literal
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END


class RepairType(Enum):
    """Tipos de reparación que Morpheo puede realizar"""
    DUPLICADO = "duplicado"           # Eliminar/mergear duplicados
    HUERFANO = "huerfano"             # Reconectar entidades sin relaciones
    INCOMPLETO = "incompleto"         # Completar metadatos faltantes
    CORRUPTO = "corrupto"             # Reparar datos corruptos
    OBSOLETO = "obsoleto"             # Actualizar información vieja
    FRAGMENTADO = "fragmentado"       # Consolidar chunks dispersos


class OptimizationType(Enum):
    """Tipos de optimización disponibles"""
    REINDEXAR = "reindexar"           # Recalcular embeddings
    CONSOLIDAR = "consolidar"         # Fusionar chunks relacionados
    COMPRIMIR = "comprimir"           # Reducir redundancia
    ENRIQUECER = "enriquecer"         # Añadir metadatos inferidos
    DEFRAGMENTAR = "defragmentar"     # Reorganizar almacenamiento


@dataclass
class MemoryIssue:
    """Problema detectado en la memoria"""
    issue_id: str
    type: RepairType
    severity: Literal["baja", "media", "alta", "critica"]
    description: str
    affected_ids: List[str]
    suggested_action: str
    estimated_impact: float  # 0-1, qué tanto mejora repararlo


@dataclass
class RepairPlan:
    """Plan de reparación generado"""
    repair_id: str
    type: RepairType
    target_ids: List[str]
    operations: List[Dict[str, Any]]
    rollback_plan: List[Dict[str, Any]]
    estimated_time_seconds: int


@dataclass
class OptimizationJob:
    """Trabajo de optimización"""
    job_id: str
    type: OptimizationType
    target_collection: str
    parameters: Dict[str, Any]
    priority: int


@dataclass
class MaintenanceReport:
    """Reporte de mantenimiento nocturno"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    issues_detected: List[MemoryIssue] = field(default_factory=list)
    repairs_executed: List[RepairPlan] = field(default_factory=list)
    optimizations_run: List[OptimizationJob] = field(default_factory=list)
    stats_before: Dict[str, Any] = field(default_factory=dict)
    stats_after: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


@dataclass
class MorpheoState:
    """Estado del agente Morpheo"""
    # Configuración
    session_id: str = ""
    start_time: Optional[datetime] = None
    max_duration_minutes: int = 360  # 6 horas por defecto
    intensity: Literal["ligero", "normal", "profundo"] = "normal"

    # Fases de trabajo
    phase: Literal["escanear", "analizar", "planificar", "reparar", "optimizar", "reportar"] = "escanear"

    # Datos recolectados
    memory_stats: Dict[str, Any] = field(default_factory=dict)
    issues_found: List[MemoryIssue] = field(default_factory=list)
    repair_queue: List[RepairPlan] = field(default_factory=list)
    optimization_queue: List[OptimizationJob] = field(default_factory=list)

    # Ejecución
    current_repair: Optional[RepairPlan] = None
    current_optimization: Optional[OptimizationJob] = None
    completed_repairs: int = 0
    completed_optimizations: int = 0

    # Resultados
    report: Optional[MaintenanceReport] = None
    should_continue: bool = True
    errors: List[str] = field(default_factory=list)


class MorpheoAgent:
    """
    Agente Morpheo - El arquitecto de los sueños digitales

    Ciclo Nocturno (Hypnos):
    1. ESCANEAR → Recolecta estadísticas de todas las bases
    2. ANALIZAR → Detecta anomalías y problemas
    3. PLANIFICAR → Crea planes de reparación y optimización
    4. REPARAR → Ejecuta reparaciones (con rollback disponible)
    5. OPTIMIZAR → Mejora rendimiento y estructura
    6. REPORTAR → Genera informe del ciclo

    Ejecución continua durante horas de baja actividad.
    Puede pausarse y reanudarse.
    """

    def __init__(
        self,
        llm=None,
        api_gateway: str = "http://localhost:8080",
        backup_dir: str = ".morpheo_backups",
        llm_config: dict = None
    ):
        self.llm = llm
        self.api_gateway = api_gateway
        self.backup_dir = backup_dir
        self.llm_config = llm_config or {}
        self.graph = self._build_graph()

        os.makedirs(backup_dir, exist_ok=True)

        self._system_analizador = """Eres Morpheo, el dios de los sueños digitales.
Tu visión penetra las capas de la memoria para detectar imperfecciones.

Analiza estadísticas de la base de conocimiento y detecta:
1. Duplicados: contenido repetido o muy similar
2. Huérfanos: entidades sin relaciones o viceversa
3. Incompletos: metadatos faltantes o vacíos
4. Corruptos: datos que no cumplen esquema
5. Obsoletos: información marcada como vieja
6. Fragmentados: chunks que deberían estar unidos

Responde en JSON:
{
    "issues": [
        {
            "type": "duplicado|huerfano|incompleto|corrupto|obsoleto|fragmentado",
            "severity": "baja|media|alta|critica",
            "description": "...",
            "affected_count": 10,
            "affected_sample": ["id1", "id2"],
            "suggested_action": "..."
        }
    ],
    "health_score": 0.85,
    "priority": "alta|media|baja"
}"""

        self._system_planificador = """Eres Morpheo planeando las reparaciones del sueño.
Crea planes detallados para cada problema detectado.

Para cada reparación:
1. Define operaciones específicas
2. Crea plan de rollback (por si falla)
3. Estima tiempo necesario
4. Prioriza por impacto

Responde en JSON:
{
    "repairs": [
        {
            "type": "...",
            "target_ids": ["..."],
            "operations": [{"op": "merge|delete|update|create", "details": {}}],
            "rollback": [{"op": "...", "backup_state": {}}],
            "estimated_seconds": 120
        }
    ],
    "optimizations": [
        {
            "type": "reindexar|consolidar|comprimir|enriquecer|defragmentar",
            "target": "collection_name",
            "parameters": {},
            "priority": 1
        }
    ]
}"""

    def _build_graph(self) -> StateGraph:
        """Construye el grafo del ciclo de sueño"""

        workflow = StateGraph(MorpheoState)

        # Nodos del ciclo nocturno
        workflow.add_node("escanear", self._node_escanear)
        workflow.add_node("analizar", self._node_analizar)
        workflow.add_node("planificar", self._node_planificar)
        workflow.add_node("reparar", self._node_reparar)
        workflow.add_node("optimizar", self._node_optimizar)
        workflow.add_node("reportar", self._node_reportar)
        workflow.add_node("verificar_tiempo", self._node_verificar_tiempo)

        # Flujo del ciclo
        workflow.set_entry_point("escanear")
        workflow.add_edge("escanear", "analizar")
        workflow.add_edge("analizar", "planificar")

        workflow.add_conditional_edges(
            "planificar",
            self._decision_planificacion,
            {
                "reparar": "reparar",
                "optimizar": "optimizar",
                "terminar": "reportar"
            }
        )

        workflow.add_edge("reparar", "verificar_tiempo")
        workflow.add_edge("optimizar", "verificar_tiempo")

        workflow.add_conditional_edges(
            "verificar_tiempo",
            self._decision_continuar,
            {
                "continuar_reparar": "reparar",
                "continuar_optimizar": "optimizar",
                "terminar": "reportar"
            }
        )

        workflow.add_edge("reportar", END)

        return workflow.compile()

    # ═══════════════════════════════════════════════════════════════
    # NODOS DEL CICLO NOCTURNO
    # ═══════════════════════════════════════════════════════════════

    def _node_escanear(self, state: MorpheoState) -> MorpheoState:
        """Escanea todas las bases de datos recolectando estadísticas"""
        state.phase = "escanear"
        state.start_time = datetime.now()
        state.session_id = f"morpheo_{state.start_time.strftime('%Y%m%d_%H%M%S')}"

        try:
            # Simular recolección de estadísticas
            # En implementación real, consultar Cassandra y Qdrant
            state.memory_stats = {
                "cassandra": {
                    "entities": 15420,
                    "relations": 38450,
                    "orphaned_entities": 127,
                    "relationless_entities": 45
                },
                "qdrant": {
                    "vectors": 28900,
                    "chunks": 42100,
                    "avg_chunk_size": 850,
                    "collections": 5
                },
                "metadata": {
                    "last_maintenance": "2024-01-15T03:00:00Z",
                    "total_storage_mb": 2048,
                    "index fragmentation": 0.15
                }
            }

            state.report = MaintenanceReport(
                session_id=state.session_id,
                start_time=state.start_time,
                stats_before=state.memory_stats.copy()
            )

        except Exception as e:
            state.errors.append(f"Error en escaneo: {str(e)}")

        return state

    def _node_analizar(self, state: MorpheoState) -> MorpheoState:
        """Analiza estadísticas y detecta problemas"""
        state.phase = "analizar"

        if not self.llm:
            state.issues_found = self._analisis_heuristico(state)
            return state

        try:
            messages = [
                SystemMessage(content=self._system_analizador),
                HumanMessage(content=f"""
Estadísticas de la base de conocimiento:
{json.dumps(state.memory_stats, indent=2)}

Detecta todos los problemas posibles.
                """)
            ]

            response = self.llm.invoke(messages)
            resultado = json.loads(response.content)

            for i, issue_data in enumerate(resultado.get("issues", [])):
                state.issues_found.append(MemoryIssue(
                    issue_id=f"issue_{i}",
                    type=RepairType(issue_data["type"]),
                    severity=issue_data["severity"],
                    description=issue_data["description"],
                    affected_ids=issue_data.get("affected_sample", []),
                    suggested_action=issue_data["suggested_action"],
                    estimated_impact=0.7 if issue_data["severity"] == "alta" else 0.4
                ))

        except Exception as e:
            state.errors.append(f"Error en análisis: {str(e)}")
            state.issues_found = self._analisis_heuristico(state)

        return state

    def _node_planificar(self, state: MorpheoState) -> MorpheoState:
        """Genera planes de reparación y optimización"""
        state.phase = "planificar"

        # Agrupar issues por tipo para eficiencia
        issues_by_type = {}
        for issue in state.issues_found:
            if issue.type not in issues_by_type:
                issues_by_type[issue.type] = []
            issues_by_type[issue.type].append(issue)

        # Crear planes de reparación
        for repair_type, issues in issues_by_type.items():
            all_affected = []
            for i in issues:
                all_affected.extend(i.affected_ids)

            if len(all_affected) > 100:
                # Procesar en lotes
                batches = [all_affected[i:i+100] for i in range(0, len(all_affected), 100)]
                for batch in batches:
                    state.repair_queue.append(self._crear_plan_reparacion(
                        repair_type, batch
                    ))
            else:
                state.repair_queue.append(self._crear_plan_reparacion(
                    repair_type, all_affected
                ))

        # Agregar optimizaciones según intensidad
        opts = self._generar_optimizaciones(state)
        state.optimization_queue.extend(opts)

        return state

    def _node_reparar(self, state: MorpheoState) -> MorpheoState:
        """Ejecuta un plan de reparación"""
        state.phase = "reparar"

        if not state.repair_queue:
            return state

        # Tomar siguiente reparación
        repair = state.repair_queue.pop(0)
        state.current_repair = repair

        try:
            # Ejecutar operaciones
            for op in repair.operations:
                self._ejecutar_operacion(op, rollback=False)

            state.completed_repairs += 1
            if state.report:
                state.report.repairs_executed.append(repair)

        except Exception as e:
            # Rollback en caso de error
            state.errors.append(f"Error en reparación {repair.repair_id}: {str(e)}")
            for op in repair.rollback_plan:
                try:
                    self._ejecutar_operacion(op, rollback=True)
                except:
                    pass  # Mejor esfuerzo en rollback

        return state

    def _node_optimizar(self, state: MorpheoState) -> MorpheoState:
        """Ejecuta un trabajo de optimización"""
        state.phase = "optimizar"

        if not state.optimization_queue:
            return state

        job = state.optimization_queue.pop(0)
        state.current_optimization = job

        try:
            self._ejecutar_optimizacion(job)
            state.completed_optimizations += 1
            if state.report:
                state.report.optimizations_run.append(job)

        except Exception as e:
            state.errors.append(f"Error en optimización {job.job_id}: {str(e)}")

        return state

    def _node_verificar_tiempo(self, state: MorpheoState) -> MorpheoState:
        """Verifica si debemos continuar o terminar"""
        elapsed = datetime.now() - state.start_time
        elapsed_minutes = elapsed.total_seconds() / 60

        # Verificar tiempo máximo
        if elapsed_minutes >= state.max_duration_minutes:
            state.should_continue = False
            return state

        # Verificar si queda trabajo
        if not state.repair_queue and not state.optimization_queue:
            state.should_continue = False

        return state

    def _node_reportar(self, state: MorpheoState) -> MorpheoState:
        """Genera el reporte final del ciclo"""
        state.phase = "reportar"

        if state.report:
            state.report.end_time = datetime.now()
            state.report.stats_after = self._recolectar_stats_finales()
            state.report.errors = state.errors

            # Guardar reporte
            report_path = os.path.join(
                self.backup_dir,
                f"report_{state.session_id}.json"
            )
            with open(report_path, 'w') as f:
                json.dump(state.report.__dict__, f, indent=2, default=str)

        return state

    # ═══════════════════════════════════════════════════════════════
    # DECISIONES CONDICIONALES
    # ═══════════════════════════════════════════════════════════════

    def _decision_planificacion(self, state: MorpheoState) -> str:
        if state.repair_queue:
            return "reparar"
        elif state.optimization_queue:
            return "optimizar"
        return "terminar"

    def _decision_continuar(self, state: MorpheoState) -> str:
        if not state.should_continue:
            return "terminar"

        if state.repair_queue:
            return "continuar_reparar"
        elif state.optimization_queue:
            return "continuar_optimizar"
        return "terminar"

    # ═══════════════════════════════════════════════════════════════
    # MÉTODOS AUXILIARES
    # ═══════════════════════════════════════════════════════════════

    def _analisis_heuristico(self, state: MorpheoState) -> List[MemoryIssue]:
        """Análisis sin LLM"""
        issues = []
        stats = state.memory_stats

        # Detectar huérfanos
        cassandra_stats = stats.get("cassandra", {})
        if cassandra_stats.get("orphaned_entities", 0) > 0:
            issues.append(MemoryIssue(
                issue_id="orphans_1",
                type=RepairType.HUERFANO,
                severity="media",
                description=f"{cassandra_stats['orphaned_entities']} entidades sin relaciones",
                affected_ids=[],
                suggested_action="Reconectar o eliminar entidades huérfanas",
                estimated_impact=0.3
            ))

        # Detectar fragmentación
        metadata = stats.get("metadata", {})
        if metadata.get("index fragmentation", 0) > 0.2:
            issues.append(MemoryIssue(
                issue_id="frag_1",
                type=RepairType.FRAGMENTADO,
                severity="alta",
                description=f"Fragmentación de índice: {metadata['index fragmentation']:.1%}",
                affected_ids=[],
                suggested_action="Reindexar colecciones fragmentadas",
                estimated_impact=0.6
            ))

        return issues

    def _crear_plan_reparacion(
        self,
        repair_type: RepairType,
        target_ids: List[str]
    ) -> RepairPlan:
        """Crea un plan de reparación"""
        repair_id = f"repair_{repair_type.value}_{hashlib.md5(str(target_ids).encode()).hexdigest()[:8]}"

        operations = []
        rollback = []

        if repair_type == RepairType.HUERFANO:
            operations = [{"op": "find_relations", "ids": target_ids}]
            rollback = [{"op": "noop"}]
        elif repair_type == RepairType.DUPLICADO:
            operations = [{"op": "merge", "ids": target_ids}]
            rollback = [{"op": "split", "ids": target_ids}]
        elif repair_type == RepairType.OBSOLETO:
            operations = [{"op": "archive", "ids": target_ids}]
            rollback = [{"op": "restore", "ids": target_ids}]
        else:
            operations = [{"op": "inspect", "ids": target_ids}]
            rollback = [{"op": "noop"}]

        return RepairPlan(
            repair_id=repair_id,
            type=repair_type,
            target_ids=target_ids,
            operations=operations,
            rollback_plan=rollback,
            estimated_time_seconds=len(target_ids) * 2
        )

    def _generar_optimizaciones(self, state: MorpheoState) -> List[OptimizationJob]:
        """Genera trabajos de optimización"""
        jobs = []

        intensity_map = {
            "ligero": [OptimizationType.REINDEXAR],
            "normal": [OptimizationType.REINDEXAR, OptimizationType.CONSOLIDAR],
            "profundo": [
                OptimizationType.REINDEXAR,
                OptimizationType.CONSOLIDAR,
                OptimizationType.DEFRAGMENTAR,
                OptimizationType.ENRIQUECER
            ]
        }

        for opt_type in intensity_map.get(state.intensity, []):
            jobs.append(OptimizationJob(
                job_id=f"opt_{opt_type.value}",
                type=opt_type,
                target_collection="docs",
                parameters={},
                priority=1
            ))

        return jobs

    def _ejecutar_operacion(self, op: Dict[str, Any], rollback: bool = False):
        """Ejecuta una operación de reparación"""
        # En implementación real, llamar a la API de TrustGraph
        op_type = op.get("op", "noop")
        print(f"  {'[ROLLBACK]' if rollback else ''} Ejecutando: {op_type}")

    def _ejecutar_optimizacion(self, job: OptimizationJob):
        """Ejecuta un trabajo de optimización"""
        print(f"  Optimizando: {job.type.value} en {job.target_collection}")

    def _recolectar_stats_finales(self) -> Dict[str, Any]:
        """Recolecta estadísticas finales"""
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "optimized"
        }

    # ═══════════════════════════════════════════════════════════════
    # API PÚBLICA
    # ═══════════════════════════════════════════════════════════════

    async def ejecutar_ciclo(
        self,
        max_duration_minutes: int = 360,
        intensity: Literal["ligero", "normal", "profundo"] = "normal"
    ) -> Dict[str, Any]:
        """
        Ejecuta un ciclo completo de mantenimiento nocturno

        Args:
            max_duration_minutes: Tiempo máximo de ejecución
            intensity: Nivel de optimización (ligero/normal/profundo)

        Returns:
            Reporte del ciclo ejecutado
        """
        initial_state = MorpheoState(
            max_duration_minutes=max_duration_minutes,
            intensity=intensity
        )

        result = await self.graph.ainvoke(initial_state)

        report_data = {}
        if result.report:
            report_data = {
                "session_id": result.report.session_id,
                "duracion_minutos": (
                    (result.report.end_time - result.report.start_time).total_seconds() / 60
                    if result.report.end_time else 0
                ),
                "issues_detectados": len(result.report.issues_detected),
                "reparaciones_completadas": len(result.report.repairs_executed),
                "optimizaciones_completadas": len(result.report.optimizations_run),
                "stats_antes": result.report.stats_before,
                "stats_despues": result.report.stats_after,
                "errores": result.errors
            }

        return {
            "success": len(result.errors) == 0,
            "session_id": result.session_id,
            "fase_final": result.phase,
            "reparaciones_hechas": result.completed_repairs,
            "optimizaciones_hechas": result.completed_optimizations,
            "reporte": report_data,
            "errores": result.errors
        }

    def ejecutar_ciclo_sync(
        self,
        max_duration_minutes: int = 360,
        intensity: Literal["ligero", "normal", "profundo"] = "normal"
    ) -> Dict[str, Any]:
        """Versión síncrona del ciclo nocturno"""
        return asyncio.run(self.ejecutar_ciclo(max_duration_minutes, intensity))


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    intensity = sys.argv[1] if len(sys.argv) > 1 else "normal"
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60

    print(f"🌙 Iniciando ciclo de Morpheo...")
    print(f"   Intensidad: {intensity}")
    print(f"   Duración máxima: {duration} minutos")
    print("-" * 50)

    agent = MorpheoAgent()
    result = agent.ejecutar_ciclo_sync(
        max_duration_minutes=duration,
        intensity=intensity
    )

    print("\n" + "=" * 50)
    print("📊 Resultado del ciclo:")
    print(json.dumps(result, indent=2, default=str))
