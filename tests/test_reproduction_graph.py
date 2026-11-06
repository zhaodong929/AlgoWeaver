from algo_weaver.agents.reproduction_graph import build_reproduction_graph
from algo_weaver.schemas.capability import AlgorithmCapability, EvidenceRef
from algo_weaver.schemas.ingestion import IngestedSource


def test_reproduction_graph_runs_without_executing_artifacts() -> None:
    source = IngestedSource(
        source_id="doc-graph",
        path="algorithm.md",
        source_type="document",
        source_format="markdown",
        content="# Moving Average\nSmooth a time series.",
        content_sha256="a" * 64,
    )
    capability = AlgorithmCapability(
        name="Moving Average",
        problem_definition="Smooth a time series.",
        algorithm_family="time_series",
        inputs=["data"],
        outputs=["averages"],
        algorithm_steps=["Slide a window."],
        evidence=[EvidenceRef(source_id="doc-graph", excerpt="Moving Average")],
    )

    result = build_reproduction_graph().invoke(
        {"source": source.model_dump(mode="json"), "capability": capability.model_dump(mode="json")}
    )

    assert "error" not in result
    assert result["plan"]["status"] == "ready"
    assert result["bundle"]["artifacts"][0]["verification_status"] == "unverified"
    assert result["reports"]
