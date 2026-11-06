from pathlib import Path

import pytest

from algo_weaver.schemas.capability import AlgorithmCapability, EvidenceRef
from algo_weaver.schemas.retrieval import EvidenceChunk, RetrievalHit
from algo_weaver.services.reproduction import ReproductionPlanner, TemplateArtifactWriter


def _capability() -> AlgorithmCapability:
    return AlgorithmCapability(
        name="Moving Average",
        problem_definition="Smooth a time series.",
        algorithm_family="time_series",
        inputs=["data", "window"],
        outputs=["averages"],
        algorithm_steps=["Read ordered values.", "Slide a fixed window.", "Average each window."],
        evidence=[
            EvidenceRef(
                source_id="doc-001",
                source_type="document",
                location="algorithm.md:L1-L8",
                excerpt="Moving average smooths a time series.",
            )
        ],
    )


def test_planner_links_retrieval_evidence_and_acceptance_checks() -> None:
    hit = RetrievalHit(
        rank=1,
        score=1.0,
        matched_terms=["moving"],
        chunk=EvidenceChunk(
            chunk_id="chunk-001",
            source_id="doc-001",
            source_type="document",
            source_format="markdown",
            path="algorithm.md",
            text="Moving average",
            line_start=1,
            line_end=2,
        ),
    )

    plan = ReproductionPlanner().build_plan(_capability(), [hit])

    assert plan.status == "ready"
    assert plan.evidence_chunk_ids == ["chunk-001"]
    assert "independent tests" in plan.acceptance_checks[-1]
    assert plan.steps[1].description == "Slide a fixed window."


def test_template_writer_creates_unverified_moving_average_artifacts(tmp_path: Path) -> None:
    plan = ReproductionPlanner().build_plan(_capability())
    bundle = TemplateArtifactWriter().generate(plan)
    paths = TemplateArtifactWriter().write(bundle, tmp_path)

    assert [path.name for path in paths] == ["algorithm.py", "test_algorithm.py"]
    assert "def moving_average" in (tmp_path / "algorithm.py").read_text(encoding="utf-8")
    assert all(artifact.verification_status == "unverified" for artifact in bundle.artifacts)


def test_blocked_plan_cannot_generate_code() -> None:
    capability = AlgorithmCapability(name="Incomplete")
    plan = ReproductionPlanner().build_plan(capability)

    assert plan.status == "blocked"
    with pytest.raises(ValueError, match="blocked reproduction plan"):
        TemplateArtifactWriter().generate(plan)
