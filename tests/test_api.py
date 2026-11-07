import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from algo_weaver.api import create_app


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
