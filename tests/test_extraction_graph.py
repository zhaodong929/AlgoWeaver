import pytest

from algo_weaver.llm.mock import MockChatModel
from algo_weaver.services.capability_extractor import CapabilityExtractor


def _build_graph():
    pytest.importorskip("langgraph")
    from algo_weaver.agents.extraction_graph import build_extraction_graph

    return build_extraction_graph(CapabilityExtractor(MockChatModel()))


def test_extraction_graph_runs_end_to_end() -> None:
    graph = _build_graph()
    result = graph.invoke(
        {
            "source_text": "# 移动平均算法\n用于时间序列平滑。",
            "source_id": "doc-001",
            "source_type": "document",
        }
    )

    assert "error" not in result
    assert result["capability"]["name"] == "移动平均算法"
    assert result["capability"]["evidence"][0]["source_id"] == "doc-001"


def test_graph_returns_actionable_error_for_empty_source() -> None:
    graph = _build_graph()
    result = graph.invoke({"source_text": " ", "source_id": "doc-001"})

    assert "error" in result
    assert "source_text cannot be empty" in result["error"]
