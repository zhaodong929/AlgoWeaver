"""Dependency-free regression metric evaluation."""

from __future__ import annotations

import math
from collections.abc import Sequence

from algo_weaver.schemas.metrics import MetricReport, MetricResult


class RegressionMetricEvaluator:
    """Compute deterministic MAE and RMSE for a configured task."""

    def evaluate(
        self,
        actual: Sequence[float],
        predicted: Sequence[float],
        *,
        task: str = "regression",
        max_mae: float | None = None,
        max_rmse: float | None = None,
    ) -> MetricReport:
        if not actual or len(actual) != len(predicted):
            raise ValueError("actual and predicted must be non-empty and have equal length")
        errors = [
            float(prediction) - float(observed)
            for observed, prediction in zip(actual, predicted, strict=True)
        ]
        mae = sum(abs(error) for error in errors) / len(errors)
        rmse = math.sqrt(sum(error * error for error in errors) / len(errors))
        metrics = [
            MetricResult(name="mae", value=mae, threshold=max_mae, passed=None if max_mae is None else mae <= max_mae),
            MetricResult(name="rmse", value=rmse, threshold=max_rmse, passed=None if max_rmse is None else rmse <= max_rmse),
        ]
        bounded = [metric.passed for metric in metrics if metric.passed is not None]
        overall = "passed" if bounded and all(bounded) else "failed" if bounded else "unscored"
        return MetricReport(task=task, sample_count=len(actual), metrics=metrics, overall_status=overall)
