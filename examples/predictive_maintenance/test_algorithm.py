import csv
from pathlib import Path

from algorithm import binary_metrics, flag_high_risk


def test_ai4i_fixture_has_expected_shape_and_metrics() -> None:
    path = Path(__file__).with_name("ai4i2020.csv")
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))

    predictions = flag_high_risk(rows)
    metrics = binary_metrics(rows, predictions)

    assert metrics["sample_count"] == 10_000
    assert metrics["high_risk_count"] == 2
    assert metrics["false_positive"] == 0
    assert metrics["precision"] == 1.0


def test_invalid_input_is_rejected() -> None:
    try:
        flag_high_risk([], torque_threshold=70)
    except ValueError as exc:
        assert "rows cannot be empty" in str(exc)
    else:
        raise AssertionError("empty input should be rejected")
