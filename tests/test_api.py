import json

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from algo_weaver.api import create_app
from algo_weaver.config import Settings
from algo_weaver.schemas.execution import ExecutionResult
from algo_weaver.services.registry import CapabilityRegistry


def test_health_endpoint() -> None:
    response = TestClient(create_app()).get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_metrics_endpoint_returns_thresholded_report() -> None:
    response = TestClient(create_app()).post(
        "/metrics",
        json={
            "task": "inventory_demand",
            "actual": [10, 12, 14],
            "predicted": [11, 11, 15],
            "max_mae": 1.0,
            "max_rmse": 1.0,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["sample_count"] == 3
    assert payload["overall_status"] == "passed"
    assert payload["metrics"][0]["name"] == "mae"


def test_metrics_endpoint_reports_threshold_failure() -> None:
    response = TestClient(create_app()).post(
        "/metrics",
        json={
            "actual": [0, 0],
            "predicted": [2, 0],
            "max_mae": 0.5,
        },
    )

    assert response.status_code == 200
    assert response.json()["overall_status"] == "failed"


def test_metrics_endpoint_rejects_mismatched_lengths() -> None:
    response = TestClient(create_app()).post(
        "/metrics",
        json={"actual": [1], "predicted": [1, 2]},
    )

    assert response.status_code == 400
    assert "equal length" in response.json()["detail"]


def test_extract_endpoint_uses_mock_by_default() -> None:
    response = TestClient(create_app()).post(
        "/extract",
        json={
            "source_text": "# 移动平均算法\n用于时间序列平滑。",
            "source_id": "api-doc-001",
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "移动平均算法"
    assert response.json()["status"] == "needs_review"


def test_reproduce_endpoint_returns_unverified_bundle() -> None:
    response = TestClient(create_app()).post(
        "/reproduce",
        json={
            "source_text": "# 移动平均算法\n用于时间序列平滑。",
            "source_id": "api-doc-002",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["plan"]["status"] == "ready"
    assert payload["bundle"]["artifacts"][0]["verification_status"] == "unverified"
    assert payload["dependency_reports"]


def test_reproduce_endpoint_exposes_mock_generation_mode() -> None:
    response = TestClient(create_app()).post(
        "/reproduce",
        json={
            "source_text": "# 移动平均算法\n用于时间序列平滑。",
            "source_id": "api-generation-mode",
            "generation_mode": "mock",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["plan"]["generation_mode"] == "mock"
    assert payload["bundle"]["artifacts"][0]["generation_mode"] == "mock"


def test_reproduce_endpoint_requires_litellm_for_llm_generation() -> None:
    response = TestClient(create_app()).post(
        "/reproduce",
        json={
            "source_text": "# moving average\nSmooth a time series.",
            "source_id": "api-llm-mode",
            "generation_mode": "llm",
        },
    )

    assert response.status_code == 400
    assert "requires mode='litellm'" in response.json()["detail"]


def test_reproduce_endpoint_requires_litellm_for_llm_repair() -> None:
    response = TestClient(create_app()).post(
        "/reproduce",
        json={
            "source_text": "# moving average\nSmooth a time series.",
            "source_id": "api-llm-repair-mode",
            "execute": True,
            "repair": True,
            "repair_mode": "llm",
        },
    )

    assert response.status_code == 400
    assert "requires mode='litellm'" in response.json()["detail"]


def test_reproduce_endpoint_collects_metrics_inside_sandbox() -> None:
    def runner(_backend: str, _workspace) -> ExecutionResult:
        return ExecutionResult(
            status="passed",
            command=["python", "-m", "unittest"],
            image="python:3.12-slim",
            exit_code=0,
            duration_seconds=0.1,
        )

    def metric_runner(_backend: str, workspace, command: list[str]) -> ExecutionResult:
        assert (workspace / "metric_input.json").exists()
        assert command[:2] == ["python", "-c"]
        return ExecutionResult(
            status="passed",
            command=command,
            image="python:3.12-slim",
            exit_code=0,
            stdout=json.dumps([11.0, 13.0, 15.0]),
            duration_seconds=0.1,
        )

    response = TestClient(
        create_app(execution_runner=runner, metric_runner=metric_runner)
    ).post(
        "/reproduce",
        json={
            "source_text": "# 移动平均算法\n用于时间序列平滑。",
            "source_id": "api-sandbox-metrics",
            "execute": True,
            "metrics": {
                "actual": [10.0, 12.0, 14.0, 16.0],
                "window": 2,
                "max_mae": 1.0,
                "max_rmse": 1.0,
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["metric_execution"]["status"] == "passed"
    assert payload["metric_report"]["sample_count"] == 3
    assert payload["metric_report"]["overall_status"] == "passed"


def test_reproduce_endpoint_requires_execution_for_sandbox_metrics() -> None:
    response = TestClient(create_app()).post(
        "/reproduce",
        json={
            "source_text": "# moving average\nSmooth a time series.",
            "source_id": "api-metrics-static",
            "metrics": {"actual": [1.0, 2.0, 3.0]},
        },
    )

    assert response.status_code == 400
    assert "requires execute=true" in response.json()["detail"]


def test_reproduce_endpoint_retrieves_additional_sources() -> None:
    response = TestClient(create_app()).post(
        "/reproduce",
        json={
            "source_text": "# 移动平均算法\n预测库存需求。",
            "source_id": "api-doc-multi",
            "additional_sources": [
                {
                    "source_text": "# 移动平均算法历史代码\ndef moving_average(data):\n    return data",
                    "source_id": "api-code-history",
                    "source_type": "code",
                    "source_format": "python",
                }
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert {source["source_id"] for source in payload["sources"]} == {
        "api-doc-multi",
        "api-code-history",
    }
    assert any(hit["chunk"]["source_id"] == "api-code-history" for hit in payload["hits"])


def test_reproduce_endpoint_can_execute_with_injected_runner() -> None:
    def runner(backend: str, workspace) -> ExecutionResult:
        assert backend == "docker"
        assert (workspace / "algorithm.py").exists()
        return ExecutionResult(
            status="passed",
            command=["python", "-m", "unittest"],
            image="python:3.12-slim",
            exit_code=0,
            duration_seconds=0.1,
        )

    response = TestClient(create_app(execution_runner=runner)).post(
        "/reproduce",
        json={
            "source_text": "# 移动平均算法\n用于时间序列平滑。",
            "source_id": "api-doc-execution",
            "execute": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["execution"]["status"] == "passed"
    assert payload["reports"][-1]["target_type"] == "capability"
    assert payload["reports"][-1]["overall_status"] == "failed"


def test_reproduce_endpoint_can_repair_with_injected_runner() -> None:
    executions = iter(
        [
            ExecutionResult(
                status="failed",
                command=["python", "-m", "unittest"],
                image="python:3.12-slim",
                exit_code=1,
                duration_seconds=0.1,
                error="assertion failed",
            ),
            ExecutionResult(
                status="passed",
                command=["python", "-m", "unittest"],
                image="python:3.12-slim",
                exit_code=0,
                duration_seconds=0.1,
            ),
        ]
    )

    def runner(_backend: str, _workspace) -> ExecutionResult:
        return next(executions)

    response = TestClient(create_app(execution_runner=runner)).post(
        "/reproduce",
        json={
            "source_text": "# 移动平均算法\n用于时间序列平滑。",
            "source_id": "api-doc-repair",
            "execute": True,
            "repair": True,
            "max_repair_attempts": 1,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["execution"]["status"] == "passed"
    assert payload["repair_result"]["final_status"] == "passed"


def test_reproduce_endpoint_persists_pending_capability_without_promotion(
    tmp_path,
) -> None:
    registry_path = tmp_path / "capabilities.sqlite3"
    response = TestClient(
        create_app(settings=Settings(registry_path=registry_path))
    ).post(
        "/reproduce",
        json={
            "source_text": "# 移动平均算法\n用于时间序列平滑。",
            "source_id": "api-doc-persist",
            "persist": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["registry_record"]["version"] == 1
    assert payload["registry_record"]["status"] == "needs_review"
    latest = CapabilityRegistry(registry_path).latest(payload["capability"]["capability_id"])
    assert latest is not None
    assert latest.status == "needs_review"
