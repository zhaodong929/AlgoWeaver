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
