"""Deterministic candidate comparison for the inventory forecasting scenario."""

from __future__ import annotations

import json
import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from algo_weaver.schemas.capability import AlgorithmCapability, CapabilityStatus
from algo_weaver.schemas.comparison import (
    ForecastCandidateResult,
    InventoryForecastComparisonReport,
)
from algo_weaver.schemas.metrics import MetricReport
from algo_weaver.schemas.validation import ValidationCheck, ValidationReport
from algo_weaver.services.metrics import RegressionMetricEvaluator

ForecastFn = Callable[[list[float], int], list[float]]


@dataclass(frozen=True)
class ForecastCandidate:
    """A local, dependency-free candidate implementation."""

    candidate_id: str
    name: str
    algorithm_family: str
    description: str
    forecast: ForecastFn


def _moving_average_forecast(values: list[float], window: int) -> list[float]:
    """Predict each holdout point from the preceding fixed window."""

    return [
        sum(values[index : index + window]) / window
        for index in range(len(values) - window)
    ]


def _naive_last_forecast(values: list[float], window: int) -> list[float]:
    """Use the most recent observed value as the next-period forecast."""

    return [values[index + window - 1] for index in range(len(values) - window)]


def _weighted_moving_average_forecast(values: list[float], window: int) -> list[float]:
    """Predict with linearly increasing weights over the preceding window."""

    denominator = window * (window + 1) / 2
    return [
        sum((offset + 1) * values[index + offset] for offset in range(window))
        / denominator
        for index in range(len(values) - window)
    ]


DEFAULT_INVENTORY_CANDIDATES: tuple[ForecastCandidate, ...] = (
    ForecastCandidate(
        candidate_id="moving_average",
        name="Fixed-window moving average",
        algorithm_family="time_series",
        description="Mean of the preceding observations in a fixed window.",
        forecast=_moving_average_forecast,
    ),
    ForecastCandidate(
        candidate_id="naive_last",
        name="Last-observation baseline",
        algorithm_family="baseline",
        description="Uses the most recent observation as the next forecast.",
        forecast=_naive_last_forecast,
    ),
    ForecastCandidate(
        candidate_id="weighted_moving_average",
        name="Weighted moving average",
        algorithm_family="time_series",
        description="Weights newer observations more heavily than older ones.",
        forecast=_weighted_moving_average_forecast,
    ),
)


