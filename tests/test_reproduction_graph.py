from pathlib import Path

from algo_weaver.agents.reproduction_graph import build_reproduction_graph
from algo_weaver.schemas.capability import AlgorithmCapability, EvidenceRef
from algo_weaver.schemas.execution import ExecutionResult
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


def test_reproduction_graph_retrieves_from_additional_sources() -> None:
    state = _state()
    state["sources"] = [
        state["source"],
        IngestedSource(
            source_id="history-code",
            path="history.py",
            source_type="code",
            source_format="python",
            content="# Moving Average history\ndef moving_average(data):\n    return data\n",
            content_sha256="c" * 64,
        ).model_dump(mode="json"),
    ]

    result = build_reproduction_graph().invoke(state)

    assert "error" not in result
    assert any(hit["chunk"]["source_id"] == "history-code" for hit in result["hits"])


def test_reproduction_graph_accepts_an_explicit_generator() -> None:
    calls: list[str] = []

    class Generator:
        def generate(self, plan, evidence=()):
            calls.append(plan.capability_name)
            from algo_weaver.services.code_generation import MockCodeGenerator

            return MockCodeGenerator().generate(plan, evidence)

    result = build_reproduction_graph(generator=Generator()).invoke(_state())

    assert calls == ["Moving Average"]
    assert result["bundle"]["plan"]["generation_mode"] == "mock"


def _state() -> dict:
    source = IngestedSource(
        source_id="doc-graph-execution",
        path="algorithm.md",
        source_type="document",
        source_format="markdown",
        content="# Moving Average\nSmooth a time series.",
        content_sha256="b" * 64,
    )
    capability = AlgorithmCapability(
        name="Moving Average",
        problem_definition="Smooth a time series.",
        algorithm_family="time_series",
        inputs=["data"],
        outputs=["averages"],
        algorithm_steps=["Slide a window."],
        evidence=[EvidenceRef(source_id=source.source_id, excerpt="Moving Average")],
    )
    return {
        "source": source.model_dump(mode="json"),
        "capability": capability.model_dump(mode="json"),
    }


def _execution(status: str, error: str | None = None) -> ExecutionResult:
    return ExecutionResult(
        status=status,
        command=["python", "-m", "unittest"],
        image="python:3.12-slim",
        exit_code=0 if status == "passed" else 1,
        duration_seconds=0.1,
        error=error,
    )


def test_reproduction_graph_executes_injected_runner_and_reports_runtime(
    tmp_path: Path,
) -> None:
    calls: list[Path] = []

    def runner(workspace: Path) -> ExecutionResult:
        calls.append(workspace)
        return _execution("passed")

    result = build_reproduction_graph(workspace=tmp_path, runner=runner).invoke(_state())

    assert calls == [tmp_path]
    assert (tmp_path / "algorithm.py").exists()
    assert result["execution"]["status"] == "passed"
    assert result["reports"][-1]["target_type"] == "capability"
    assert result["reports"][-1]["overall_status"] == "passed"


def test_reproduction_graph_repairs_failed_execution_with_bounded_callback(
    tmp_path: Path,
) -> None:
    executions = iter([_execution("failed", "assertion failed"), _execution("passed")])
    repairs: list[str] = []

    def runner(_workspace: Path) -> ExecutionResult:
        return next(executions)

    def repair(_bundle, _workspace: Path, observation: ExecutionResult) -> bool:
        repairs.append(observation.status)
        return True

    result = build_reproduction_graph(
        workspace=tmp_path,
        runner=runner,
        repair=repair,
        max_repair_attempts=1,
    ).invoke(_state())

    assert repairs == ["failed"]
    assert result["execution"]["status"] == "passed"
    assert result["repair_result"]["final_status"] == "passed"


def test_reproduction_graph_stops_after_repair_budget(tmp_path: Path) -> None:
    def runner(_workspace: Path) -> ExecutionResult:
        return _execution("failed", "still broken")

    result = build_reproduction_graph(
        workspace=tmp_path,
        runner=runner,
        repair=lambda _bundle, _workspace, _observation: True,
        max_repair_attempts=2,
    ).invoke(_state())

    assert result["repair_result"]["final_status"] == "exhausted"
    assert len(result["repair_result"]["attempts"]) == 2
    assert result["execution"]["status"] == "failed"
