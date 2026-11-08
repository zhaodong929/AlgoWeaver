import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from algo_weaver.cli import app
from algo_weaver.schemas.capability import AlgorithmCapability, EvidenceRef
from algo_weaver.schemas.comparison import InventoryForecastComparisonReport
from algo_weaver.services.comparison import InventoryForecastComparator


def _capability(status: str = "draft") -> AlgorithmCapability:
    return AlgorithmCapability(
        capability_id="cap_inventory_compare",
        name="Inventory demand forecast",
        problem_definition="Forecast the next inventory demand value.",
        inputs=["sales", "window"],
        outputs=["forecast"],
        algorithm_steps=["Use preceding sales to forecast the next value."],
        evidence=[EvidenceRef(source_id="inventory-doc", excerpt="forecast demand")],
        status=status,
    )


def test_inventory_comparator_selects_lowest_metric_and_validates_status() -> None:
    report = InventoryForecastComparator().compare([18, 21, 20, 24, 22], window=3)

    assert report.overall_status == "passed"
    assert report.status == "draft"
    assert report.validation_report.overall_status == report.overall_status
    assert report.selected_candidate_id == min(
        report.candidates,
        key=lambda item: next(metric.value for metric in item.metric_report.metrics if metric.name == "mae"),
    ).candidate_id
    assert all(item.validation_report.overall_status == "passed" for item in report.candidates)


def test_comparator_preserves_verified_status_but_failed_gate_needs_review() -> None:
    verified = InventoryForecastComparator().compare(
        [18, 21, 20, 24, 22], window=3, capability=_capability("verified")
    )
    assert verified.status == "verified"

    failed = InventoryForecastComparator().compare(
        [18, 21, 20, 24, 22], window=3, max_mae=0.1, capability=_capability("verified")
    )
    assert failed.overall_status == "failed"
    assert failed.status == "needs_review"
    assert failed.validation_report.overall_status == "failed"


def test_comparison_writer_emits_json_and_markdown(tmp_path: Path) -> None:
    report = InventoryForecastComparator().compare([10, 12, 14, 13, 15], window=2)
    json_path, markdown_path = InventoryForecastComparator.write_report(
        report, tmp_path / "comparison.json"
    )

    persisted = InventoryForecastComparisonReport.model_validate_json(
        json_path.read_text(encoding="utf-8")
    )
    assert persisted.report_id == report.report_id
    assert markdown_path.exists()
    assert "Inventory forecasting candidate comparison" in markdown_path.read_text(encoding="utf-8")


def test_comparison_cli_writes_report_and_registry_status(tmp_path: Path) -> None:
    metrics = tmp_path / "sales.csv"
    metrics.write_text(
        "date,sales\n2026-10-01,18\n2026-10-02,21\n2026-10-03,20\n2026-10-04,24\n2026-10-05,22\n",
        encoding="utf-8",
    )
    capability = tmp_path / "capability.json"
    capability.write_text(_capability().model_dump_json(), encoding="utf-8")
    output = tmp_path / "report.json"
    registry = tmp_path / "registry.sqlite3"

    result = CliRunner().invoke(
        app,
        [
            "compare",
            "--metrics-file",
            str(metrics),
            "--output",
            str(output),
            "--capability-file",
            str(capability),
            "--registry",
            str(registry),
            "--candidate",
            "moving_average",
            "--candidate",
            "naive_last",
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert "Validation: passed" in result.stdout
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["registry_version"] == 1
    assert payload["status"] == "draft"
    assert (tmp_path / "report.md").exists()
    assert (tmp_path / "registry_record.json").exists()


def test_comparator_rejects_window_without_holdout() -> None:
    with pytest.raises(ValueError, match="smaller than actual length"):
        InventoryForecastComparator().compare([1, 2, 3], window=3)
