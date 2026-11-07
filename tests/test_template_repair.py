from pathlib import Path

from algo_weaver.schemas.capability import AlgorithmCapability, EvidenceRef
from algo_weaver.schemas.execution import ExecutionResult
from algo_weaver.services.reproduction import ReproductionPlanner, TemplateArtifactWriter
from algo_weaver.services.template_repair import TemplateRepairer


def _capability() -> AlgorithmCapability:
    return AlgorithmCapability(
        name="Moving Average",
        problem_definition="Smooth a time series.",
        algorithm_family="time_series",
        inputs=["data", "window"],
        outputs=["averages"],
        algorithm_steps=["Slide a fixed window."],
        evidence=[EvidenceRef(source_id="doc-001", excerpt="moving average")],
    )


def test_template_repairer_restores_only_bundle_artifacts(tmp_path: Path) -> None:
    plan = ReproductionPlanner().build_plan(_capability())
    bundle = TemplateArtifactWriter().generate(plan)
    (tmp_path / "algorithm.py").write_text("broken", encoding="utf-8")
    failed = ExecutionResult(
        status="failed",
        command=["python", "-m", "unittest"],
        image="python:3.12-slim",
        exit_code=1,
        stderr="assertion failed",
        duration_seconds=0.1,
    )

    assert TemplateRepairer().repair(bundle, tmp_path, failed) is True
    assert "def moving_average" in (tmp_path / "algorithm.py").read_text(encoding="utf-8")


def test_template_repairer_does_not_repair_blocked_execution(tmp_path: Path) -> None:
    plan = ReproductionPlanner().build_plan(_capability())
    bundle = TemplateArtifactWriter().generate(plan)
    blocked = ExecutionResult(
        status="blocked",
        command=["python", "-m", "unittest"],
        image="python:3.12-slim",
        duration_seconds=0,
        error="Docker unavailable",
    )

    assert TemplateRepairer().repair(bundle, tmp_path, blocked) is False
