"""Stateful reproduction workflow with an optional LangGraph backend."""

from __future__ import annotations

from typing import Any, NotRequired, TypedDict, cast

from algo_weaver.schemas.capability import AlgorithmCapability
from algo_weaver.schemas.ingestion import IngestedSource
from algo_weaver.schemas.reproduction import ReproductionPlan
from algo_weaver.schemas.retrieval import RetrievalHit
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
    capability: dict
    hits: NotRequired[list[dict]]
    plan: NotRequired[dict]
    bundle: NotRequired[dict]
    reports: NotRequired[list[dict]]
    error: NotRequired[str]


def build_reproduction_graph():
    """Build retrieve -> plan -> generate -> validate workflow."""

    def retrieve_node(state: ReproductionState) -> dict:
        source = IngestedSource.model_validate(state["source"])
        capability = AlgorithmCapability.model_validate(state["capability"])
        chunks = SourceChunker().chunk(source)
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
        bundle = TemplateArtifactWriter().generate(plan)
        return {"bundle": bundle.model_dump(mode="json")}

    def validate_node(state: ReproductionState) -> dict:
        capability = AlgorithmCapability.model_validate(state["capability"])
        bundle = state["bundle"]
        validator = ValidationService()
        reports = [validator.validate_capability(capability)]
        for artifact in bundle["artifacts"]:
            if artifact["kind"] == "python_source":
                reports.append(
                    validator.validate_python_source(
                        artifact["content"], source_id=artifact["path"]
                    )
                )
        return {"reports": [report.model_dump(mode="json") for report in reports]}

    if StateGraph is None:
        class FallbackGraph:
            def invoke(self, state: ReproductionState) -> dict:
                current: dict[str, object] = dict(state)
                for node in (retrieve_node, plan_node, generate_node, validate_node):
                    update = node(cast(ReproductionState, current))
                    current.update(update)
                    if "error" in update:
                        break
                return current

        return FallbackGraph()

    builder = StateGraph(ReproductionState)
    builder.add_node("retrieve", retrieve_node)
    builder.add_node("plan", plan_node)
    builder.add_node("generate", generate_node)
    builder.add_node("validate", validate_node)
    builder.add_edge(START, "retrieve")
    builder.add_edge("retrieve", "plan")
    builder.add_edge("plan", "generate")
    builder.add_edge("generate", "validate")
    builder.add_edge("validate", END)
    return builder.compile()
