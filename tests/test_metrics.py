import pytest

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
