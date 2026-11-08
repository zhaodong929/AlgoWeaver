from algo_weaver.schemas.capability import AlgorithmCapability
from algo_weaver.schemas.failure import RepairFailureRecord
from algo_weaver.services.registry import CapabilityRegistry


def test_registry_persists_failure_experience_and_exports_jsonld(tmp_path):
    registry = CapabilityRegistry(tmp_path / "registry.sqlite3")
    registry.save(
        AlgorithmCapability(
            capability_id="cap-1",
            name="Inventory forecast",
            problem_definition="Forecast demand.",
            inputs=["sales"],
            outputs=["forecast"],
            algorithm_steps=["Use recent sales."],
        )
    )
    record = RepairFailureRecord(
        run_id="run-1",
        capability_id="cap-1",
        attempt=1,
        observation="generated test failed with missing column",
        patch_hash="abc123",
        outcome="repaired",
    )

    registry.record_failure(record)

    assert registry.list_failures("cap-1") == [record]
    graph = registry.export_jsonld()["@graph"]
    assert any(item.get("@type") == "algo:RepairFailure" for item in graph)
