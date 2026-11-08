"""Deterministic binary classification metric evaluation."""

from __future__ import annotations

from collections.abc import Sequence

from algo_weaver.schemas.metrics import MetricReport, MetricResult


class ClassificationMetricEvaluator:
    """Compute accuracy, precision, recall and F1 for binary labels."""

    def evaluate(
        self,
        actual: Sequence[int | bool],
        predicted: Sequence[int | bool],
        *,
        task: str = "binary_classification",
        min_accuracy: float | None = None,
        min_precision: float | None = None,
        min_recall: float | None = None,
        min_f1: float | None = None,
    ) -> MetricReport:
        if not actual or len(actual) != len(predicted):
            raise ValueError("actual and predicted must be non-empty and have equal length")
        actual_values = [_label(value, "actual") for value in actual]
        predicted_values = [_label(value, "predicted") for value in predicted]
        true_positive = sum(
            observed == 1 and estimate == 1
            for observed, estimate in zip(actual_values, predicted_values, strict=True)
        )
        true_negative = sum(
            observed == 0 and estimate == 0
            for observed, estimate in zip(actual_values, predicted_values, strict=True)
        )
        false_positive = sum(
            observed == 0 and estimate == 1
            for observed, estimate in zip(actual_values, predicted_values, strict=True)
        )
        false_negative = sum(
            observed == 1 and estimate == 0
            for observed, estimate in zip(actual_values, predicted_values, strict=True)
        )
        sample_count = len(actual_values)
        accuracy = (true_positive + true_negative) / sample_count
        precision = _ratio(true_positive, true_positive + false_positive)
        recall = _ratio(true_positive, true_positive + false_negative)
        f1 = _ratio(2 * precision * recall, precision + recall)
        metrics = [
            MetricResult(name="accuracy", value=accuracy, threshold=min_accuracy, passed=_passes(accuracy, min_accuracy)),
            MetricResult(name="precision", value=precision, threshold=min_precision, passed=_passes(precision, min_precision)),
            MetricResult(name="recall", value=recall, threshold=min_recall, passed=_passes(recall, min_recall)),
            MetricResult(name="f1", value=f1, threshold=min_f1, passed=_passes(f1, min_f1)),
        ]
        bounded = [metric.passed for metric in metrics if metric.passed is not None]
        overall = "passed" if bounded and all(bounded) else "failed" if bounded else "unscored"
        return MetricReport(task=task, sample_count=sample_count, metrics=metrics, overall_status=overall)


def _label(value: int | bool, name: str) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int) and value in {0, 1}:
        return value
    raise ValueError(f"{name} labels must be binary 0/1 values")


def _ratio(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def _passes(value: float, threshold: float | None) -> bool | None:
    return None if threshold is None else value >= threshold
