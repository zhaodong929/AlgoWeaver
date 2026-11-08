import pytest

from algo_weaver.services.classification_metrics import ClassificationMetricEvaluator
from algo_weaver.services.metrics import RegressionMetricEvaluator


def test_regression_metrics_compute_and_apply_thresholds() -> None:
    report = RegressionMetricEvaluator().evaluate(
        [10, 12, 14],
        [11, 11, 15],
        task="inventory_demand",
        max_mae=1.0,
        max_rmse=1.0,
    )

    assert report.sample_count == 3
    assert report.overall_status == "passed"
    assert report.metrics[0].name == "mae"


def test_regression_metrics_reject_empty_or_mismatched_inputs() -> None:
    with pytest.raises(ValueError):
        RegressionMetricEvaluator().evaluate([], [])
    with pytest.raises(ValueError):
        RegressionMetricEvaluator().evaluate([1], [1, 2])


def test_classification_metrics_compute_and_apply_thresholds() -> None:
    report = ClassificationMetricEvaluator().evaluate(
        [1, 0, 1, 0],
        [1, 0, 0, 0],
        task="predictive_maintenance",
        min_accuracy=0.75,
        min_precision=0.9,
        min_recall=0.9,
    )

    assert report.sample_count == 4
    assert report.overall_status == "failed"
    assert {metric.name for metric in report.metrics} == {"accuracy", "precision", "recall", "f1"}


def test_classification_metrics_accept_bool_labels_and_reject_invalid_inputs() -> None:
    report = ClassificationMetricEvaluator().evaluate([True, False], [1, 0])
    assert report.overall_status == "unscored"
    with pytest.raises(ValueError):
        ClassificationMetricEvaluator().evaluate([0], [2])
    with pytest.raises(ValueError):
        ClassificationMetricEvaluator().evaluate([0], [0, 1])
