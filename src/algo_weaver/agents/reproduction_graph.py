"""Stateful reproduction workflow with an optional LangGraph backend."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any, NotRequired, TypedDict, cast

from algo_weaver.schemas.capability import AlgorithmCapability
from algo_weaver.schemas.execution import ExecutionResult
from algo_weaver.schemas.ingestion import IngestedSource
from algo_weaver.schemas.reproduction import ReproductionBundle, ReproductionPlan
from algo_weaver.schemas.retrieval import RetrievalHit
from algo_weaver.services.code_generation import ArtifactGenerator
from algo_weaver.services.repair import BoundedRepairLoop
from algo_weaver.services.reproduction import ReproductionPlanner, TemplateArtifactWriter
from algo_weaver.services.retrieval import LocalLexicalRetriever, SourceChunker
from algo_weaver.services.validation import ValidationService

END: Any = None
START: Any = None
StateGraph: Any = None

try:
    from langgraph.graph import END as _END
    from langgraph.graph import START as _START
    from langgraph.graph import StateGraph as _StateGraph

    END = _END
    START = _START
    StateGraph = _StateGraph
except ModuleNotFoundError:  # pragma: no cover - fallback is used in the baseline environment
    pass


class ReproductionState(TypedDict):
    source: dict
    sources: NotRequired[list[dict]]
    capability: dict
    hits: NotRequired[list[dict]]
    plan: NotRequired[dict]
    bundle: NotRequired[dict]
    artifact_paths: NotRequired[list[str]]
    execution: NotRequired[dict]
    repair_result: NotRequired[dict]
    reports: NotRequired[list[dict]]
    error: NotRequired[str]


ExecutionRunner = Callable[[Path], ExecutionResult]
RepairAction = Callable[[ReproductionBundle, Path, ExecutionResult], bool]


def build_reproduction_graph(
    *,
    workspace: str | Path | None = None,
    runner: ExecutionRunner | None = None,
    repair: RepairAction | None = None,
    max_repair_attempts: int = 0,
    generator: ArtifactGenerator | None = None,
):
    """Build a reproduction workflow with optional isolated execution and repair.

    The default graph remains retrieve -> plan -> generate -> validate. Passing an
    injected runner enables artifact writing and execution without ever executing
    generated code on the host. A repair callback is invoked only for failed or
    timed-out runner observations and is bounded by ``max_repair_attempts``.
    """
    workspace_path = Path(workspace) if workspace is not None else None
    if runner is not None and workspace_path is None:
        raise ValueError("workspace is required when an execution runner is supplied")
    if repair is not None and runner is None:
        raise ValueError("an execution runner is required when a repair callback is supplied")
    if max_repair_attempts < 0:
        raise ValueError("max_repair_attempts cannot be negative")
    execution_enabled = runner is not None
    repair_enabled = repair is not None and max_repair_attempts > 0

    def retrieve_node(state: ReproductionState) -> dict:
        capability = AlgorithmCapability.model_validate(state["capability"])
        source_records = state.get("sources") or [state["source"]]
        sources = [IngestedSource.model_validate(item) for item in source_records]
        chunks = [chunk for source in sources for chunk in SourceChunker().chunk(source)]
        hits = LocalLexicalRetriever(chunks).search(capability.name, top_k=5)
        return {"hits": [hit.model_dump(mode="json") for hit in hits]}

    def plan_node(state: ReproductionState) -> dict:
        capability = AlgorithmCapability.model_validate(state["capability"])
        hits = [RetrievalHit.model_validate(item) for item in state.get("hits", [])]
        plan = ReproductionPlanner().build_plan(capability, hits)
        if plan.status != "ready":
            return {"error": "; ".join(plan.blocking_reasons)}
        return {"plan": plan.model_dump(mode="json")}

    def generate_node(state: ReproductionState) -> dict:
        plan = ReproductionPlan.model_validate(state["plan"])
        hits = [RetrievalHit.model_validate(item) for item in state.get("hits", [])]
        bundle = (
            generator.generate(plan, hits)
            if generator is not None
            else TemplateArtifactWriter().generate(plan)
        )
        return {
            "plan": bundle.plan.model_dump(mode="json"),
            "bundle": bundle.model_dump(mode="json"),
        }

    def write_node(state: ReproductionState) -> dict:
        if workspace_path is None:
            raise ValueError("workspace is required for artifact writing")
        bundle = ReproductionBundle.model_validate(state["bundle"])
        paths = TemplateArtifactWriter().write(bundle, workspace_path)
        return {"artifact_paths": [str(path) for path in paths]}

    def execute_node(_state: ReproductionState) -> dict:
        if runner is None or workspace_path is None:
            raise ValueError("execution runner and workspace are required")
        result = runner(workspace_path)
        return {"execution": result.model_dump(mode="json")}

    def route_after_execute(state: ReproductionState) -> str:
        execution = ExecutionResult.model_validate(state["execution"])
        if repair_enabled and execution.status in {"failed", "timeout"}:
            return "repair"
        return "validate"

    def repair_node(state: ReproductionState) -> dict:
        if runner is None or repair is None or workspace_path is None:
            raise ValueError("repair requires runner, callback and workspace")
        bundle = ReproductionBundle.model_validate(state["bundle"])
        initial = ExecutionResult.model_validate(state["execution"])
        latest = initial

        def execute_again() -> ExecutionResult:
            nonlocal latest
            latest = runner(workspace_path)
            return latest

        loop_result = BoundedRepairLoop(max_attempts=max_repair_attempts).run(
            initial,
            repair=lambda observation, _attempt: repair(bundle, workspace_path, observation),
            execute=execute_again,
        )
        return {
            "bundle": bundle.model_dump(mode="json"),
            "execution": latest.model_dump(mode="json"),
            "repair_result": loop_result.model_dump(mode="json"),
        }

    def validate_node(state: ReproductionState) -> dict:
        capability = AlgorithmCapability.model_validate(state["capability"])
        bundle = state["bundle"]
        validator = ValidationService()
        reports = [validator.validate_capability(capability)]
        for artifact in bundle["artifacts"]:
            if artifact["kind"] == "python_source":
                reports.append(
                    validator.validate_python_source(
                        artifact["content"],
                        source_id=artifact["path"],
                        required_function=(
                            "moving_average" if "moving_average" in artifact["content"] else None
                        ),
                    )
                )
        if "execution" in state:
            execution = ExecutionResult.model_validate(state["execution"])
            reports.append(validator.build_runtime_report(capability, execution, reports[1:]))
        return {"reports": [report.model_dump(mode="json") for report in reports]}

    if StateGraph is None:
        class FallbackGraph:
            def invoke(self, state: ReproductionState) -> dict:
                current: dict[str, object] = dict(state)
                for node in (retrieve_node, plan_node, generate_node):
                    update = node(cast(ReproductionState, current))
                    current.update(update)
                    if "error" in update:
                        break
                if "error" not in current and execution_enabled:
                    current.update(write_node(cast(ReproductionState, current)))
                    current.update(execute_node(cast(ReproductionState, current)))
                    if repair_enabled and route_after_execute(cast(ReproductionState, current)) == "repair":
                        current.update(repair_node(cast(ReproductionState, current)))
                if "error" not in current:
                    current.update(validate_node(cast(ReproductionState, current)))
                return current

        return FallbackGraph()

    builder = StateGraph(ReproductionState)
    builder.add_node("retrieve", retrieve_node)
    builder.add_node("plan", plan_node)
    builder.add_node("generate", generate_node)
    if execution_enabled:
        builder.add_node("write_artifacts", write_node)
        builder.add_node("execute", execute_node)
        if repair_enabled:
            builder.add_node("repair", repair_node)
    builder.add_node("validate", validate_node)
    builder.add_edge(START, "retrieve")
    builder.add_edge("retrieve", "plan")
    builder.add_edge("plan", "generate")
    if execution_enabled:
        builder.add_edge("generate", "write_artifacts")
        builder.add_edge("write_artifacts", "execute")
        if repair_enabled:
            builder.add_conditional_edges(
                "execute",
                route_after_execute,
                {"repair": "repair", "validate": "validate"},
            )
            builder.add_edge("repair", "validate")
        else:
            builder.add_edge("execute", "validate")
    else:
        builder.add_edge("generate", "validate")
    builder.add_edge("validate", END)
    return builder.compile()