class InventoryForecastComparator:
    """Compare local forecasting candidates with one reproducible metric gate."""

    def __init__(
        self,
        candidates: Sequence[ForecastCandidate] | None = None,
        *,
        metric_evaluator: RegressionMetricEvaluator | None = None,
    ) -> None:
        selected = tuple(candidates or DEFAULT_INVENTORY_CANDIDATES)
        if not selected:
            raise ValueError("at least one forecasting candidate is required")
        candidate_ids = [candidate.candidate_id for candidate in selected]
        if len(candidate_ids) != len(set(candidate_ids)):
            raise ValueError("candidate_id values must be unique")
        self.candidates = selected
        self.metric_evaluator = metric_evaluator or RegressionMetricEvaluator()

    def compare(
        self,
        actual: Sequence[float],
        *,
        window: int = 3,
        selection_metric: str = "mae",
        max_mae: float | None = None,
        max_rmse: float | None = None,
        capability: AlgorithmCapability | None = None,
    ) -> InventoryForecastComparisonReport:
        """Evaluate candidates on a one-step-ahead holdout and select a winner.

        The first ``window`` observations form the initial context. Each later
        observation is evaluated against a forecast made without seeing that
        target, which keeps candidate comparison free of target leakage.
        """

        values = [float(value) for value in actual]
        if len(values) < 2:
            raise ValueError("actual must contain at least two observations")
        if not 1 <= window < len(values):
            raise ValueError("window must be positive and smaller than actual length")
        if selection_metric not in {"mae", "rmse"}:
            raise ValueError("selection_metric must be 'mae' or 'rmse'")
        if not all(math.isfinite(value) for value in values):
            raise ValueError("actual values must be finite")

        target = values[window:]
        results: list[ForecastCandidateResult] = []
        for candidate in self.candidates:
            predictions = [float(value) for value in candidate.forecast(values, window)]
            metric_report = self.metric_evaluator.evaluate(
                target,
                predictions,
                task="inventory_demand",
                max_mae=max_mae,
                max_rmse=max_rmse,
            )
            checks = [
                ValidationCheck(
                    check_id="candidate.prediction_length",
                    name="Prediction length",
                    status="passed" if len(predictions) == len(target) else "failed",
                    message=(
                        "Candidate returned one prediction for every holdout observation."
                        if len(predictions) == len(target)
                        else "Candidate prediction length does not match the holdout."
                    ),
                    details={"expected": len(target), "actual": len(predictions)},
                ),
                ValidationCheck(
                    check_id="candidate.finite_predictions",
                    name="Finite predictions",
                    status="passed" if all(math.isfinite(value) for value in predictions) else "failed",
                    message=(
                        "All candidate predictions are finite."
                        if all(math.isfinite(value) for value in predictions)
                        else "Candidate returned a non-finite prediction."
                    ),
                ),
                ValidationCheck(
                    check_id="candidate.metric_gate",
                    name="Metric gate",
                    status="passed" if metric_report.overall_status != "failed" else "failed",
                    message=(
                        "Candidate metrics satisfy configured thresholds."
                        if metric_report.overall_status != "failed"
                        else "Candidate metrics exceeded at least one configured threshold."
                    ),
                ),
            ]
            validation = _validation_report(candidate.candidate_id, checks)
            results.append(
                ForecastCandidateResult(
                    candidate_id=candidate.candidate_id,
                    name=candidate.name,
                    algorithm_family=candidate.algorithm_family,
                    predictions=predictions,
                    metric_report=metric_report,
                    validation_report=validation,
                )
            )

        valid_results = [
            result for result in results if result.validation_report.overall_status == "passed"
        ]
        winner = None
        if valid_results:
            winner = min(
                valid_results,
                key=lambda result: (
                    _metric_value(result.metric_report, selection_metric),
                    result.candidate_id,
                ),
            )
        overall_status = "failed" if len(valid_results) != len(results) else "passed"
        report_id = f"cmp_{uuid4().hex[:12]}"
        comparison_checks = [
            ValidationCheck(
                check_id="comparison.candidates",
                name="Candidate validation",
                status="passed" if overall_status == "passed" else "failed",
                message=(
                    "All candidates produced valid predictions and passed metric gates."
                    if overall_status == "passed"
                    else "At least one candidate failed prediction or metric validation."
                ),
                details={"candidate_count": len(results), "valid_count": len(valid_results)},
            ),
            ValidationCheck(
                check_id="comparison.selection",
                name="Candidate selection",
                status="passed" if winner is not None else "failed",
                message=(
                    f"Selected '{winner.candidate_id}' by lowest {selection_metric}."
                    if winner is not None
                    else "No valid candidate was available for selection."
                ),
                details={"selection_metric": selection_metric},
            ),
        ]
        validation_report = _validation_report(report_id, comparison_checks, target_type="comparison")
        capability_status: CapabilityStatus = capability.status if capability else "draft"
        if overall_status == "failed":
            capability_status = "needs_review"
        return InventoryForecastComparisonReport(
            report_id=report_id,
            window=window,
            actual=values,
            evaluation_target=target,
            candidates=results,
            selected_candidate_id=winner.candidate_id if winner else None,
            selection_metric=selection_metric,  # type: ignore[arg-type]
            validation_report=validation_report,
            overall_status=overall_status,  # type: ignore[arg-type]
            status=capability_status,
            capability_id=capability.capability_id if capability else None,
            notes=[
                "Evaluation uses one-step-ahead forecasts from the preceding window.",
                "A passing comparison does not independently promote a capability to verified.",
            ],
        )

    @staticmethod
    def write_report(
        report: InventoryForecastComparisonReport,
        output_file: str | Path,
        *,
        markdown_file: str | Path | None = None,
    ) -> tuple[Path, Path]:
        """Write JSON and a human-readable Markdown companion artifact."""

        json_path = Path(output_file)
        if json_path.suffix.lower() != ".json":
            json_path = json_path.with_suffix(".json")
        markdown_path = Path(markdown_file) if markdown_file else json_path.with_suffix(".md")
        json_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(
            json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        markdown_path.write_text(_render_markdown(report), encoding="utf-8")
        return json_path, markdown_path


def _metric_value(report: MetricReport, metric_name: str) -> float:
    for metric in report.metrics:
        if metric.name == metric_name:
            return metric.value
    raise ValueError(f"metric not found: {metric_name}")


def _validation_report(
    target_id: str,
    checks: list[ValidationCheck],
    *,
    target_type: str = "comparison",
) -> ValidationReport:
    statuses = {check.status for check in checks}
    overall = "failed" if "failed" in statuses else "partial" if "skipped" in statuses else "passed"
    return ValidationReport(
        target_type=target_type,  # type: ignore[arg-type]
        target_id=target_id,
        checks=checks,
        overall_status=overall,  # type: ignore[arg-type]
    )


def _render_markdown(report: InventoryForecastComparisonReport) -> str:
    lines = [
        "# Inventory forecasting candidate comparison",
        "",
        f"- Report: `{report.report_id}`",
        f"- Status: **{report.status}**",
        f"- Validation: **{report.overall_status}**",
        f"- Window: `{report.window}`",
        f"- Selection metric: `{report.selection_metric}`",
        f"- Selected candidate: `{report.selected_candidate_id or 'none'}`",
        "",
        "| Candidate | Family | MAE | RMSE | Validation |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for candidate in report.candidates:
        metrics = {metric.name: metric.value for metric in candidate.metric_report.metrics}
        lines.append(
            f"| {candidate.name} (`{candidate.candidate_id}`) | {candidate.algorithm_family} "
            f"| {metrics.get('mae', float('nan')):.4f} | {metrics.get('rmse', float('nan')):.4f} "
            f"| {candidate.validation_report.overall_status} |"
        )
    lines.extend(["", "## Validation checks", ""])
    for check in report.validation_report.checks:
        lines.append(f"- **{check.status}** `{check.name}` — {check.message}")
    lines.extend(["", "## Notes", ""])
    lines.extend(f"- {note}" for note in report.notes)
    return "\n".join(lines) + "\n"


__all__ = [
    "DEFAULT_INVENTORY_CANDIDATES",
    "ForecastCandidate",
    "InventoryForecastComparator",
]
