import csv
import importlib.util
from pathlib import Path

EXAMPLE_DIR = Path(__file__).parents[1] / "examples" / "predictive_maintenance"


def _load_module():
    spec = importlib.util.spec_from_file_location("ai4i_demo", EXAMPLE_DIR / "algorithm.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load AI4I demo")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_ai4i_open_dataset_rule_baseline() -> None:
    with (EXAMPLE_DIR / "ai4i2020.csv").open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    module = _load_module()
    predictions = module.flag_high_risk(rows)
    metrics = module.binary_metrics(rows, predictions)

    assert metrics["sample_count"] == 10_000
    assert metrics["high_risk_count"] == 2
    assert metrics["precision"] == 1.0

