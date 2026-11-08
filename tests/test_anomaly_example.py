import csv
import importlib.util
from collections.abc import Callable
from pathlib import Path

from algo_weaver.schemas.capability import AlgorithmCapability

EXAMPLE_DIR = Path(__file__).parents[1] / "examples" / "anomaly_detection"


def _load_detector() -> Callable:
    spec = importlib.util.spec_from_file_location("anomaly_demo", EXAMPLE_DIR / "algorithm.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load anomaly demo")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.detect_anomalies


def test_anomaly_fixture_and_capability_card_are_consistent() -> None:
    with (EXAMPLE_DIR / "sensor_readings.csv").open(newline="", encoding="utf-8") as handle:
        values = [float(row["value"]) for row in csv.DictReader(handle)]
    results = _load_detector()(values)
    capability = AlgorithmCapability.model_validate_json(
        (EXAMPLE_DIR / "reviewed_capability.json").read_text(encoding="utf-8")
    )

    assert capability.algorithm_family == "anomaly_detection"
    assert sum(bool(item["is_anomaly"]) for item in results) == 1
    assert results[8]["is_anomaly"] is True

