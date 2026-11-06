import pytest
from pydantic import ValidationError

from algo_weaver.schemas.capability import AlgorithmCapability, EvidenceRef


def test_capability_card_has_stable_schema_fields() -> None:
    card = AlgorithmCapability(
        name="Moving Average",
        evidence=[
            EvidenceRef(
                source_id="doc-001",
                source_type="document",
                location="algorithm.md#overview",
                excerpt="Moving average smooths a time series.",
            )
        ],
    )
    assert card.name == "Moving Average"
    assert card.schema_version == "1.0"
    assert card.status == "draft"
    assert card.capability_id.startswith("cap_")


def test_capability_rejects_blank_name() -> None:
    with pytest.raises(ValidationError):
        AlgorithmCapability(name="   ")
