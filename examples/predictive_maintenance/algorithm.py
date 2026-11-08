"""Transparent rule baseline for the UCI predictive-maintenance scenario."""

from __future__ import annotations

from collections.abc import Mapping, Sequence


def flag_high_risk(
    rows: Sequence[Mapping[str, str]],
    *,
    torque_threshold: float = 70.0,
    wear_threshold: float = 180.0,
) -> list[dict[str, float | int | bool]]:
    """Return one risk decision for every UCI AI4I row."""

    if torque_threshold <= 0 or wear_threshold <= 0:
        raise ValueError("thresholds must be positive")
    if not rows:
        raise ValueError("rows cannot be empty")
    results: list[dict[str, float | int | bool]] = []
    for index, row in enumerate(rows):
        try:
            torque = float(row["Torque [Nm]"])
            wear = float(row["Tool wear [min]"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("rows must contain numeric torque and tool wear") from exc
        score = float(torque >= torque_threshold) + float(wear >= wear_threshold)
        results.append(
            {
                "index": index,
                "torque": torque,
                "tool_wear": wear,
                "risk_score": score,
                "is_high_risk": score == 2.0,
            }
        )
    return results


def binary_metrics(
    rows: Sequence[Mapping[str, str]], predictions: Sequence[Mapping[str, object]]
) -> dict[str, float | int]:
    """Compute deterministic precision/recall against the published label."""

    if len(rows) != len(predictions):
        raise ValueError("rows and predictions must have equal length")
    true_values = [row.get("Machine failure") == "1" for row in rows]
    predicted_values = [bool(item["is_high_risk"]) for item in predictions]
    true_positive = sum(actual and predicted for actual, predicted in zip(true_values, predicted_values, strict=True))
    false_positive = sum((not actual) and predicted for actual, predicted in zip(true_values, predicted_values, strict=True))
    false_negative = sum(actual and (not predicted) for actual, predicted in zip(true_values, predicted_values, strict=True))
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    return {
        "sample_count": len(rows),
        "high_risk_count": sum(predicted_values),
        "true_positive": true_positive,
        "false_positive": false_positive,
        "precision": precision,
        "recall": recall,
    }
