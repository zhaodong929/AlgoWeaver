from pathlib import Path

import pytest

from algo_weaver.schemas.capability import AlgorithmCapability, EvidenceRef
from algo_weaver.schemas.validation import ValidationCheck, ValidationReport
from algo_weaver.services.registry import CapabilityRegistry


def _capability() -> AlgorithmCapability:
    return AlgorithmCapability(
        capability_id="cap_registry",
        name="Moving Average",
        problem_definition="Smooth a time series.",
        inputs=["data"],
        outputs=["averages"],
        algorithm_steps=["Slide a window."],
        evidence=[EvidenceRef(source_id="doc-001", excerpt="moving average")],
    )


def test_registry_appends_versions_and_searches_latest(tmp_path: Path) -> None:
    registry = CapabilityRegistry(tmp_path / "capabilities.sqlite3")
    first = registry.save(_capability())
    second = registry.save(_capability().model_copy(update={"problem_definition": "Smooth noisy data."}))

    assert first.version == 1
    assert second.version == 2
    assert registry.latest("cap_registry").version == 2
    assert registry.search("Moving")[0].version == 2


def test_registry_requires_passing_report_for_verified_promotion(tmp_path: Path) -> None:
    registry = CapabilityRegistry(tmp_path / "capabilities.sqlite3")
    registry.save(_capability())
    partial = ValidationReport(
        target_type="capability",
        target_id="cap_registry",
        checks=[
            ValidationCheck(
                check_id="pending",
                name="pending",
                status="skipped",
                message="pending",
            )
        ],
        overall_status="partial",
    )
    with pytest.raises(ValueError, match="passing independent"):
        registry.promote_verified("cap_registry", partial)

    passing = partial.model_copy(
        update={
            "checks": [
                ValidationCheck(
                    check_id="passed",
                    name="passed",
                    status="passed",
                    message="independent checks passed",
                )
            ],
            "overall_status": "passed",
        }
    )
    promoted = registry.promote_verified("cap_registry", passing)
    assert promoted.status == "verified"
    assert promoted.version == 2
    assert registry.search_reusable("Moving")[0].status == "verified"


def test_registry_rejects_invalid_queries(tmp_path: Path) -> None:
    registry = CapabilityRegistry(tmp_path / "capabilities.sqlite3")
    with pytest.raises(ValueError, match="query cannot be empty"):
        registry.search(" ")


def test_registry_exports_jsonld_capability_and_evidence(tmp_path: Path) -> None:
    registry = CapabilityRegistry(tmp_path / "graph.sqlite3")
    registry.save(_capability())

    graph = registry.export_jsonld()

    assert graph["@context"]["algo"] == "https://algoweaver.dev/schema#"
    assert {node["@type"] for node in graph["@graph"]} == {
        "algo:CapabilityVersion",
        "algo:Evidence",
    }
