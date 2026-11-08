from algorithm import detect_anomalies


def test_detects_sensor_spike() -> None:
    results = detect_anomalies([20.1, 20.3, 19.9, 20.2, 35.0, 20.0, 20.3])

    assert [item["index"] for item in results if item["is_anomaly"]] == [4]


def test_constant_series_has_no_anomalies() -> None:
    assert not any(item["is_anomaly"] for item in detect_anomalies([5.0, 5.0, 5.0]))


def test_rejects_invalid_inputs() -> None:
    for values, threshold in [([], 2.0), ([1.0], 0.0)]:
        try:
            detect_anomalies(values, threshold)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid input should raise ValueError")
