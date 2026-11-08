import json

import pytest
import typer
from typer.testing import CliRunner

from algo_weaver.cli import app, reproduce
from algo_weaver.schemas.capability import AlgorithmCapability, EvidenceRef
from algo_weaver.schemas.execution import ExecutionResult
from algo_weaver.schemas.validation import ValidationCheck, ValidationReport
from algo_weaver.services.registry import CapabilityRegistry


def test_version_command() -> None:
    result = CliRunner().invoke(app, ["version"])
    assert result.exit_code == 0
    assert "AlgoWeaver 0.1.0" in result.stdout


def test_reproduce_command_writes_unverified_bundle(tmp_path) -> None:
    source = tmp_path / "algorithm.md"
    source.write_text("# 移动平均算法\n用于时间序列平滑。", encoding="utf-8")
    output_dir = tmp_path / "bundle"

    result = CliRunner().invoke(
        app,
        [
            "reproduce",
            "--input",
            str(source),
            "--output-dir",
            str(output_dir),
            "--mode",
            "mock",
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert "unverified" in result.stdout
    assert (output_dir / "algorithm.py").exists()
    assert (output_dir / "test_algorithm.py").exists()
    assert (output_dir / "reproduction_bundle.json").exists()
    assert (output_dir / "validation_reports.json").exists()


def test_reproduce_command_accepts_additional_input(tmp_path) -> None:
    source = tmp_path / "algorithm.md"
    source.write_text("# 移动平均算法\n用于时间序列平滑。", encoding="utf-8")
    history = tmp_path / "history.py"
    history.write_text(
        "# 移动平均算法历史代码\ndef moving_average(data):\n    return data",
        encoding="utf-8",
    )
    output_dir = tmp_path / "bundle"

    result = CliRunner().invoke(
        app,
        [
            "reproduce",
            "--input",
            str(source),
            "--additional-input",
            str(history),
            "--output-dir",
            str(output_dir),
            "--mode",
            "mock",
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert "1 ingested" in result.stdout
    assert (output_dir / "ingestion_batch.json").exists()


def test_reproduce_command_accepts_mock_generation_mode(tmp_path) -> None:
    source = tmp_path / "algorithm.md"
    source.write_text("# 移动平均算法\n用于时间序列平滑。", encoding="utf-8")
    output_dir = tmp_path / "bundle"

    result = CliRunner().invoke(
        app,
        [
            "reproduce",
            "--input",
            str(source),
            "--output-dir",
            str(output_dir),
            "--generation-mode",
            "mock",
        ],
    )

    assert result.exit_code == 0, result.stdout
    bundle = json.loads((output_dir / "reproduction_bundle.json").read_text(encoding="utf-8"))
    assert bundle["plan"]["generation_mode"] == "mock"


def test_reproduce_command_requires_litellm_for_llm_generation(tmp_path) -> None:
    source = tmp_path / "algorithm.md"
    source.write_text("# Moving Average\nSmooth a time series.", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "reproduce",
            "--input",
            str(source),
            "--generation-mode",
            "llm",
        ],
    )

    assert result.exit_code == 2
    with pytest.raises(typer.BadParameter, match="requires --mode litellm"):
        reproduce(input_file=source, generation_mode="llm")


def test_reproduce_command_requires_litellm_for_llm_repair(tmp_path) -> None:
    source = tmp_path / "algorithm.md"
    source.write_text("# Moving Average\nSmooth a time series.", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "reproduce",
            "--input",
            str(source),
            "--repair",
            "--repair-mode",
            "llm",
        ],
    )

    assert result.exit_code == 2
    with pytest.raises(typer.BadParameter, match="requires --mode litellm"):
        reproduce(input_file=source, repair=True, repair_mode="llm")


def test_reproduce_accepts_an_explicit_reviewed_capability_file(tmp_path) -> None:
    source = tmp_path / "algorithm.md"
    source.write_text("# Moving Average\nSmooth a time series.", encoding="utf-8")
    capability = tmp_path / "capability.json"
    capability.write_text(
        '{"name":"Moving Average","problem_definition":"Smooth a time series.",'
        '"inputs":["data"],"outputs":["averages"],"algorithm_steps":["Slide a window."],'
        '"evidence":[{"source_id":"doc-001","source_type":"document","excerpt":"source"}],'
        '"status":"draft"}',
        encoding="utf-8",
    )
    output_dir = tmp_path / "bundle"

    result = CliRunner().invoke(
        app,
        [
            "reproduce",
            "--input",
            str(source),
            "--output-dir",
            str(output_dir),
            "--capability-file",
            str(capability),
            "--mode",
            "mock",
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert "reviewed capability card" in result.stdout


def test_reproduce_does_not_promote_when_metric_gate_fails(tmp_path, monkeypatch) -> None:
    source = tmp_path / "algorithm.md"
    source.write_text("# Moving Average\nSmooth a time series.", encoding="utf-8")
    capability = tmp_path / "capability.json"
    capability.write_text(
        '{"capability_id":"metric_gate_cli","name":"Moving Average",'
        '"problem_definition":"Smooth a time series.","inputs":["data"],'
        '"outputs":["averages"],"algorithm_steps":["Slide a window."],'
        '"evidence":[{"source_id":"doc-001","source_type":"document",'
        '"excerpt":"source"}],"status":"draft"}',
        encoding="utf-8",
    )
    output_dir = tmp_path / "bundle"
    registry_path = tmp_path / "registry.sqlite3"

    class FakeRunner:
        def run(self, workspace, command, policy):
            stdout = "[12.0, 12.0, 12.0, 12.0]" if command[:2] == ["python", "-c"] else ""
            return ExecutionResult(
                status="passed",
                command=command,
                image="python:3.12-slim",
                exit_code=0,
                stdout=stdout,
                duration_seconds=0.1,
            )

    monkeypatch.setattr("algo_weaver.cli.DockerSandboxRunner", FakeRunner)
    result = CliRunner().invoke(
        app,
        [
            "reproduce",
            "--input",
            str(source),
            "--output-dir",
            str(output_dir),
            "--capability-file",
            str(capability),
            "--registry",
            str(registry_path),
            "--execute",
            "--metrics-file",
            "examples/inventory_forecast/sales_history.csv",
            "--metrics-window",
            "2",
            "--max-mae",
            "0.1",
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert "Verification status: unverified" in result.stdout
    record = json.loads((output_dir / "registry_record.json").read_text(encoding="utf-8"))
    assert record["status"] != "verified"
    metric_report = json.loads((output_dir / "metric_report.json").read_text(encoding="utf-8"))
    assert metric_report["overall_status"] == "failed"


def test_reuse_command_returns_verified_capabilities_only(tmp_path) -> None:
    registry_path = tmp_path / "capabilities.sqlite3"
    registry = CapabilityRegistry(registry_path)
    capability = AlgorithmCapability(
        capability_id="cap_reuse_cli",
        name="Inventory Forecast",
        problem_definition="Forecast demand.",
        inputs=["sales"],
        outputs=["forecast"],
        algorithm_steps=["Average recent sales."],
        evidence=[EvidenceRef(source_id="doc", excerpt="forecast")],
    )
    registry.save(capability)
    report = ValidationReport(
        target_type="capability",
        target_id=capability.capability_id,
        checks=[
            ValidationCheck(
                check_id="pass",
                name="pass",
                status="passed",
                message="pass",
            )
        ],
        overall_status="passed",
    )
    registry.promote_verified(capability.capability_id, report)

    result = CliRunner().invoke(
        app,
        ["reuse", "Inventory", "--registry", str(registry_path)],
    )

    assert result.exit_code == 0, result.stdout
    assert "cap_reuse_cli" in result.stdout
    assert "verified" in result.stdout


def test_reproduce_can_select_a_verified_capability_for_reuse(tmp_path) -> None:
    source = tmp_path / "algorithm.md"
    source.write_text("# Inventory forecast\n", encoding="utf-8")
    capability = tmp_path / "capability.json"
    capability.write_text(
        '{"capability_id":"cap_reuse_run","name":"Inventory Forecast",'
        '"problem_definition":"Forecast demand.","inputs":["sales"],'
        '"outputs":["forecast"],"algorithm_steps":["Average recent sales."],'
        '"evidence":[{"source_id":"doc","source_type":"document","excerpt":"forecast"}],'
        '"status":"draft"}',
        encoding="utf-8",
    )
    registry_path = tmp_path / "capabilities.sqlite3"
    registry = CapabilityRegistry(registry_path)
    saved = registry.save(AlgorithmCapability.model_validate_json(capability.read_text()))
    registry.promote_verified(
        saved.capability_id,
        ValidationReport(
            target_type="capability",
            target_id=saved.capability_id,
            checks=[ValidationCheck(check_id="p", name="p", status="passed", message="p")],
            overall_status="passed",
        ),
    )
    output_dir = tmp_path / "bundle"

    result = CliRunner().invoke(
        app,
        [
            "reproduce",
            "--input",
            str(source),
            "--output-dir",
            str(output_dir),
            "--registry",
            str(registry_path),
            "--reuse-query",
            "Inventory",
            "--mode",
            "mock",
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert "Reusing verified capability" in result.stdout
