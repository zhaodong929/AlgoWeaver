"""LangGraph workflow for the first vertical slice: capability extraction."""

from typing import Any, NotRequired, TypedDict

from algo_weaver.schemas.capability import SourceType
from algo_weaver.services.capability_extractor import CapabilityExtractor

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
except ModuleNotFoundError:  # pragma: no cover - exercised through the CLI smoke path
    pass


class ExtractionState(TypedDict):
    source_text: str
    source_id: str
    source_type: NotRequired[SourceType]
    source_location: NotRequired[str | None]
    capability: NotRequired[dict]
    error: NotRequired[str]


def build_extraction_graph(extractor: CapabilityExtractor):
    """Build and compile a single-node extraction graph.

    This intentionally starts small. Later milestones will add ingestion,
    retrieval, validation, reproduction, execution, and repair nodes.
    """

    def extract_node(state: ExtractionState) -> dict:
        try:
            capability = extractor.extract(
                source_text=state["source_text"],
                source_id=state["source_id"],
                source_type=state.get("source_type", "unknown"),
                source_location=state.get("source_location"),
            )
            return {"capability": capability.model_dump(mode="json")}
        except Exception as exc:
            return {"error": f"{type(exc).__name__}: {exc}"}

    if StateGraph is None:
        class FallbackGraph:
            """Minimal compatible runner used when optional LangGraph is unavailable."""

            def invoke(self, state: ExtractionState) -> dict:
                return extract_node(state)

        return FallbackGraph()

    builder = StateGraph(ExtractionState)
    builder.add_node("extract_capability", extract_node)
    builder.add_edge(START, "extract_capability")
    builder.add_edge("extract_capability", END)
    return builder.compile()
