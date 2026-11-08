"""Dependency-free z-score anomaly detector for the demo fixture."""

from __future__ import annotations

import math
from collections.abc import Sequence


def detect_anomalies(
    values: Sequence[float], threshold: float = 2.0
) -> list[dict[str, float | int | bool]]:
    """Return one scored record per input value."""

    if not values:
        raise ValueError("values cannot be empty")
    if threshold <= 0:
        raise ValueError("threshold must be positive")
    mean = sum(float(value) for value in values) / len(values)
    variance = sum((float(value) - mean) ** 2 for value in values) / len(values)
    std = math.sqrt(variance)
    results: list[dict[str, float | int | bool]] = []
    for index, value in enumerate(values):
        z_score = 0.0 if std == 0 else abs(float(value) - mean) / std
        results.append(
            {
                "index": index,
                "value": float(value),
                "z_score": z_score,
                "is_anomaly": z_score > threshold,
            }
        )
    return results
